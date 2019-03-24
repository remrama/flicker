
import logging
import datetime
from collections import deque

import numpy as np
import pyqtgraph as pg


ts2str = lambda ts: datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
class TimeAxisItem(pg.AxisItem):
    '''subclass to get timestamps on x axis
    https://gist.github.com/friendzis/4e98ebe2cf29c0c2c232
    '''
    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)
    def tickStrings(self,values,scale,spacing):
        return [ ts2str(value) for value in values ]


class myWindow(pg.QtGui.QWidget):
    '''Main window display.'''
    def __init__(self,ymax,log_fname='./data.log'):
        super(self.__class__,self).__init__()

        # set up logging
        logging.basicConfig(filename=log_fname,
                            filemode='w',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        self.ymax = ymax
        self.initUI()


    def initUI(self):
        # create all widgets for the main window
        self.plotw = pg.PlotWidget(axisItems={'bottom':TimeAxisItem(orientation='bottom')})
        self.listw = pg.QtGui.QListWidget()
        self.savebox = pg.QtGui.QCheckBox('Save')
        self.plotbox = pg.QtGui.QCheckBox('Plot')
        self.detectbox = pg.QtGui.QCheckBox('Listen for flicks')
        self.plotbox.setChecked(True) # default plot on
        self.detectbox.setChecked(True) # default detection on
        self.recbutton = pg.QtGui.QPushButton('Play audio')
        self.recbutton.setCheckable(True)
        self.recbutton.clicked.connect(self.handleRcBtn)

        # manage the location/size of widgets
        grid = pg.QtGui.QGridLayout()
        grid.addWidget(self.savebox,0,0)
        grid.addWidget(self.plotbox,1,0)
        grid.addWidget(self.detectbox,2,0)
        grid.addWidget(self.recbutton,3,0)
        grid.addWidget(self.listw,4,0)
        grid.addWidget(self.plotw,0,1,5,1)
        self.setLayout(grid)

        # aesthetics
        # self.plotw.setXRange(0,N_XPOINTS)
        self.plotw.setYRange(0,self.ymax)
        self.plotw.setLabel('left','Voltage',units='V') # can move to plot init too
        # self.plotw.setLabel('bottom','Time')
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


    @pg.QtCore.pyqtSlot(str,bool,float) # maybe not necessary
    def updateLog(self,msg,warning,xval):
        '''
        Receives <signal4log> from workerClass.
        Exports msg to log file and prints it in GUI display
        Plots vertical line at xval if flick was detected.

        ARGS
        ----
        msg     : str, gets sent to log file and display
        warning : bool, indicating if logging should use warning
        xval    : float, timestamp of flick detected if detected (else 0)
        '''
        # send to log file
        if warning:
            logging.warning(msg)
        else:
            logging.info(msg)
        if self.plotbox.isChecked():
            # send to GUI display
            item = pg.QtGui.QListWidgetItem(msg)
            if warning: # change txt color
                item.setForeground(pg.QtCore.Qt.red)
            self.listw.addItem(item)
            if xval:
                self.plotw.addLine(x=xval,pen='g',name='flick')


    @pg.QtCore.pyqtSlot(deque,deque,deque) # maybe not necessary
    def updatePlot(self,xvals,yvals,pstamps):
        '''
        Receives <signal4plot> from workerClass.
        Updates plot with new data and sampling rate.

        ARGS
        ----
        xvals   : deque, most recent timestamps
        yvals   : deque, most recent sensor values
        pstamps : deque, most recent pollstamps, indicating freq of polling
        '''
        if self.plotbox.isChecked():
            # self.curve.setData((np.array(xvals)-t0),yvals)
            self.curve.setData(xvals,yvals)
        # check for lines drawn from flick detection,
        # and remove if outside visible range (to avoid stretching)
        # TODO: is this worth it?
        for p in self.plotw.items():
            if isinstance(p,pg.InfiniteLine) and p.x() < xvals[0]:
                self.plotw.removeItem(p)
        # report frequency/ies
        if len(xvals) > 1:
            self.plotw.setTitle('{:.02f} / {:.02f} Hz'.format(
                1./np.mean(np.diff(pstamps)),
                1./np.mean(np.diff(xvals))))
        # app.processEvents() # force complete redraw for every plot


    def closeEvent(self,event):
        '''Overrides default window shutdown
        behavior by asking for confirmation.
        '''
        quit_msg = 'Are you sure you want to exit?'
        reply = pg.QtGui.QMessageBox.question(self,'Message',quit_msg,
                    pg.QtGui.QMessageBox.Yes,pg.QtGui.QMessageBox.No)
        if reply == pg.QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
