'''
For collecting sensor data.
GUI pops up, there are buttons for plotting and saving.
'''


from itertools import islice

import sys
import time
import logging
import numpy as np

import pyqtgraph as pg
import sounddevice as sd


# initialize variables
LOG_FNAME = './data.log'
SOUND_FNAMES = dict(left='./sounds/left.npy',
                    right='./sounds/right.npy')



# placeholders
plotting = False


# set up logging
logging.basicConfig(filename=LOG_FNAME,
                    filemode='w',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# load the audio files
sounds = { k: np.load(v) for k, v in SOUND_FNAMES.items() }


def log_and_display(qtwin,msg):
    logging.info(msg)
    stamp = time.strftime('%m/%d-%H:%M:%S')
    qtwin.listw.addItem('{:s}, {:s}'.format(stamp,msg))
    # TODO: should this item be a QtGui.QListWidgetItem ??
    # app.processEvents() # necessary??




# class DataGrabber(pg.QtCore.QThread):
#     def __del__(self):
#         self.exiting = True
#         self.wait()


