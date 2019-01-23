import numpy as np

def detector(data):
    '''Return boolean for signal presence'''
    present = np.mean(np.diff(data)>0) > .5

    return present