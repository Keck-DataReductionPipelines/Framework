
from primitives.base_primitive import Base_primitive
from models.arguments import Arguments
from primitives.base_img import Base_img
from primitives.kcwi_file_primitives import *
import ccdproc
import numpy as np
import matplotlib.pyplot as pl
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.io import save
from scipy.signal import find_peaks
from skimage import transform as tf



class subtract_overscan(Base_primitive):

    def __init__(self, action, context):
        Base_primitive.__init__(self, action, context)


    def _perform(self):
        # image sections for each amp
        bsec, dsec, tsec, direc = self.action.args.map_ccd
        namps = len(bsec)
        # polynomial fit order
        if namps == 4:
            porder = 2
        else:
            porder = 7
        # header keyword to update
        key = 'OSCANSUB'
        # is it performed?
        performed = False
        # loop over amps
        for ia in range(namps):
            # get gain
            gain = self.context.data_set.getInfo(self.action.args.name, 'GAIN%d' % (ia + 1))
            # check if we have enough data to fit
            if (bsec[ia][3] - bsec[ia][2]) > self.context.config.instrument.minoscanpix:
                # pull out an overscan vector
                x0 = bsec[ia][2] + self.context.config.instrument.oscanbuf
                x1 = bsec[ia][3] - self.context.config.instrument.oscanbuf
                y0 = bsec[ia][0]
                y1 = bsec[ia][1] + 1
                osvec = np.nanmedian(self.action.args.ccddata.data[y0:y1, x0:x1], axis=1)
                nsam = x1 - x0
                xx = np.arange(len(osvec), dtype=np.float)
                # fit it, avoiding first 50 px
                if direc[ia]:
                    # forward read skips first 50 px
                    oscoef = np.polyfit(xx[50:], osvec[50:], porder)
                else:
                    # reverse read skips last 50 px
                    oscoef = np.polyfit(xx[:-50], osvec[:-50], porder)
                # generate fitted overscan vector for full range
                osfit = np.polyval(oscoef, xx)
                # calculate residuals
                resid = (osvec - osfit) * math.sqrt(nsam) * gain / 1.414
                sdrs = float("%.3f" % np.std(resid))
                self.logger.info("Amp%d Read noise from oscan in e-: %.3f" %
                          ((ia + 1), sdrs))
                self.action.args.ccddata.header['OSCNRN%d' % (ia + 1)] = (sdrs, "amp%d RN in e- from oscan" % (ia + 1))

                if self.context.config.instrument.interactive>=1:
                    # plot data and fit
                    #fig = self.context.plot
                    # fig = pl.figure(num=0, figsize=(17.0, 6.0))
                    # fig.canvas.set_window_title('KCWI DRP')
                    #pl.ion()
                    #fig = pl.figure(num=0, figsize=(17, 6))
                    #fig.canvas.set_window_title('KCWI DRP')
                    x=np.arange(len(osvec))
                    p = figure(title='Overscan amp %d' % (ia+1), x_axis_label='x', y_axis_label='counts')
                    p.line(x,osvec)
                    p.line(x,osfit)
                    show(p)
                    #if ia==0:
                    #    show(p)
                    #else:
                    #    save(p)
                    #pl.plot(osvec)
                    #legend = ["oscan", ]
                    #pl.plot(osfit)
                    #legend.append("fit")
                    #pl.xlabel("pixel")
                    #pl.ylabel("DN")
                    #pl.legend(legend)
                    #pl.title("Overscan img #%d amp #%d" % (
                    #    self.context.data_set.getInfo(self.action.args.name,'FRAMENO'), (ia + 1)))

                    if self.context.config.instrument.interactive >= 2:
                        input("Next? <cr>: ")
                    else:
                        pl.pause(self.context.config.instrument.plotpause)
                    #pl.clf()
                # subtract it
                for ix in range(dsec[ia][2], dsec[ia][3] + 1):
                    self.action.args.ccddata.data[y0:y1, ix] = \
                        self.action.args.ccddata.data[y0:y1, ix] - osfit
            performed = True
            #else:
            #    self.log.info("not enough overscan px to fit amp %d")

        if performed:
            self.action.args.ccddata.header[key] = (True, 'Overscan subtracted')
        else:
            self.action.args.ccddata.header[key] = (False, 'Overscan subtracted')
        logstr = self.__module__ + "." + self.__class__.__name__
        self.action.args.ccddata.header['HISTORY'] = logstr
        #self.log.info(self.subtract_oscan.__qualname__)

        #new_name = "%s_ovsc" % self.action.args.name
        kcwi_fits_writer(self.action.args.ccddata, table=self.action.args.table, output_file=self.action.args.name, suffix="oscan")
        return self.action.args


