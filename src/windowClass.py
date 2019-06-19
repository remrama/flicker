"""
See class docs.
"""
import logging
import numpy as np
import pyqtgraph as pg
from datetime import datetime
from collections import deque

from PSDPlotWidget import PSDPlotWidget


class TimeAxisItem(pg.AxisItem):
    """Subclass to get realtime timestamps on x-axis.
    https://gist.github.com/friendzis/4e98ebe2cf29c0c2c232
    """
    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)
        self.__ts2str = lambda ts: datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    def tickStrings(self,values,scale,spacing):
        return [ self.__ts2str(value) for value in values ]


class myWindow(pg.QtGui.QWidget):
    """
    Main GUI display.

    A QT QWidget that operates on a thread independent
    of <myWorker> (see runall.py).

    Some of the buttons/sliders pass signals (via QT
    signals/slots) to myWorker.
    """

    ## initialize signals that will be passed to <worker>
    # gain value to optimize LRLR detection, 
    # passed to <myDetector> via route through <myWorker>
    signal_gain4worker = pg.QtCore.pyqtSignal(int)
    # notification of button pressed to simulate single flick
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

        # initialize the user interface with custom setup method
        self.__initUI()


    def __initUI(self):
        """
        Initialize user interface.
        Sets up the QT layout and has all aesthetic information.
        """

        # create all widgets for the main window
        self.plotWidg = pg.PlotWidget(axisItems={'bottom':TimeAxisItem(orientation='bottom')})
        self.eventList = pg.QtGui.QListWidget()
        self.saveCheck = pg.QtGui.QCheckBox('Save')
        self.plotCheck = pg.QtGui.QCheckBox('Plot')
        self.plotCheck.setChecked(True) # default plot on
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
        grid.addWidget(self.saveCheck,0,0)
        grid.addWidget(self.plotCheck,1,0)
        grid.addWidget(self.psdplotbutton,2,0)
        grid.addWidget(self.gensigButton,3,0)
        grid.addWidget(self.gainSlider,4,0)
        grid.addWidget(self.eventList,5,0)
        grid.addWidget(self.plotWidg,0,1,6,1)
        self.setLayout(grid)

        # aesthetics
        # self.plotw.setXRange(0,N_XPOINTS)
        self.plotWidg.setYRange(0,self.ymax)
        self.plotWidg.setLabel('left','Voltage',units='V') # can move to plot init too
        # self.plotw.setLabel('bottom','Time')
        # self.plotw.getAxis('bottom').setTicks([])
        self.setWindowTitle('flicker')
        # self.setGeometry(300,300,300,300)
        
        # initiate line for drawing data
        self.curve = self.plotWidg.plot()
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
        if self.plotCheck.isChecked():
            # send to GUI display
            item = pg.QtGui.QListWidgetItem(msg)
            if warning: # change txt color
                item.setForeground(pg.QtCore.Qt.red)
            self.eventList.addItem(item)
            self.eventList.update()
            if xval:
                self.plotWidg.addLine(x=xval,pen='g',name='flick')


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
        if self.plotCheck.isChecked():
            # self.curve.setData((np.array(xvals)-t0),yvals)
            self.curve.setData(xvals,yvals)
        # check for lines drawn from flick detection,
        # and remove if outside visible range (to avoid stretching)
        # TODO: is this worth it?
        for p in self.plotWidg.items():
            if isinstance(p,pg.InfiniteLine) and p.x() < xvals[0]:
                self.plotWidg.removeItem(p)
        # report frequency/ies
        if len(xvals) > 1:
            self.plotWidg.setTitle('{:.02f} / {:.02f} Hz'.format(
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
