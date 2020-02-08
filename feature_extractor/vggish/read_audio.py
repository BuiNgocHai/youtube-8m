
import pandas as pd
import os
import librosa
import librosa.display
import numpy as np
from test import *

def extract_features(file_name):
   
    try:
        audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast') 
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=128)
        mfccsscaled = np.mean(mfccs.T,axis=0)
        
    except Exception as e:
        print("Error encountered while parsing file: ", file_name)
        return None 
     
    return mfccsscaled

data = extract_features('/home/vicker/Downloads/Sai-Lam-Cua-Anh-Dinh-Dung.mp3')
print(data)

# import tensorflow as tf
# tf.reset_default_graph()
# sess = tf.Session()

# vgg = CreateVGGishNetwork(0.01)

resdict = EmbeddingsFromVGGish(vgg, data, 44100)
print(resdict)
import ipdb; ipdb.set_trace()