class trim_overscan(Base_primitive):

    def __init__(self, action, context):
        Base_primitive.__init__(self, action, context)

    def _perform(self):

        # parameters
        # image sections for each amp
        bsec, dsec, tsec, direc = self.action.args.map_ccd
        namps = len(bsec)
        # header keyword to update
        key = 'OSCANTRM'
        # get output image dimensions
        max_sec = max(tsec)
        # create new blank image
        new = np.zeros((max_sec[1]+1, max_sec[3]+1), dtype=np.float64)
        # loop over amps
        for ia in range(namps):
            # input range indices
            yi0 = dsec[ia][0]
            yi1 = dsec[ia][1] + 1
            xi0 = dsec[ia][2]
            xi1 = dsec[ia][3] + 1
            # output range indices
            yo0 = tsec[ia][0]
            yo1 = tsec[ia][1] + 1
            xo0 = tsec[ia][2]
            xo1 = tsec[ia][3] + 1
            # transfer to new image
            new[yo0:yo1, xo0:xo1] = self.action.args.ccddata.data[yi0:yi1, xi0:xi1]
            # update amp section
            sec = "[%d:" % (xo0+1)
            sec += "%d," % xo1
            sec += "%d:" % (yo0+1)
            sec += "%d]" % yo1
            self.logger.info("ADDING ATSEC%d" % (ia + 1))
            self.action.args.ccddata.header['ATSEC%d' % (ia+1)] = sec
            # remove obsolete sections
            self.action.args.ccddata.header.pop('ASEC%d' % (ia + 1))
            self.action.args.ccddata.header.pop('BSEC%d' % (ia + 1))
            self.action.args.ccddata.header.pop('DSEC%d' % (ia + 1))
            self.action.args.ccddata.header.pop('CSEC%d' % (ia + 1))
        # update with new image
        self.action.args.ccddata.data = new
        self.action.args.ccddata.header['NAXIS1'] = max_sec[3] + 1
        self.action.args.ccddata.header['NAXIS2'] = max_sec[1] + 1
        self.action.args.ccddata.header[key] = (True, "Overscan trimmed")

        logstr = self.__module__ + "." + \
                 self.__class__.__name__
        self.action.args.ccddata.header['HISTORY'] = logstr
        #new_name = "%s_trim" % self.action.args.name

        kcwi_fits_writer(self.action.args.ccddata, table=self.action.args.table, output_file=self.action.args.name, suffix="trim")
        return self.action.args
        #self.log.info(self.trim_oscan.__qualname__)


class correct_gain(Base_primitive):

    def __init__(self, action, context):
        Base_primitive.__init__(self, action, context)

    def _perform(self):
        #print(self.action.args.ccddata.header)
        namps = self.action.args.namps
        for ia in range(namps):
            # get amp section
            section = self.action.args.ccddata.header['ATSEC%d' % (ia +1)]
            sec, rfor = parse_imsec(section)
            # get gain for this amp
            gain = self.context.data_set.getInfo(self.action.args.name,'GAIN%d' % (ia + 1))
            self.logger.info("Applying gain correction of %.3f in section %s" %(gain, self.action.args.ccddata.header['ATSEC%d' % (ia + 1)]))
            self.action.args.ccddata.data[sec[0]:(sec[1]+1), sec[2]:(sec[3]+1)] *= gain
            #sliced_ccddata.header=self.action.args.header

            #multiplied_ccddata = sliced_ccddata.multiply(gain)
            #mu
            #self.action.args.ccddata=multiplied_ccddata

        self.action.args.ccddata.header['GAINCOR'] = (True, "Gain corrected")
        self.action.args.ccddata.header['BUNIT'] = ('electron','Units set to electrons')
        self.action.args.ccddata.unit = 'electron'

        #logstr = self.correct_gain.__module__ + "." + \
        #         self.correct_gain.__qualname__
        #self.frame.header['HISTORY'] = logstr
        #self.log.info(self.correct_gain.__qualname__)
        #self.logger.info("Writing test file")
        #self.action.args.ccddata.write('test.fits')
        kcwi_fits_writer(self.action.args.ccddata, table=self.action.args.table, output_file=self.action.args.name, suffix="int")
        return self.action.args

