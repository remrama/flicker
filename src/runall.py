"""
Open flicker GUI.

It's made using 3 distinct classes.
Threading is performed using PyQT QThreads.

<windowClass> is the main window.
<workerClass> is what collects data from Arduino,
    and operates on its own QThread. The data is 
    saved on the same thread, but passed to <windowClass> 
    for plotting and event logging using PyQT signals/slots.
<detectorClass> is used to check for flicks (LRLR),
    and is opened as an attribute on the workerClass.
"""
import sys
import yaml
import pyqtgraph as pg

from windowClass import myWindow
from workerClass import myWorker
from detectorClass import myDetector


if __name__ == '__main__':

    # load parameters from configuration file
    with open('config.yaml') as f:
        PARAMS = yaml.load(f,Loader=yaml.FullLoader)

    # initialize the PyQT app
    app = pg.QtGui.QApplication([])

    # create the main window
    window = myWindow(ymax=0.41209716796874996,
                      log_fname=PARAMS['log_fname'])

    # open thread where the <worker> will be placed
    thread = pg.QtCore.QThread()
    # create the <worker> QObject for data collection
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
                      PARAMS['detection_threshold_down'],
                      PARAMS['lrlr_timerange'],
                      PARAMS['n_flicks'])
    # connect data signals from <worker> to <window> (for plotting/logging)
    worker.signal4plot.connect(window.updatePlot)
    worker.signal4log.connect(window.updateLog)
    # connect GUI signals from <window> to <worker> (for adjusting parameters)
    window.signal_gain4worker.connect(worker.update_gain)
    window.signal_to_gensignal.connect(worker.generateSignal)
    # worker.signal4psdplot.connect(window.psdplotwin.updatePlot)

    # move the <worker> onto the separate <thread> (ie, QThread)
    worker.moveToThread(thread)
    # start the <worker> thread (now they are one)
    # and kick off with the function to grab data from Arduino
    thread.started.connect(worker.keepGrabbingData)
    thread.start()

    # run the app
    sys.exit(app.exec_())