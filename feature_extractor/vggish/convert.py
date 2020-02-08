import subprocess
import os
def convert_wav(name):
    check = True
    src = name
    output = name[:-4]+'.wav'
    if os.path.isfile(output):
        os.remove(output)
    command = 'ffmpeg -i ' +src +' -ab 160k -ac 1 -ar 44100 -vn '+output

    subprocess.call(command, shell=True)
    return check
