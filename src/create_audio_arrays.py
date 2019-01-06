'''
One-time use.

Saves numpy arrays saying "left" or "right"
to be used for timestamping events.
'''

import numpy as np
import sounddevice as sd


fs = 44100    # sampling frequency
duration = 1  # seconds


def save_recording(word):

    print 'say {:s}'.format(word)

    myrecording = sd.rec(int(duration*fs),
                         samplerate=fs,
                         channels=2,
                         blocking=True)

    fname = './{:s}.npy'.format(word)
    np.save(fname,myrecording)


def playback_recording(word):
    fname = './{:s}.npy'.format(word)
    sound_array = np.load(fname)
    sd.play(sound_array,fs,blocking=True)



if __name__ == '__main__':
    
    for direction in ['left','right']:
        save_recording(word=direction)
        playback_recording(word=direction)