class process_bias(Base_img):

    def __init__(self, action, context):
        Base_img.__init__(self, action, context)

    def _pre_condition(self):
        """
        Checks is we can build a stacked  frame
        Expected arguments:
            want_type: ie. BIAS
            min_files: ie 10
            new_type: ie MASTER_BIAS
            new_file_name: master_bias.fits

        """
        try:
            args = self.action.args
            df = self.context.data_set.data_table
            files = df[(df.IMTYPE == args.want_type) & (df.GROUPID == args.groupid)]
            nfiles = len(files)


            self.logger.info(f"pre condition got {nfiles}, expecting {args.min_files}")
            if nfiles < 1 or nfiles < args.min_files:
                return False
            return True
        except Exception as e:
            self.logger.error(f"Exception in base_ccd_primitive: {e}")
            return False

    def _perform(self):
        """
        Returns an Argument() with the parameters that depends on this operation.
        """
        args = self.action.args

        df = self.context.data_set.data_table
        files = list(df[(df.IMTYPE == args.want_type) & (df.GROUPID == args.groupid)].index)
        stack = []
        for file in files:
            # using [0] drops the table
            stack.append(kcwi_fits_reader(file)[0])

        stacked = ccdproc.combine(stack)
        stacked.header.IMTYPE=args.new_type

        kcwi_fits_writer(stacked, output_file = args.new_file_name)

        return Arguments(name=args.new_file_name)

class process_contbars(Base_primitive):

    def __init__(self, action, context):
        Base_primitive.__init__(self, action, context)

    def _perform(self):
        return self.action.args

class find_bars(Base_primitive):

    def __init__(self, action, context):
        Base_primitive.__init__(self, action, context)

    def _perform(self):
        self.logger.info("Finding continuum bars")
        # Do we plot?
        if self.context.config.instrument.interactive >= 1:
            do_plot = True
            pl.ion()
        else:
            do_plot = False
        # initialize
        midcntr = []
        # get image dimensions
        nx = self.action.args.ccddata.data.shape[1]
        ny = self.action.args.ccddata.data.shape[0]
        # get binning
        ybin = self.action.args.ybinsize
        win = int(10 / ybin)
        # select from center rows of image
        midy = int(ny / 2)
        midvec = np.median(self.action.args.ccddata.data[(midy-win):(midy+win+1), :], axis=0)
        # set threshold for peak finding
        midavg = np.average(midvec)
        self.logger.info("peak threshold = %f" % midavg)
        # find peaks above threshold
        midpeaks, _ = find_peaks(midvec, height=midavg)
        # do we have the requisite number?
        if len(midpeaks) != self.context.config.instrument.NBARS:
            self.logger.error("Did not find %d peaks: n peaks = %d"
                           % (self.context.config.instrument.NBARS, len(midpeaks)))
        else:
            self.logger.info("found %d bars" % len(midpeaks))
            if do_plot:
                # plot the peak positions
                pl.plot(midvec, '-')
                pl.plot(midpeaks, midvec[midpeaks], 'rx')
                pl.plot([0, nx], [midavg, midavg], '--', color='grey')
                pl.xlabel("CCD X (px)")
                pl.ylabel("e-")
                pl.title("Img %d, Thresh = %.2f" %
                         (self.frame.header['FRAMENO'], midavg))
            # calculate the bar centroids
            for peak in midpeaks:
                xs = list(range(peak-win, peak+win+1))
                ys = midvec[xs] - np.nanmin(midvec[xs])
                xc = np.sum(xs*ys) / np.sum(ys)
                midcntr.append(xc)
                if do_plot:
                    pl.plot([xc, xc], [midavg, midvec[peak]], '-.',
                            color='grey')
            if do_plot:
                pl.plot(midcntr, midvec[midpeaks], 'gx')
                if self.context.config.instrument.interactive >= 2:
                    input("next: ")
                else:
                    pl.pause(self.frame.plotpause())
            self.logger.info("Found middle centroids for continuum bars")
        self.action.args.midcntr = midcntr
        self.action.args.midrow = midy
        self.action.args.win = win
        return self.action.args


