
import sys
import yaml
import pyqtgraph as pg

from windowClass import myWindow
from workerClass import myWorker
from detectorClass import myDetector


if __name__ == '__main__':

    with open('config.yaml') as f:
        PARAMS = yaml.load(f,Loader=yaml.FullLoader)

    app = pg.QtGui.QApplication([])
    window = myWindow(ymax=0.41209716796874996,
                      log_fname=PARAMS['log_fname'])

    thread = pg.QtCore.QThread()

    # data is collected on a separate thread
    # and sent to GUI for plotting 
    worker = myWorker(PARAMS['serial_name'],
                      PARAMS['buffer_len'],
                      PARAMS['data_fname'],
                      PARAMS['columns'],
                      PARAMS['max_analog_volts'],
                      PARAMS['analog_read_resolution'],
                      PARAMS['internal_sampling_rate'],
                      PARAMS['moving_average_time'],
                      PARAMS['psd_calc_window_time'],
                      PARAMS['target_freq_index'],
                      PARAMS['detection_threshold_up'],
                      PARAMS['detection_threshold_down'])
    worker.signal4plot.connect(window.updatePlot)
    worker.signal4log.connect(window.updateLog)
    # worker.signal4psdplot.connect(window.psdplotwin.updatePlot)
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
