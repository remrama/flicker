
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


data_num = 2

val_fname = '../../data/data{:02d}.csv'.format(data_num)
plt_fname = '../../data/data{:02d}.png'.format(data_num)


stamps, volts = np.loadtxt(val_fname,
                           skiprows=1,
                           delimiter=',',
                           dtype=[('stamps',float),
                                  ('volts',float)],
                           unpack=True)

list_of_datetimes = [ datetime.fromtimestamp(x) for x in stamps ]
dates = mdates.date2num(list_of_datetimes)

fig, ax = plt.subplots()
ax.plot_date(dates,volts,c='k',fmt='-')

myFmt = mdates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(myFmt)
ax.set_ylabel('Volts')

plt.savefig(plt_fname)
plt.show()
