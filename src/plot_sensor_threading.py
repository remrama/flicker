'''
For collecting sensor data.
GUI pops up, there are buttons for plotting and saving.
'''


from collections import deque
from itertools import islice

import sys
import time
import serial
import logging
import threading
import numpy as np

import pyqtgraph as pg
import sounddevice as sd


# initialize variables
SERIAL_NAME = '/dev/cu.usbmodem52417201'
LOG_FNAME = './data.log'
DATA_FNAME = './data.csv'
COLUMNS = ['stamp','data'] # of the output file
SOUND_FNAMES = dict(left='./sounds/left.npy',
                    right='./sounds/right.npy')

N_XPOINTS = 1000 # limits data in plot window
REFRACTORY_SECS = 4 # time to go idle after a detected signal

# for conversion of input to volts
MAX_ANALOG_VOLTS = 3.3
ANALOG_READ_RESOLUTION = 13 # unique to teensy
raw2volts = lambda x: MAX_ANALOG_VOLTS * x / float(2**ANALOG_READ_RESOLUTION)

# placeholders
time_last_flick = 0
saving = False
plotting = False


# set up logging
logging.basicConfig(filename=LOG_FNAME,
                    filemode='w',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# try to intialize connection with duino
try:
    ## TODO: add timeout and baudrate args
    duino = serial.Serial(SERIAL_NAME)
except serial.serialutil.SerialException:
    logging.warning('No serial connection, simulating data')
    duino = None

# load the audio files
sounds = { k: np.load(v) for k, v in SOUND_FNAMES.items() }



def start_new_outfile():
    '''initializes file with column names only'''
    with open(DATA_FNAME,'w') as newfile:
        newfile.write(','.join(COLUMNS))

def saverow(outlist):
    '''Appends existing file.
    outlist : 1 value for each column
    '''
    with open(DATA_FNAME,'a') as outfile:
        outfile.write('\n'+','.join([ str(x) for x in outlist ]))

def log_and_display(qtwin,msg):
    logging.info(msg)
    stamp = time.strftime('%m/%d-%H:%M:%S')
    qtwin.listw.addItem('{:s}, {:s}'.format(stamp,msg))
    # TODO: should this item be a QtGui.QListWidgetItem ??
    # app.processEvents() # necessary??


class DataGrabber(pg.QtCore.QThread):

    # signal gets sent to the plotter with each "emit" call
    signal = pg.QtCore.pyqtSignal(deque,deque,deque)

    def __init__(self):
        super(DataGrabber,self).__init__()
        # initialize empty lists for holding data/time buffers
        self.data = deque(maxlen=N_XPOINTS)
        self.stamps = deque(maxlen=N_XPOINTS)
        self.pollstamps = deque(maxlen=N_XPOINTS)
        ## TEMP just hvae pollstamps for testing
        ## to distinguish poll vs data incoming frequency

    def __del__(self):
        self.exiting = True
        self.wait()

    def grab_from_serial(self):
        '''
        This includes the emit() method, which automatically
        sends its args to wherever it is latter 'connected'.
        Grab data from the teensy by checking serial port.
        Doesn't return anything, just appends to existing lists.
        '''
        try:
            # receive from serial
            ser_str = duino.readline()
            # sometimes 2 vals get sent
            sep = ser_str.split('\r')
            vals = [ float(x) for x in sep if x.isalnum() ]
        except AttributeError: # since duino is None-type if no duino
            # simulate serial
            vals = [np.random.normal(500,100)] # as list to match receive_serial output
        stamp = time.time()
        ## TODO: currently this only includes the last
        ## _if_ multiple values come thu serial at once
        if len(vals) > 0:
            v = raw2volts(vals[-1])
            # update data buffer
            self.data.append(v)
            self.stamps.append(stamp)
            self.pollstamps.append(stamp)
            # save
            if saving:
                saverow(outlist=[stamp,v])
        else:
            log_and_display('Serial poll came back empty')
            self.pollstamps.append(stamp)

    def run(self):
        '''Automatically called once'''
        while True:
            self.grab_from_serial()
            # if plotting, send to the plotter (w builtin emit)
            self.signal.emit(self.stamps,self.data,self.pollstamps)
            time.sleep(.001)



def look4signal(data_buffer):
    '''Always runs on the whole data list, which is constanly appended.
    This is filler atm.
    '''
    N_VALS = 100 # take the last N values from data buffer
    global time_last_flick
    if (len(data_buffer) < N_VALS) or (
        time.time()-time_last_flick < REFRACTORY_SECS):
        # skip beginning of stream or soon after a found signal
        pass
    else:
        # grab a subset of data buffer
        data2search = list(islice(reversed(data_buffer),0,N_VALS)) # ugly slice bc of deque
        # check for signal
        flick_found = np.mean(np.diff(data2search)>0) > .5
        if flick_found:
            log_and_display(win,'Flick detected')
            # send to duino
            # win.myThread.msleep(100)
            duino.write(bytes(1))
            # time.sleep(1)
            time_last_flick = time.time()



class Window(pg.QtGui.QWidget):
    '''Main window display. Maybe overkill.
    '''
    def __init__(self):
        super(Window,self).__init__()
        self.initUI()

    def initUI(self):
        # create all widgets for the main window
        self.plotw = pg.PlotWidget()
        self.listw = pg.QtGui.QListWidget()
        self.svbutton = pg.QtGui.QPushButton('Save')
        self.svbutton.setCheckable(True)
        self.svbutton.clicked.connect(self.handleBtn)
        self.plbutton = pg.QtGui.QPushButton('Plot')
        self.plbutton.setCheckable(True)
        self.plbutton.clicked.connect(self.handleBtn)
        self.plbutton.click()
        self.recbutton = pg.QtGui.QPushButton('Play audio')
        self.recbutton.setCheckable(True)
        self.recbutton.clicked.connect(self.handleRcBtn)

        # manage the location/size of widgets
        grid = pg.QtGui.QGridLayout()
        grid.addWidget(self.svbutton,0,0)
        grid.addWidget(self.plbutton,1,0)
        grid.addWidget(self.recbutton,2,0)
        grid.addWidget(self.listw,3,0)
        grid.addWidget(self.plotw,0,1,4,1)
        self.setLayout(grid)

        # plot aesthetics
        # self.plotw.setXRange(0,N_XPOINTS)
        self.plotw.setYRange(0,raw2volts(1023))
        self.plotw.setLabel('left','Voltage',units='V')
        self.plotw.setLabel('bottom','Time passed',units='s')
        # self.plotw.getAxis('bottom').setTicks([])
        self.setWindowTitle('flicker')
        # self.setGeometry(300,300,300,300)
        
        # initiate line for drawing data
        self.curve = self.plotw.plot()
        # ## TODO: consider this for speed (from examples)
        # # Use automatic downsampling and clipping to reduce the drawing load
        # self.plotw.setDownsampling(mode='peak')
        # self.plotw.setClipToView(True)

        # # open timer, which is what repeatedly runs the custom
        # # function to check serial and plot incoming values
        # self.timer = pg.QtCore.QTimer() # create a timer
        # self.timer.timeout.connect(self.update_plot) # connect it to custom function
        # self.timer.start(0) # call custom function every x seconds

        # connect the data collection "threader" to the plotting function
        self.myThread = DataGrabber()
        self.myThread.start()
        self.myThread.signal.connect(self.update_plot)

        self.show()

    def handleBtn(self):
        '''Handles both plotting and saving buttons, since
        they do the same thing really.
        .sender() provides access to the button
        Switches appropriate bool and send msg to log&disp.
        '''
        global saving, plotting
        btn_txt = self.sender().text()
        act_txt = 'started' if self.sender().isChecked() else 'stopped'
        if btn_txt == 'Save':
            saving ^= 1
            if saving:
                start_new_outfile()
        else:
            plotting ^= 1
        msg = '{button} {action}'.format(button=btn_txt,action=act_txt)
        log_and_display(self,msg)

    def handleRcBtn(self):
        '''For recording. Plays audio (words left/right)
        and logs timestamps, for syncing with data files.
        Once pressed, should play a series of sounds 
        separated by a few seconds.
        '''
        BETWEEN_SOUNDS = 8 # seconds
        N_SOUNDS = 5 # randomize each sound
        if not self.sender().isChecked():
            ## TODO: any way to cancel/exit thread??
            pass
        else:
            def play_sequence():
                for i in range(N_SOUNDS):
                    snd = sounds['left']
                    sd.play(snd,samplerate=44100)
                    log_and_display(self,"Played 'left'")
                    time.sleep(BETWEEN_SOUNDS)
                log_and_display(self,'Stopped audio')
                if self.recbutton.isChecked():
                    self.recbutton.click()
            self.t = threading.Thread(target=play_sequence)
            self.t.start()
            log_and_display(self,'Started audio')


    def update_plot(self,xvals,yvals,pstamps):
        if plotting:
            self.curve.setData((np.array(xvals)-t0),yvals)
            # self.curve.setData(xvals,yvals)
        if len(xvals) > 1: # report frequency/ies
            self.plotw.setTitle('{:.02f} / {:.02f} Hz'.format(
                1./np.mean(np.diff(pstamps)),
                1./np.mean(np.diff(xvals))))
        # app.processEvents() # force complete redraw for every plot
        look4signal(self.myThread.data)



if __name__ == '__main__':
    app = pg.QtGui.QApplication([])
    logging.info('App started')
    t0 = time.time() # for x-axis
    win = Window()
    sys.exit(app.exec_())
