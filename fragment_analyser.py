#!/usr/bin/python
import sys
import numpy as np
import pandas as pd


# Used to avoid issue with missing DISPLAY on the cluster.
import matplotlib
matplotlib.use('Agg')
import pylab


def nonemedian(data):
    # same as numpy but handles None instead of nan
    data = [x for x in data if x is not None]
    return np.median(data)



# a data structure to handle the Well with a given sample 
class Well(object):
    """Class dedicated to a well



    """
    def __init__(self, name, wellID, data, sigma=50):
        """.. rubric:: Constructor

        """
        self.df = data
        self.name = name
        self.wellID = wellID
        self.tic = None
        self.tim = None
        self.total_concentration = None
        self.guess = None
        self.lower_bp_filter = 120
        self.sigma = sigma

    def get_peak_and_index(self):
        df = self.df.copy()
        mask = df['Size (bp)'].astype(float) > self.lower_bp_filter
        df = df[mask]

        if len(df) == 0:
            return None

        positions = df['Size (bp)'].astype(float)

        data = df['RFU'].copy()

        # this need to be cast into float
        data = data.astype(float)

        naive_max = data.max()
        index = data.argmax()

        if self.guess is None:
            pass
        else:
            weighted_data = pylab.exp(-0.5*( (self.guess-positions.values) /
                self.sigma)**2)
            data = data * weighted_data
            # check it is unique 
            subdata = data
            #if len(subdata) == 1:
            #    found_max = subdata.values[0]
            #    index = subdata.index[0]
            #else:
            #    found_max = naive_max
            index = data.argmax()

        peak_pos = float(df['Size (bp)'].ix[index])

        return peak_pos, index

    def get_peak(self):
        try:
            # get_peak_and_index may return None
            maximum, index = self.get_peak_and_index()
            return maximum
        except:
            return None

    def get_ng_per_ul(self):
        try:
            maximum, index = self.get_peak_and_index()
            return float(self.df.ix[index]['ng/ul'])
        except:
            return None

    def get_mw(self, constant=650):
        try:
            return self.get_peak() * constant / 1000.
        except:
            return None

    def plot(self):
        x = self.df['Size (bp)'].astype(float).values
        y = self.df['RFU'].astype(float).values
        pylab.plot(x, y, 'o')



class Line(object):
    """Class dedicated to a Line

    A line has 12 :class:`Well`.

    """
    def __init__(self):
        self.wells = []
        self.number = None
        self.number_wells = 12

    def append(self, well):
        self.wells.append(well)

    def guess_peak(self):
        peaks = self.get_peaks()
        guess = nonemedian(peaks)
        return guess

    def set_guess(self, guess=None):
        if guess is None:
            guess = self.guess_peak()
        for well in self.wells:
            well.guess = guess

    def get_peaks(self):
        peaks = [well.get_peak() for well in self.wells]
        return peaks

    def get_well_names(self):
        return [well.wellID for well in self.wells]

    def get_ng_per_ul(self):
        return [well.get_ng_per_ul() for well in self.wells]

    def diagnostic(self):
        """Shows detected peaks for each well and confidence at 1,2,3
        MAD value


        """
        peaks = [well.get_peak() for well in self.wells]
        names = [well.name for well in self.wells]

        pylab.clf()
        pylab.plot(peaks, 'o-', mfc='red')
        pylab.axhline(self.guess_peak(), linestyle='--', lw=2, color='k')
        pylab.grid(True)
        pylab.xlabel('names')
        pylab.ylabel('Size bp')
        pylab.xticks(range(0, self.number_wells-1), names)
        pylab.ylim([0, pylab.ylim()[1]*1.2])
        pylab.xlim([-0.5, 10.5])

        peaks = pylab.array(self.get_peaks())
        sigma = pylab.std([x for x in peaks if x is not None])
        X = [i for i,x in enumerate(peaks) if x is not None]
        peaks = np.array([x for x in peaks if x is not None])

        # sigma is biased the presence of outliers, so we better off using the MAD
        sigma = self.get_mad()


        pylab.fill_between(X, peaks-sigma*3, peaks+sigma*3, color='red', alpha=0.5)
        pylab.fill_between(X, peaks-sigma*2, peaks+sigma*2, color='orange', alpha=0.5)
        pylab.fill_between(X, peaks-sigma, peaks+sigma, color='green', alpha=0.5)

    def get_mad(self, minimum=25):
        # The crux of the problem is that the standard deviation is based on squared distances, 
        # so extreme points are much more influential than those close to the mean.
        # A good candidate is the median absolute deviation from median, commonly shortened to 
        # the median absolute deviation (MAD). It is the median of the set comprising the absolute 
        #values of the differences between the median and each data point
        peaks = pylab.array(self.get_peaks())

        # we may have None in the list of peaks
        peaks = [x for x in peaks if x is not None]

        sigma = nonemedian(abs(peaks-nonemedian(peaks)))

        if sigma < minimum:
            sigma = minimum
        return sigma


