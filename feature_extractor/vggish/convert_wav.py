import os
import convert
import csv
from tensorflow import flags
FLAGS = flags.FLAGS


if __name__ == '__main__':
    flags.DEFINE_string(
      'input_videos_csv', None,
      'CSV file with lines "<video_file>,<labels>", where '
      '<video_file> must be a path of a video and <labels> '
      'must be an integer list joined with semi-colon ";"')

    for video_file, label in csv.reader(open(FLAGS.input_videos_csv)):
        _check = convert.convert_wav(video_file)