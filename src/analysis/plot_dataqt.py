
import sys
import numpy as np
import pyqtgraph as pg


try:
    data_num = int(sys.argv[-1])
except ValueError:
    raise Warning('must enter data value atm')
val_fname = '../../data/data{:02d}.csv'.format(data_num)
plt_fname = '../../data/data{:02d}.png'.format(data_num)

stamps, volts = np.loadtxt(val_fname,
                           skiprows=1,
                           delimiter=',',
                           dtype=[('stamps',float),
                                  ('volts',float)],
                           unpack=True)


app = pg.QtGui.QApplication([])


plot = pg.plot(stamps,volts)


app.exec_()