class Plate(object):
    """Dedicated class for plates

    A plate contains (at most) 8 :class:`lines` with 12 :class:`well` each.

    This is a Abstract base class and 2 children classes are derived from it to 
    read different types of input data:

        - :class:`PlatePF1`
        - :class:`PlatePFGE`

    """
    def __init__(self, filenames, guess=None, lower_bp=1, upper_bp=1e6,
        sigma=50, output_filename="results.csv"):

        self.filenames = filenames
        self.guess = guess
        self.number_wells = 12
        self.sigma = sigma
        self.output_filename = output_filename
        self.lower_bp = lower_bp
        self.upper_bp = upper_bp
    
    def get_lines(self):
        print("Reading the %s files:" % len(self.filenames))
        self.lines = []
        for filename in self.filenames:
            print(" - " + filename),
            try:
                ptr = PeakTableReader(filename, sigma=self.sigma)
                line = ptr.get_line()
                # THIS LINE IS IMPORTANANT TO WEIGHT DOWN OUTLIERS
                line.set_guess(self.guess)
                self.lines.append(line)
                print('...done')
            except Exception as err:
                print(err)
                print('WARNING. This file could not be interpreted')

    def get_data(self):
        raise NotImplementedError

    def to_csv(self):
        raise NotImplementedError


class PlatePF1(Plate):
    """12 wells times 8 lines

    Input data must look like:todo
    """
    def __init__(self, filenames, guess=None,
            sigma=50,  output_filename='results.csv'):
        lower_bp = 10
        upper_bp=1e6
        super(PlatePF1, self).__init__(filenames, guess, lower_bp, 
            upper_bp, sigma, output_filename)

        self.get_lines()

    def get_data(self):

        data = []
        for line in self.lines:
            for well in line.wells:
                res = well.get_peak_and_index()
                if res:
                    peak, index = res
                    data.append(well.df.ix[index])
        df = pd.DataFrame(data)
        df.reset_index(inplace=True, drop=True)
        df.drop('Peak ID', axis=1, inplace=True)
        return df

    def to_csv(self, filename="results.csv"):
        df = self.get_data()
        if filename is None:
            df.to_csv(self.output_filename, index=False)
        else:
            df.to_csv(filename, index=False)


class PlatePFGE(Plate):
    """12 wells times 8 lines
    
    Input data must look like:todo
    """
    def __init__(self, filenames, guess=None, lower_bp=150, upper_bp=5999,
            sigma=50,  output_filename='results.csv'):
        super(PlatePFGE, self).__init__(filenames, guess, lower_bp, 
            upper_bp, sigma, output_filename)

        #Molecular Weight of  dsDNA  (daltons/base Pair) (constant)
        self.mw_dna = 650 

        self.get_lines()

    def get_data(self):
        data = {'names':[],'conc':[], 'size':[] , 'amount':[]}
        for line in self.lines:
            peaks = pylab.array(line.get_peaks())
            concs = pylab.array(line.get_ng_per_ul())
            names = line.get_well_names()

            # peak and conc may be none
            #amount = conc * 1000. / (peaks*self.mw_dna/1000.)
            sigma = line.get_mad()

            for i, peak in enumerate(peaks):
                data['names'].append(names[i])

                if peak is None:
                    data['conc'].append(None)
                    data['size'].append(None)
                    data['amount'].append(None)
                elif peak + 3 * sigma < nonemedian(peaks):
                    data['conc'].append(None)
                    data['size'].append(None)
                    data['amount'].append(None)
                elif peak - 3 * sigma > nonemedian(peaks):
                    data['conc'].append(None)
                    data['size'].append(None)
                    data['amount'].append(None)
                else:
                    conc = concs[i]
                    amount = conc * 1000. / (peak*self.mw_dna/1000.)
                    data['conc'].append(conc)
                    data['size'].append(peak)
                    data['amount'].append(amount)

            # add the control
            data['names'].append('Ladder')
            data['conc'].append(None)
            data['size'].append(None)
            data['amount'].append(None)
        return data

    def to_csv(self, filename=None):
        data = self.get_data()
        df = pd.DataFrame(data)
        df = df[['names', 'conc', 'size', 'amount']]
        df.columns = ['names', 'ng/uL (QUBIT/FA)', 'Size (bp)', 'nM']
        df.index = [x+1 for x in df.index]
        if filename is None:
            df.to_csv(self.output_filename, index=False)
        else:
            df.to_csv(filename, index=False)


