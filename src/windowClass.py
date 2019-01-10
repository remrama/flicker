
from collections import deque

import numpy as np
import pyqtgraph as pg


class myWindow(pg.QtGui.QWidget):
    '''Main window display. Maybe overkill.
    '''
    def __init__(self,ymax):
        super(self.__class__,self).__init__()

        self.ymax = ymax
        self.initUI()


    def initUI(self):
        # create all widgets for the main window
        self.plotw = pg.PlotWidget()
        self.listw = pg.QtGui.QListWidget()
        self.savebox = pg.QtGui.QCheckBox('Save')
        self.plotbox = pg.QtGui.QCheckBox('Plot')
        self.plotbox.setChecked(True) # default to plot on
        self.recbutton = pg.QtGui.QPushButton('Play audio')
        self.recbutton.setCheckable(True)
        self.recbutton.clicked.connect(self.handleRcBtn)

        # manage the location/size of widgets
        grid = pg.QtGui.QGridLayout()
        grid.addWidget(self.savebox,0,0)
        grid.addWidget(self.plotbox,1,0)
        grid.addWidget(self.recbutton,2,0)
        grid.addWidget(self.listw,3,0)
        grid.addWidget(self.plotw,0,1,4,1)
        self.setLayout(grid)

        # aesthetics
        # self.plotw.setXRange(0,N_XPOINTS)
        self.plotw.setYRange(0,self.ymax)
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

        self.show()


    def handleBtn(self):
        '''Handles both plotting and saving buttons, since
        they do the same thing really.
        .sender() provides access to the button
        Switches appropriate bool and send msg to log&disp.
        '''
        global saving, plotting
        # btn_txt = self.sender().text()
        # act_txt = 'started' if self.sender().isChecked() else 'stopped'
        # if btn_txt == 'Save':
        #     saving ^= 1
        #     if saving:
        #         start_new_outfile()
        # else:
        #     plotting ^= 1
        # msg = '{button} {action}'.format(button=btn_txt,action=act_txt)
        # log_and_display(self,msg)

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


    @pg.QtCore.pyqtSlot(deque,deque,deque) # maybe not necessary
    def updatePlot(self,xvals,yvals,pstamps):
        if self.plotbox.isChecked():
            # self.curve.setData((np.array(xvals)-t0),yvals)
            self.curve.setData(xvals,yvals)
        # for i in range(100000):
        #     pass
        # self.curve.setData(xvals,yvals)
        if len(xvals) > 1: # report frequency/ies
            self.plotw.setTitle('{:.02f} / {:.02f} Hz'.format(
                1./np.mean(np.diff(pstamps)),
                1./np.mean(np.diff(xvals))))
        # app.processEvents() # force complete redraw for every plot
        # look4signal(self.myThread.data)

