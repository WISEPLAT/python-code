# pip install numpy matplotlib
import os.path, time
import numpy as np
import matplotlib.style
import matplotlib as mpl

mpl.style.use('classic')
mpl.rcParams['axes.formatter.useoffset'] = False
import matplotlib.pyplot as plt

dataFile = 'YNDX_210801_210823.txt'

def my_split(s, seps):  # this function splits line to parts separated with given separators
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    i = 0
    while i < len(res):
        if res[i] == '':
            res.pop(i)
            continue
        i += 1
    return res


def loadFinamCsv(fname):
    if not os.path.isfile(fname):
        raise ValueError('wrong file name: %s' % fname)

    counter = 0

    fi = open(fname, 'r')

    tickerNameIsFound = False

    for line in fi:  # this loop counts number of bars and reads ticker name from the first bar
        firstSymbol = line[:1]
        if firstSymbol == '' or firstSymbol == '<':
            continue
        if not tickerNameIsFound:
            parsed = my_split(line, ',\n')
            ticker = parsed[0]
            period = parsed[1]
            tickerNameIsFound = True
        counter += 1

    bars = np.zeros((counter, 6), dtype=np.float64)  # create matrix for reading the whole file

    print(counter)

    fi.seek(0, 0)  # move file pointer to the beginning

    counter = 0

    for line in fi:
        firstSymbol = line[:1]
        if firstSymbol == '' or firstSymbol == '<':
            continue

        parsed = my_split(line, ';,\n')

        timeStamp = parsed[2] + parsed[3]
        dtime = time.strptime(timeStamp + '+0300', '%Y%m%d%H%M%S%z')
        timeEpoch = time.mktime(dtime)

        bars[counter, :] = np.array((timeEpoch, np.float64(parsed[4]), np.float64(parsed[5]),
                                     np.float64(parsed[6]), np.float64(parsed[7]), np.float64(parsed[8])))

        counter += 1
        if counter % 1000 == 0:
            print(int(counter / 1000), end=' ')

    fi.close()
    print('\n')

    return {'ticker': ticker, 'period': period, 'bars': bars}


def convertPeriodString(periodRaw):
    try:
        numMins = int(periodRaw)
        if numMins % 60 != 0:
            return 'M%d' % numMins
        else:
            return 'H%d' % (numMins // 60)
    except ValueError:
        return periodRaw


timeZoneDiffSecs = 3 * 3600  # we need to know in advance the time zone difference between UTC
pt = 0.01  # we need to know in advance the min price step (point)

data = loadFinamCsv(dataFile)
ticker = data['ticker']
period = data['period']
bars = data['bars']

periodFine = convertPeriodString(period)

xs = np.array(range(bars.shape[0]))

bodyCentres = 0.5 * (bars[:, 1] + bars[:, 4])
bodySpans = 0.5 * (bars[:, 4] - bars[:, 1])
totalCentres = 0.5 * (bars[:, 2] + bars[:, 3])
totalSpans = 0.5 * (bars[:, 2] - bars[:, 3])

blackBars = np.abs(bodySpans) < 0.25 * pt
greenBars = np.logical_and(np.logical_not(blackBars),
                           bodySpans >= 0.25 * pt)
redBars = np.logical_not(np.logical_or(blackBars, greenBars))

plt.clf()

plt.errorbar(xs[blackBars], totalCentres[blackBars], yerr=totalSpans[blackBars], ecolor='k', elinewidth=0.5, capsize=0,
             ls='none')
plt.errorbar(xs[blackBars], bodyCentres[blackBars], yerr=np.abs(bodySpans[blackBars]), ecolor='k', elinewidth=0.5,
             capsize=2, ls='none')

plt.errorbar(xs[greenBars], totalCentres[greenBars], yerr=totalSpans[greenBars], ecolor='g', elinewidth=0.5, capsize=0,
             ls='none')
plt.errorbar(xs[greenBars], bodyCentres[greenBars], yerr=np.abs(bodySpans[greenBars]), ecolor='g', elinewidth=0.5,
             capsize=2, ls='none')

plt.errorbar(xs[redBars], totalCentres[redBars], yerr=totalSpans[redBars], ecolor='r', elinewidth=0.5, capsize=0,
             ls='none')
plt.errorbar(xs[redBars], bodyCentres[redBars], yerr=np.abs(bodySpans[redBars]), ecolor='r', elinewidth=0.5, capsize=2,
             ls='none')

plt.xlabel('Bar No., %s' % periodFine)
plt.ylabel(ticker)  # before was: fname[ : fname.find( ' ' ) ]

plt.xlim(xs[0] - 0.5, xs[-1] + 0.5)

plt.annotate('start: %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(bars[0, 0] + timeZoneDiffSecs))),
             xy=(0.1, 0.95), xycoords='axes fraction',
             fontsize=11, horizontalalignment='left', verticalalignment='top')

plt.annotate('end: %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(bars[-1, 0] + timeZoneDiffSecs))),
             xy=(0.1, 0.90), xycoords='axes fraction',
             fontsize=11, horizontalalignment='left', verticalalignment='top')

plt.savefig(dataFile[: dataFile.rfind('.')] + '.png')

plt.show()
