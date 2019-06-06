
import sys
import numpy as np
import pyqtgraph as pg
from scipy.signal import welch

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets



class PSDPlotWidget(QtGui.QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        # QtWidgets.QWidget.__init__(self)

        # widget = QtWidgets.QWidget()
        grid = QtGui.QGridLayout()
        self.setLayout(grid)



        self.plot = pg.PlotWidget()
        self.curve = self.plot.plot()

        grid.addWidget(self.plot)
        # self.setWidget(widget)
        # self.setWidgetResizable(True)

        # main window stuff
        self.setGeometry(500,0,900,500)
        self.setWindowTitle('Power spectral density')    


    @pg.QtCore.pyqtSlot(list) # maybe not necessary
    def updatePlot(self,psdvals):
        '''
        Receives <signal4psdplot> from workerClass.
        Updates plot with new data.
        '''
        self.curve.setData(range(len(psdvals)),psdvals)


    def _softmax(self,x):
        """Compute softmax values for each sets of scores in x."""
        e_x = np.exp(x - np.max(x))
        return np.nan_to_num(e_x / np.nan_to_num(e_x.sum(axis=0)))

    def _rand_psd_generator(self):
        volts = np.random.uniform(.3,.1,size=100)
        INTERNAL_SAMPLING_RATE = 1000
        nperseg = 10
        volts *= 1e6
        _, psd = welch(volts,fs=INTERNAL_SAMPLING_RATE,window='boxcar',nperseg=nperseg)
        return self._softmax(psd)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = PSDPlotWidget()
    window.show()
    sys.exit(app.exec_())