class PeakTableReader(object):
    """Read a fragment analyser data set

    """
    def __init__(self, filename="2015_07_20_20H_52M_Peak_Table.csv", sigma=50):
        """.. rubric:: Constructor

        :param filename:
        :param sigma:

        """
        self.filename = filename
        self.sigma = sigma

        # guess the mode (CSV input files are in mode alternate or mode standard)
        self._guess_mode()

        # two types of input data (standard or alternate) require specific
        # interpretation:
        self.interpret()

    def _guess_mode(self):
        df = pd.read_csv(self.filename, sep=",")
        if 'Well' in df.columns:
            self.mode = "standard"
        else:
            self.mode = "alternate"

    def _identify_names(self):
        # Each of the 8 plates is labelled by a letter from A to H
        names = [x for x in self.df[0].dropna().unique() if x.strip() and x[0] in 'ABCDEFGH']
        assert len(names) == 12
        # make sure there is no spaces
        self.names = [name.strip() for name in names]

    def _identify_start(self):
        # let us keep track of the starting position of each name
        positions = [self.df.index[(self.df[0] == name)][0] for name in self.names]
        self.start_positions = positions

    def _identify_end(self):
        # READ one file corresponding to one Line that is 12 wells
        ends = []
        for name, position in zip(self.names, self.start_positions):
            # not optimal but let us make it simple and scan the dataframe
            # for each name to retrieve only the data corresponding to the
            # name. Using the position, we can jump to the start 
    
            # find index where the current name ends
            found = -1
            # +1 to skip the row with the name itself
            for index, line in self.df.ix[position+1:].iterrows():
                line = line.fillna("")
                if line[0].strip() in self.names:
                    found = index
                    break
            if found == -1:
                found = index
            ends.append(found)
        self.end_positions = ends

    def interpret(self):
        if self.mode == "alternate":
            self.interpret_alternate()
        elif self.mode == "standard":
            self.interpret_standard()

    def interpret_standard(self):
        print('Standard input data')
        self.df = pd.read_csv(self.filename, sep=",")
        #self.df.fillna('', inplace=True)
        # replaces spaces by empty strings
        #self.df = self.df.applymap(lambda x: x.strip())
        #identify names
        self.names = list(self.df.Well.unique())
        wells = []

        for i, well_name in enumerate(self.names):
            data = self.df.ix[self.df.groupby("Well").groups[well_name]]
            # column TIM contains the unit, redundant with header. Besides,
            # cannot be used as float:
            data['TIM (nmole/L)'] = data['TIM (nmole/L)'].apply(lambda x: x.split(" ")[0])

            # convert all data to the correct type:
            for colname in data.columns:
                if colname in ['Well', 'Sample ID']:
                    pass
                else:
                    data[colname] = data[colname].astype(float)

            well_ID = data['Sample ID'].unique()[0]

            # !! data may be empty once the 0 and 6000 controls are removed
            mask = data['Size (bp)'].apply(lambda x: x>1 and x<5999)
            data = data[mask]

            well = Well(well_name, well_ID, data, sigma=self.sigma)
            wells.append(well)
        self.wells = wells

    def interpret_alternate(self):
        # Read a CSV file
        print('Alternate input data')
        self.df = pd.read_csv(self.filename, sep=",", header=None)
        # replaces spaces or empty spaces by empty na
        self.df = self.df.applymap(lambda x: np.nan if isinstance(x, str) and x.isspace() else x)

        # identify the submatrices in the CSV file
        self._identify_names()
        self._identify_start()
        self._identify_end()

        wells = []

        for i, name in enumerate(self.names):
            subdf = self.df.ix[self.start_positions[i]:self.end_positions[i]-1].copy()

            subdf.reset_index(inplace=True, drop=True)

            # get some data
            well_name = subdf.ix[0][0]
            well_ID = subdf.ix[0][1]

            data = subdf.copy()
            data = data.ix[1:] # drop first line ( well and samples ids)
            # then get next line to set the header
            data.columns = data.ix[1].values
            # drop the row used for the header, note that we start at index 2
            # since indices have names
            data = data.ix[2:]
            # now we will start at zero again
            data.reset_index(inplace=True, drop=True)

            # right now we have a dataframe with all data and metadata (TIV,
            # TIM, Total conc). Let us extract the metadata to get the value
            # of the RIC, TIM, Total conc
            metadata = data[data['Peak ID'].isnull()]

            # access 
            metadata = metadata.iloc[:, [1,2,3]]  # keep columns with data
            metadata = metadata.dropna()
            metadata.reset_index(inplace=True, drop=True)

            # Remove the rows where Size bp is the lower or upper mark (usually
            # at size = 1 or 6000. It has a string LM or UM in it
            self.data= data
            mask = data['Size (bp)'].apply(lambda x: isinstance(x, str) 
                    and 'UM' not in x and 'LM' not in x)

            data = data[mask].copy()

            data['TIC (ng/uL)'] = float(metadata.ix[0][1])
            data['TIM (nmole/L)'] = float(metadata.ix[1][1])
            data['Total Conc.: (ng/uL)'] = float(metadata.ix[2][1])

            # convert all data to the correct type:
            # get rid of rows where there are NAs, so TIC; TIM, Total conc
            # should be dropped 
            data.dropna(inplace=True)

            for colname in data.columns:
                if colname in ['Well', 'Sample ID']:
                    pass
                data[colname] = data[colname].astype(float)
                #except:
                #    data[colname] = data[colname]

            well = Well(well_name, well_ID, data, sigma=self.sigma)
            wells.append(well)

        self.wells = wells

    def get_line(self):
        # Returns  only 11 wells instead of 12. The last one one being the
        # control
        line = Line()
        for well in self.wells[0:-1]:
            line.append(well)
        line.control = self.wells[-1]
        return line

    def diagnostic(self):
        line = self.get_line()
        line.diagnostic()

    def get_peaks(self):
        line = self.get_line()
        return line.get_peaks()


