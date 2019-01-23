
import sys
import pyqtgraph as pg

from windowClass import myWindow
from workerClass import myWorker
from detectorClass import myDetector


if __name__ == '__main__':

    app = pg.QtGui.QApplication([])
    window = myWindow(ymax=0.41209716796874996)

    thread = pg.QtCore.QThread()

    # data is collected on a separate thread
    # and sent to the window for plotting 
    worker = myWorker()
    worker.signal4plot.connect(window.updatePlot)
    worker.signal4list.connect(window.updateList)
    worker.moveToThread(thread)
    thread.started.connect(worker.keepGrabbingData)

    # # # data is also sent from the worker thread
    # # # to the signal detector for finding saccades
    # detector = myDetector(worker.duino)
    # worker.detect_signal.connect(detector.check)

    thread.start()

    sys.exit(app.exec_())


    # objwork.finished.connect(objthread.quit)
    # objthread.started.connect()

    # # connect the data collection "threader" to the plotting function
    # self.myThread = DataGrabber()
    # self.myThread.start()
    # self.myThread.signal.connect(self.update_plot)



# if __name__ == '__main__':
#     app = pg.QtGui.QApplication([])
#     logging.info('App started')
#     t0 = time.time() # for x-axis
#     win = Window()
#     sys.exit(app.exec_())