class trace_bars(Base_primitive):

    def __init__(self, action, context):
        Base_primitive.__init__(self, action, context)

    def _perform(self):
        self.logger.info("Tracing continuum bars")
        if self.context.config.instrument.interactive >= 1:
            do_plot = True
            pl.ion()
        else:
            do_plot = False
        if len(self.action.args.midcntr) < 1:
            self.logger.error("No bars found")
        else:
            # initialize
            samp = int(80 / self.action.args.ybinsize)
            win = self.action.args.win
            xi = []     # x input
            xo = []     # x output
            yi = []     # y input (and output)
            barid = []  # bar id number
            slid = []   # slice id number
            # loop over bars
            for barn, barx in enumerate(self.action.args.midcntr):
                # nearest pixel to bar center
                barxi = int(barx + 0.5)
                self.logger.info("bar number %d is at %.3f" % (barn, barx))
                # middle row data
                xi.append(barx)
                xo.append(barx)
                yi.append(self.action.args.midrow)
                barid.append(barn)
                slid.append(int(barn/5))
                # trace up
                samy = self.action.args.midrow + samp
                done = False
                while samy < (self.action.args.ccddata.data.shape[0] - win) and not done:
                    ys = np.median(
                        self.action.args.ccddata.data[(samy - win):(samy + win + 1),
                                        (barxi - win):(barxi + win + 1)],
                        axis=0)
                    ys = ys - np.nanmin(ys)
                    xs = list(range(barxi - win, barxi + win + 1))
                    xc = np.sum(xs * ys) / np.sum(ys)
                    if np.nanmax(ys) > 255:
                        xi.append(xc)
                        xo.append(barx)
                        yi.append(samy)
                        barid.append(barn)
                        slid.append(int(barn/5))
                    else:
                        done = True
                    samy += samp
                # trace down
                samy = self.action.args.midrow - samp
                done = False
                while samy >= win and not done:
                    ys = np.median(
                        self.action.args.ccddata.data[(samy - win):(samy + win + 1),
                                        (barxi - win):(barxi + win + 1)],
                        axis=0)
                    ys = ys - np.nanmin(ys)
                    xs = list(range(barxi - win, barxi + win + 1))
                    xc = np.sum(xs * ys) / np.sum(ys)
                    if np.nanmax(ys) > 255:
                        xi.append(xc)
                        xo.append(barx)
                        yi.append(samy)
                        barid.append(barn)
                        slid.append(int(barn / 5))
                    else:
                        done = True
                    # disable for now
                    samy -= samp
            # end loop over bars
            # create source and destination coords
            yo = yi
            dst = np.column_stack((xi, yi))
            src = np.column_stack((xo, yo))
            if do_plot:
                # plot them
                pl.clf()
                # pl.ioff()
                pl.plot(xi, yi, 'x', ms=0.5)
                pl.plot(self.action.args.midcntr, [self.action.args.midrow]*120, 'x', color='red')
                pl.xlabel("CCD X (px)")
                pl.ylabel("CCD Y (px)")
                pl.title("Img %d" % self.action.args.ccddata.header['FRAMENO'])
                if self.context.config.instrument.interactive >= 2:
                    pl.show()
                    input("next: ")
                else:
                    pl.pause(self.frame.plotpause())
            #self.write_table(table=[src, dst, barid, slid],
            #                 names=('src', 'dst', 'barid', 'slid'),
            #                 suffix='trace',
            #                 comment=['Source and destination fiducial points',
            #                          'Derived from KCWI continuum bars images',
            #                          'For defining spatial transformation'],
            #                 keywords={'MIDROW': self.midrow,
            #                           'WINDOW': self.win})
            if True:
                # fit transform
                self.logger.info("Fitting spatial control points")
                tform = tf.estimate_transform('polynomial', src, dst, order=3)
                self.logger.info("Transforming bars image")
                warped = tf.warp(self.action.args.ccddata.data, tform)
                # write out warped image
                self.action.args.ccddata.data = warped
                kcwi_fits_writer(self.action.args.ccddata, self.action.args.table, output_file=self.action.args.name, suffix='warped')
                self.logger.info("Transformed bars produced")