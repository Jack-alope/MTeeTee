import glob
import pandas as pd
from scipy.signal import savgol_filter
import peakutils
import numpy as np
import matplotlib.pyplot as plt
from analysis.calculations import PerformCalculations as pf
from analysis.output import OutputData as od


class GraphAnalyze():
    def __init__(self, expar):
        # Create list where I will store files
        files = []
        # Set path to where my files are
        filepath = '{0}'.format(expar['FOLDER'])
        # Grab all csv files in the folder
        files = sorted(glob.glob(filepath + '/T*.csv'))
        # Read in the heights, maybe change to giu but for now from csv
        if expar['BIO'] == 'multitissue':
            heights = sorted(glob.glob(filepath + '/H*.csv'))
            heightfile = [pd.read_csv(filename) for filename in heights]
        else:
            heightfile = 0

        # Put each file in a dataframe, this will be rewitten to allow for time frame
        olddf = [pd.read_csv(filename) for filename in files]
        # Create a new dataframe for the peaks, basepoints, etc
        analyzeddf = [pd.DataFrame() for filename in files]
        # Create dataframe that will hold data for analysis
        df = [pd.DataFrame() for filename in files]
        # For each file
        for i in range(len(files)):
            j = 0
            k = 0
            # Find the index value for the minimum time value
            while olddf[i]['time'][j] < expar['TIMEMIN']*1000:
                j += 1
            # Find the index value for the max time value, only if not 0
            if expar['TIMEMAX'] != 0:
                while olddf[i]['time'][k] < expar['TIMEMAX']*1000:
                    k += 1
            # If maxtimevalue is 0 set it to the last item in the dataframe
            else:
                k = len(olddf[i]['time'])
            # Copy over the values within the time frame over into new dataframe
            df[i] = olddf[i].iloc[j:k]
            # Reset the index for the new dataframe so it satrts at zero
            df[i] = df[i].reset_index(drop=True)

            # Add a list of index values, maybe repetative and could just use index but whatever.
            numbers = []
            for l in range(len(df[i]['time'])):
                numbers.append(l)
            df[i]['numbers'] = numbers

        # Call the populate dicts funmction to fill df, analyzeddf, and update expar
        (analyzeddf, df, expar) = self.populatepoints(
            analyzeddf, df, files, expar, heightfile)

        # Graph each tissue as well as calculate the forcecoefficient for each tissue
        for i in range(len(files)):
            self.graph(analyzeddf[i], df[i], i, expar[i]
                       ['TISSUE'], expar[i]['PACINGFREQ'])
            # POPULATE FORCE COEF IN expar
            pf.forcecoef(pf, expar, i)
        # Show the graphs
        plt.show()
        # Creates and populates the datadict with all the calculated values
        datadict = pf.populatedata(pf, analyzeddf, df, expar)
        od.writesummarycsv(od, datadict, expar)

    def populatepoints(self, analyzeddf, df, files, expar, heightfile):
        # For each file, NEEDS TO BE MOVED To OWN FUNCTION
        for i in range(len(files)):
            # Get tissue name
            expar[i] = {}
            expar[i]['TISSUE'] = files[i].split('/')[-1].split('@')[0]
            expar[i]['DAY'] = files[i].split('/')[-1].split('_')[-1].split('.')[0]
            expar[i]['PACINGFREQ'] = files[i].split(
                '/')[-1].split('@')[1].split('Hz')[0]
            expar[i]['CROSSSECT'] = df[i]['crosssect'][0]
            # Put height schtuff into expar dict
            if expar['BIO'] == 'multitissue':
                expar['POSTRADIUS'] = .277
                expar[i]['POSTHEIGHT1'] = heightfile[0]['POSTHEIGHT1'][i]
                expar[i]['TISSUEHEIGHT1'] = heightfile[0]['TISSUEHEIGHT1'][i]
                expar[i]['POSTHEIGHT2'] = heightfile[0]['POSTHEIGHT2'][i]
                expar[i]['TISSUEHEIGHT2'] = heightfile[0]['TISSUEHEIGHT2'][i]
            elif expar['BIO'] == 'eht':
                expar['POSTRADIUS'] = .5
                expar[i]['POSTHEIGHT1'] = 12
                expar[i]['TISSUEHEIGHT1'] = 11.5
                expar[i]['POSTHEIGHT2'] = 12
                expar[i]['TISSUEHEIGHT2'] = 11.5

            # Convert to seconds
            df[i]['time'] = df[i]['time'].divide(1000)
            # Prep the data
            df[i]['disp'] = self.prepdata(df[i]['disp'], expar)
            # Find the peaks
            temppeaks = peakutils.indexes(
                df[i]['disp'], thres=expar['PEAKSENS'], min_dist=expar['PEAKDIST'])
            # Find the basepoints
            (analyzeddf[i]['basepoints'],  analyzeddf[i]['peaks'], analyzeddf[i]['frontpoints']) = self.findbasepoints(
                df[i]['disp'], df[i]['time'], temppeaks, analyzeddf[i], df[i]['numbers'], expar)
            # Find the baseline
            df[i]['baseline'] = peakutils.baseline(df[i]['disp'], deg=4)

            # Find 10%,  50, and 90 points
            (analyzeddf[i]['10contractedx'], analyzeddf[i]['10contractedy']) = self.returnpoint(
                analyzeddf[i]['peaks'], analyzeddf[i]['basepoints'], df[i]['disp'], df[i]['time'], 10)
            (analyzeddf[i]['50contractedx'], analyzeddf[i]['50contractedy']) = self.returnpoint(
                analyzeddf[i]['peaks'], analyzeddf[i]['basepoints'], df[i]['disp'], df[i]['time'], 50)
            (analyzeddf[i]['90contractedx'], analyzeddf[i]['90contractedy']) = self.returnpoint(
                analyzeddf[i]['peaks'], analyzeddf[i]['basepoints'], df[i]['disp'], df[i]['time'], 90)
            (analyzeddf[i]['10relaxedx'], analyzeddf[i]['10relaxedy']) = self.returndownpoint(
                analyzeddf[i]['peaks'], analyzeddf[i]['frontpoints'], df[i]['disp'], df[i]['time'], 90)
            (analyzeddf[i]['50relaxedx'], analyzeddf[i]['50relaxedy']) = self.returndownpoint(
                analyzeddf[i]['peaks'], analyzeddf[i]['frontpoints'], df[i]['disp'], df[i]['time'], 50)
            (analyzeddf[i]['90relaxedx'], analyzeddf[i]['90relaxedy']) = self.returndownpoint(
                analyzeddf[i]['peaks'], analyzeddf[i]['frontpoints'], df[i]['disp'], df[i]['time'], 10)

            # Drop last peak
            analyzeddf[i] = analyzeddf[i][0:-1]

        return (analyzeddf, df, expar)

    def prepdata(self, dispdata, expar):
        # Smooth the data
        dispdata = savgol_filter(
            dispdata, expar['PEAKWIND'], expar['PEAKPOLY'])
        # Invert the data
        dispdata = dispdata * (-1)
        return dispdata

    def findbasepoints(self, dispdata, time, peaklist, analyzeddf, num, expar):
        basepoints = []
        frontpoints = []
        # find threshold
        measPerPeak = len(dispdata) / (2*len(peaklist))
        thres = int(measPerPeak * expar['THRESWIDTH'])

        # For each peak
        for peak in peaklist:

            # From the peak backwards towards the start
            for i in range(peak - thres, 1, -1):
                # Find the slope of the line
                slope = (dispdata[i] - dispdata[i-1]) / (num[i] - num[i-1])
                # if the slope is negative or zero you found the point
                if slope <= 0:
                    basepoints.append(i)
                    break
            for i in range(peak + thres, max(num), 1):
                # Find the slope of the line
                slope = (dispdata[i] - dispdata[i-1]) / (num[i] - num[i-1])
                # if the slope is negative or zero you found the point
                if slope >= 0:
                    frontpoints.append(i-1)
                    break

        # If there are more peaks than basepoints delete the first peak
        if len(basepoints) < len(peaklist) and len(frontpoints) < len(peaklist):
            peaklist = np.delete(peaklist, [0])
            frontpoints = np.delete(frontpoints, [0])
            peaklist = peaklist[:-1]
            basepoints = basepoints[:-1]
        elif len(basepoints) < len(peaklist):
            peaklist = np.delete(peaklist, [0])
            frontpoints = np.delete(frontpoints, [0])
        elif len(frontpoints) < len(peaklist):
            peaklist = peaklist[:-1]
            basepoints = basepoints[:-1]

        # Reurn a list of index values for where the basepoints are and updated peaks
        return (basepoints, peaklist, frontpoints)

    def returnpoint(self, peaklist, basepoints, dispdata, time, percentage):
        # Works good for contract 10, 50
        xpoints = []
        ypoints = []

        # From 0, num of basepoints - 1
        for i in range(len(basepoints)):
            # Find the difference in y between peak and basepoint
            ydiff = dispdata[peaklist[i]] - dispdata[basepoints[i]]
            # Find how much of the diff we want (ie 10, 50, 90%)
            diff = ydiff * (percentage/100)
            # Locate the y value we want to get as close to as possible
            yval = dispdata[basepoints[i]] + diff
            #xval = 0
            # From the basepoint to the peak
            for j in range(basepoints[i], peaklist[i], 1):
                # if we pass the point grab the point before and after
                if dispdata[j] > yval or j == peaklist[i] - 1:
                    # Find slope for linear approx
                    slope = (dispdata[j] - dispdata[j-1]) / \
                        (time[j] - time[j-1])
                    # Use linear approx to find x val
                    xval = ((yval - dispdata[j-1]) / slope) + time[j-1]
                    break
                elif dispdata[j] == yval:
                    xval = time[j]
                    break
                elif j == peaklist[i] - 1:
                    slope = (dispdata[j] - dispdata[j-1]) / \
                        (time[j] - time[j-1])
                    # Use linear approx to find x val
                    xval = ((yval - dispdata[j-1]) / slope) + time[j-1]
                    break

            xpoints.append(xval)
            ypoints.append(yval)

        return (xpoints, ypoints)

    def returndownpoint(self, peaklist, basepoints, dispdata, time, percentage):
        # Works good for contract 10, 50
        xpoints = []
        ypoints = []

        # From 0, num of basepoints - 1
        for i in range(len(basepoints) - 1):
            # Find the difference in y between peak and basepoint
            ydiff = dispdata[peaklist[i]] - dispdata[basepoints[i]]
            # Find how much of the diff we want (ie 10, 50, 90%)
            diff = ydiff * (percentage/100)
            # Locate the y value we want to get as close to as possible
            yval = dispdata[basepoints[i]] + diff

            # From the peak to the basepoint
            for j in range(peaklist[i], basepoints[i]):
                # if we pass the point grab the point before and after
                if dispdata[j] < yval:
                    # Find slope for linear approx
                    slope = (dispdata[j] - dispdata[j-1]) / \
                        (time[j] - time[j-1])
                    # Use linear approx to find x val
                    xval = ((yval - dispdata[j-1]) / slope) + time[j-1]
                    break
                elif j == basepoints[i] - 1:
                    slope = (dispdata[j - 1] - dispdata[j-2]
                             ) / (time[j-1] - time[j-2])
                    xval = ((yval - dispdata[j-2]) / slope) + time[j-2]
                    break
                elif dispdata[j] == yval:
                    xval = time[j]
                    break

            xpoints.append(xval)
            ypoints.append(yval)
        # Add row so it is same length. will cut back in init
        xpoints.append(0)
        ypoints.append(0)
        return (xpoints, ypoints)

    def graph(self, analyzeddf, df, i, name, freq):

        plt.figure(i)
        plt.title('Tissue {0} @ {1} Hz'.format(name, freq))
        plt.plot(df['time'], df['disp'],
                 df['time'], df['baseline'],
                 analyzeddf['10contractedx'], analyzeddf['10contractedy'], 'gs',
                 analyzeddf['50contractedx'], analyzeddf['50contractedy'], 'bs',
                 analyzeddf['90contractedx'], analyzeddf['90contractedy'], 'rs',
                 analyzeddf['10relaxedx'], analyzeddf['10relaxedy'], 'rs',
                 analyzeddf['50relaxedx'], analyzeddf['50relaxedy'], 'bs',
                 analyzeddf['90relaxedx'], analyzeddf['90relaxedy'], 'gs',
                 df['time'][analyzeddf['peaks']
                            ], df['disp'][analyzeddf['peaks']], 'g^',
                 df['time'][analyzeddf['basepoints']
                            ], df['disp'][analyzeddf['basepoints']], 'b^',
                 df['time'][analyzeddf['frontpoints']
                            ], df['disp'][analyzeddf['frontpoints']], 'r^'
                 )
