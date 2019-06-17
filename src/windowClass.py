
import logging
import datetime
from collections import deque

import numpy as np
import pyqtgraph as pg

from PSDPlotWidget import PSDPlotWidget


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


    signal_gain4worker = pg.QtCore.pyqtSignal(int)
    signal_to_gensignal = pg.QtCore.pyqtSignal(bool)

    def __init__(self,ymax,log_fname='./data.log'):
        super(self.__class__,self).__init__()

        # set up logging
        logging.basicConfig(filename=log_fname,
                            filemode='w',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        self.psdplotwin = PSDPlotWidget()

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
        self.psdplotbutton = pg.QtGui.QPushButton('PSD plot')
        # self.psdplotbutton.setCheckable(True)
        self.psdplotbutton.clicked.connect(self.handlePSDbutton)
        self.gensigButton = pg.QtGui.QPushButton('Generate signal')
        self.gensigButton.clicked.connect(self.handleGenSigButton)

        # gain slider
        self.gainSlider = pg.QtGui.QSlider(pg.QtCore.Qt.Horizontal)
        self.gainSlider.setRange(0,10000)
        self.gainSlider.setValue(0)
        # self.gainSlider.setTickPosition(pg.QtGui.QSlider.TicksBelow)
        self.gainSlider.setTickInterval(10)
        self.gainSlider.setSingleStep(10)
        self.gainSlider.valueChanged.connect(self.handle_gainSlider)
        # Label = QtWidgets.QLabel(qstr)


        # manage the location/size of widgets
        grid = pg.QtGui.QGridLayout()
        grid.addWidget(self.savebox,0,0)
        grid.addWidget(self.plotbox,1,0)
        grid.addWidget(self.detectbox,2,0)
        grid.addWidget(self.psdplotbutton,3,0)
        grid.addWidget(self.gensigButton,4,0)
        grid.addWidget(self.gainSlider,5,0)
        grid.addWidget(self.listw,6,0)
        grid.addWidget(self.plotw,0,1,7,1)
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

    def handlePSDbutton(self):
        self.psdplotwin.show()
        
    def handle_gainSlider(self):
        new_gain = self.gainSlider.value()
        self.signal_gain4worker.emit(new_gain)

    def handleGenSigButton(self):
        self.signal_to_gensignal.emit(True)


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
