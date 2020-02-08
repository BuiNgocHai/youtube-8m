import os
import numpy as np 
from time import sleep
from threading import Thread
import threading
import shutil
import pymysql
import sys
import wget
import csv
import time
import cv2
import feature_extractor
import tensorflow as tf
from tensorflow import app
from tensorflow import flags
import subprocess

sys.path.append('/storage/haibn/yt8m/code/video_classification/feature_extractor/vggish/')
from vggish import convert,vggish_inference


CAP_PROP_POS_MSEC = 0
FLAGS = flags.FLAGS

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

path = '/storage1/haibn/data_yt8m_vid/'
def dowload_video(url, post_id, id_video, label):
    os.makedirs(path + 'crawl/' + post_id + '/',exist_ok=True)
    name = id_video
    try:
        name_csv = post_id + '.csv'
        name_video = name + '.mp4'
        url = 'http://172.26.46.99'+url[19:]
        print('Dowload video: ' + url)

        wget.download(url, path +'crawl/' + post_id + '/' + name_video)
        #save in csv
        with open(path + 'crawl/' + post_id + '/' + name_csv, mode = 'a') as output_file:
            check = True
            for file_name in os.listdir(path + 'crawl/' + post_id):
                if (file_name[-4:] != '.mp4' and file_name[-4:] != '.csv'):
                    check = False 
            writer = csv.writer(output_file, delimiter =',', quotechar ='"', quoting = csv.QUOTE_MINIMAL)
            writer.writerow([path + 'crawl/' + post_id + '/'+name_video, label])
    except:
        print('Dowload fail ' + url)
        e = sys.exc_info()
        print(e)


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
  features = np.clip(features, min_quantized_value, max_quantized_value)
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
        update_cmd = 'UPDATE adnetwork_task.youtube_crawler \
          SET status_process = 1\
            WHERE VideoID = "' +video_file[38:-4] +'"'
        cursor.execute(update_cmd)
        db.commit()
        os.remove(video_file)
        os.remove(video_file[:-4]+'.wav')
  
  print('Successfully encoded %i out of %i videos' %
        (total_written, total_written + total_error))

def call_ex(input_videos_csv, output_tfrecords_file, video_of_thread):
  all_video = []
  total_video = {}
  count = 0 
  writer = tf.python_io.TFRecordWriter(output_tfrecords_file)
  data = csv.reader(open(input_videos_csv))
  total_video_csv = sum(1 for row in data) 
  video_thread = int(total_video_csv/video_of_thread)
  
  for video_file, label in csv.reader(open(input_videos_csv)):
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
    

db = pymysql.connect("123.30.58.145",'big_data',password = '1')
cursor = db.cursor()
if __name__ == '__main__':
    #read data from data base
    print("Read data from db")
    sql = "select VideoID,Label,S3Link from adnetwork_task.youtube_crawler"
    
    cursor.execute(sql)
    results = cursor.fetchall()
    index = 1 
    count = 0 
    all_data = []
    for i in results:
        count += 1
        
        if count%1000 == 0: 
            all_data.append(results[count - 1000 :count])
    #print(all_data)
    
    for val in all_data:
        for item in val:
            name = item[0]
            label = item[1]
            link = item[2]
        
            thread = threading.Thread(target=dowload_video, args=(link, str(index), name, label ))
            thread.start()
            print('Thread done : ')
        path_csv = path +'crawl/' + str(index) + '/' + str(index)+'.csv'
        path_tfrecord = path +'train/' + str(index)+'.tfrecord'
        index+=1
        count = 0
        thread.join()
        # command_extract = 'python3 /storage/haibn/yt8m/code/video_classification/feature_extractor/extract_tfrecords_main.py --input_videos_csv=' + path_csv + ' --output_tfrecords_file=' + path_tfrecord + ' --extract_wav=True --video_of_thread=1000'
        # subprocess.call(command_extract, shell=True)
        call_ex(path_csv, path_tfrecord, 1000)
        

        #shutil.rmtree(path+'crawl/' + str(index -1 ) + '/')
    #create writer file 
    #writer = tf.python_io.TFRecordWriter(FLAGS.output_tfrecords_file)