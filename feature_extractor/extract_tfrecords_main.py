# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Produces tfrecord files similar to the YouTube-8M dataset.

It processes a CSV file containing lines like "<video_file>,<labels>", where
<video_file> must be a path of a video, and <labels> must be an integer list
joined with semi-colon ";". It processes all videos and outputs tfrecord file
onto --output_tfrecords_file.

It assumes that you have OpenCV installed and properly linked with ffmpeg (i.e.
function `cv2.VideoCapture().open('/path/to/some/video')` should return True).

The binary only processes the video stream (images) and not the audio stream.
"""

import csv
import os
import sys

import cv2
import feature_extractor
import numpy
import tensorflow as tf
from tensorflow import app
from tensorflow import flags
sys.path.append('/storage/haibn/yt8m/code/video_classification/feature_extractor/vggish/')
from threading import Thread
import threading
import time
from vggish import convert,vggish_inference
FLAGS = flags.FLAGS

# In OpenCV3.X, this is available as cv2.CAP_PROP_POS_MSEC
# In OpenCV2.X, this is available as cv2.cv.CV_CAP_PROP_POS_MSEC
CAP_PROP_POS_MSEC = 0

if __name__ == '__main__':
  # Required flags for input and output.
  flags.DEFINE_string(
      'output_tfrecords_file', None,
      'File containing tfrecords will be written at this path.')
  flags.DEFINE_string(
      'input_videos_csv', None,
      'CSV file with lines "<video_file>,<labels>", where '
      '<video_file> must be a path of a video and <labels> '
      'must be an integer list joined with semi-colon ";"')
  # Optional flags.
  flags.DEFINE_string('model_dir', os.path.join(os.getenv('HOME'), 'yt8m'),
                      'Directory to store model files. It defaults to ~/yt8m')

  # The following flags are set to match the YouTube-8M dataset format.
  flags.DEFINE_integer('frames_per_second', 1,
                       'This many frames per second will be processed')
  flags.DEFINE_boolean(
      'skip_frame_level_features', False,
      'If set, frame-level features will not be written: only '
      'video-level features will be written with feature '
      'names mean_*')
  flags.DEFINE_string(
      'labels_feature_key', 'labels',
      'Labels will be written to context feature with this '
      'key, as int64 list feature.')
  flags.DEFINE_string(
      'image_feature_key', 'rgb',
      'Image features will be written to sequence feature with '
      'this key, as bytes list feature, with only one entry, '
      'containing quantized feature string.')
  flags.DEFINE_string(
      'video_file_feature_key', 'id',
      'Input <video_file> will be written to context feature '
      'with this key, as bytes list feature, with only one '
      'entry, containing the file path of the video. This '
      'can be used for debugging but not for training or eval.')
  flags.DEFINE_boolean(
      'insert_zero_audio_features', True,
      'If set, inserts features with name "audio" to be 128-D '
      'zero vectors. This allows you to use YouTube-8M '
      'pre-trained model.')
  flags.DEFINE_integer(
    'video_of_thread',1,
    'Number of video on one thread'
  )
  flags.DEFINE_boolean(
  'extract_wav',True,
  'Status accept extrac_wav'
)

def frame_iterator(filename, every_ms=1000, max_num_frames=300):
  """Uses OpenCV to iterate over all frames of filename at a given frequency.

  Args:
    filename: Path to video file (e.g. mp4)
    every_ms: The duration (in milliseconds) to skip between frames.
    max_num_frames: Maximum number of frames to process, taken from the
      beginning of the video.

  Yields:
    RGB frame with shape (image height, image width, channels)
  """
  video_capture = cv2.VideoCapture()
  if not video_capture.open(filename):
    print ( sys.stderr, 'Error: Cannot open video file ' + filename)
    return
  last_ts = -99999  # The timestamp of last retrieved frame.
  num_retrieved = 0

  while num_retrieved < max_num_frames:
    # Skip frames
    while video_capture.get(CAP_PROP_POS_MSEC) < every_ms + last_ts:
      if not video_capture.read()[0]:
        return

    last_ts = video_capture.get(CAP_PROP_POS_MSEC)
    has_frames, frame = video_capture.read()
    if not has_frames:
      break
    yield frame
    num_retrieved += 1


def _int64_list_feature(int64_list):
  return tf.train.Feature(int64_list=tf.train.Int64List(value=int64_list))


def _bytes_feature(value):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def _make_bytes(int_array):
  if bytes == str:  # Python2
    return ''.join(map(chr, int_array))
  else:
    return bytes(int_array)


def quantize(features, min_quantized_value=-2.0, max_quantized_value=2.0):
  """Quantizes float32 `features` into string."""
  assert features.dtype == 'float32'
  assert len(features.shape) == 1  # 1-D array
  features = numpy.clip(features, min_quantized_value, max_quantized_value)
  quantize_range = max_quantized_value - min_quantized_value
  features = (features - min_quantized_value) * (255.0 / quantize_range)
  features = [int(round(f)) for f in features]

  return _make_bytes(features)

def write_csv(all_video, writer):
  extractor = feature_extractor.YouTube8MFeatureExtractor(FLAGS.model_dir)
  total_written = 0
  total_error = 0
  for video_file, labels in all_video.items():
    rgb_features = []
    sum_rgb_features = None
    if os.path.isfile(video_file[:-4]+'.wav'):
      print('have wav file')
    elif FLAGS.extract_wav == True:
      _check = convert.convert_wav(video_file)

    if FLAGS.extract_wav == False:
      audio_feature = [0] * 128
      count = 0
      for rgb in frame_iterator(
          video_file, every_ms=1000.0 / FLAGS.frames_per_second):
        features = extractor.extract_rgb_frame_features(rgb[:, :, ::-1])
        if sum_rgb_features is None:
          sum_rgb_features = features
        else:
          sum_rgb_features += features
        rgb_features.append(_bytes_feature(quantize(features)))

      if not rgb_features:
        print ( sys.stderr, 'Could not get features for ' + video_file)
        total_error += 1
        continue

      mean_rgb_features = sum_rgb_features / len(rgb_features)

      # Create SequenceExample proto and write to output.
      feature_list = {
          FLAGS.image_feature_key: tf.train.FeatureList(feature=rgb_features),
      }
      context_features = {
          FLAGS.labels_feature_key:
              _int64_list_feature(sorted(map(int, labels.split(';')))),
          FLAGS.video_file_feature_key:
              _bytes_feature(_make_bytes(map(ord, video_file))),
          'mean_' + FLAGS.image_feature_key:
              tf.train.Feature(
                  float_list=tf.train.FloatList(value=mean_rgb_features)),
      }

      
      zero_vec = audio_feature[count]
      feature_list['audio'] = tf.train.FeatureList(
          feature=[_bytes_feature(_make_bytes(zero_vec))] * len(rgb_features))
      context_features['mean_audio'] = tf.train.Feature(
          float_list=tf.train.FloatList(value=zero_vec))
      count +=1

      if FLAGS.skip_frame_level_features:
        example = tf.train.SequenceExample(
            context=tf.train.Features(feature=context_features))
      else:
        example = tf.train.SequenceExample(
            context=tf.train.Features(feature=context_features),
            feature_lists=tf.train.FeatureLists(feature_list=feature_list))
      writer.write(example.SerializeToString())
      total_written += 1
    else:
      if os.path.isfile(video_file[:-4]+'.wav'):
        audio_feature = vggish_inference.extract(video_file[:-4]+'.wav')
        count = 0
        for rgb in frame_iterator(
            video_file, every_ms=1000.0 / FLAGS.frames_per_second):
          features = extractor.extract_rgb_frame_features(rgb[:, :, ::-1])
          if sum_rgb_features is None:
            sum_rgb_features = features
          else:
            sum_rgb_features += features
          rgb_features.append(_bytes_feature(quantize(features)))

        if not rgb_features:
          print ( sys.stderr, 'Could not get features for ' + video_file)
          total_error += 1
          continue

        mean_rgb_features = sum_rgb_features / len(rgb_features)

        # Create SequenceExample proto and write to output.
        feature_list = {
            FLAGS.image_feature_key: tf.train.FeatureList(feature=rgb_features),
        }
        context_features = {
            FLAGS.labels_feature_key:
                _int64_list_feature(sorted(map(int, labels.split(';')))),
            FLAGS.video_file_feature_key:
                _bytes_feature(_make_bytes(map(ord, video_file))),
            'mean_' + FLAGS.image_feature_key:
                tf.train.Feature(
                    float_list=tf.train.FloatList(value=mean_rgb_features)),
        }

        
        zero_vec = audio_feature[count]
        feature_list['audio'] = tf.train.FeatureList(
            feature=[_bytes_feature(_make_bytes(zero_vec))] * len(rgb_features))
        context_features['mean_audio'] = tf.train.Feature(
            float_list=tf.train.FloatList(value=zero_vec))
        count +=1

        if FLAGS.skip_frame_level_features:
          example = tf.train.SequenceExample(
              context=tf.train.Features(feature=context_features))
        else:
          example = tf.train.SequenceExample(
              context=tf.train.Features(feature=context_features),
              feature_lists=tf.train.FeatureLists(feature_list=feature_list))
        writer.write(example.SerializeToString())
        total_written += 1

  
  print('Successfully encoded %i out of %i videos' %
        (total_written, total_written + total_error))

def main(unused_argv):
  all_video = []
  total_video = {}
  count = 0 
  writer = tf.python_io.TFRecordWriter(FLAGS.output_tfrecords_file)
  data = csv.reader(open(FLAGS.input_videos_csv))
  total_video_csv = sum(1 for row in data) 
  video_thread = int(total_video_csv/FLAGS.video_of_thread)
  
  for video_file, label in csv.reader(open(FLAGS.input_videos_csv)):
    total_video[video_file] = label
    count +=1
    if count == video_thread:
        all_video.append(total_video)
        total_video = {}
        count = 0
  
  if count != 0:
    all_video.append(total_video)

  
  for index in range(len(all_video)):
    thread = threading.Thread(target=write_csv, args=(all_video[index], writer ,))
    print(len(all_video[index]))
    thread.start()
    print('Thread done : ', index)

if __name__ == '__main__':
  app.run(main)