def help():
    print("Usage:\n")
    print("fragment_analyser.py --pattern 2015*csv\n")
    print("fragment_analyser.py --pattern 2015*csv --output summary.csv\n")
    print("fragment_analyser.py --pattern 2015*csv --create-images\n")



if __name__ == "__main__":
    import sys
    print("Starting Fragment Analyser:")

    if len(sys.argv) <3 or  '--pattern' not in sys.argv:
        help()
        sys.exit()


    index = sys.argv.index("--pattern")
    pattern = sys.argv[index+1]


    # a user may use 2015*csv on the command line, which is expanded into a list
    # of filse unless user plase quotes around it "2015*csv". It is highly
    # likely that most users won't understand and forget the quotes

    if "*" in pattern or "?" in pattern:
        import glob
        filenames = glob.glob(pattern)
    else:
        # how many files do we have
        filenames = []
        # loop on sys.argv until we have a --
        count = index
        found = True
        while found:
            try:
                newfile = sys.argv[index+count]
                if newfile.startswith('--'):
                    found = False
                else:
                    filenames.append(newfile)
                    count += 1
            except:
                found = False


    if '--output' in sys.argv:
        index = sys.argv.index("--output")
        output_filename = sys.argv[index+1]
    else:
        output_filename = 'results.csv'


    if "--platform" in sys.argv:
        platform = sys.argc.index("--platform")
        output_filename = sys.argv[index+1]
    else:
        platform = raw_input("What data / platform is this ? (PFGE / PF1):")
    assert platform in ["PFGE", "PF1"]


    if platform == "PFGE":
        plate = PlatePFGE(filenames, output_filename=output_filename)
    else:
        plate = PlatePF1(filenames, output_filename=output_filename)

    plate.to_csv()

    if '--no-images' in sys.argv:
        pass
    else:
        print("Creating images")
        for i, line in enumerate(plate.lines):
            filename = '%s_diagnostic.png' % str(i+1) 
            print("Creating image %s out of %s (%s)" % (i+1, len(plate.lines),
                filename))
            line.diagnostic()
            pylab.savefig(filename)






