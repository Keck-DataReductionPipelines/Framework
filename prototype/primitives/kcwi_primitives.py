
from primitives.base_primitive import Base_primitive
from models.arguments import Arguments
from primitives.base_img import Base_img
from primitives.kcwi_file_primitives import *
import ccdproc
import numpy as np
import matplotlib.pyplot as pl




class subtract_overscan(Base_primitive):

    def __init__(self, action, context):
        Base_img.__init__(self, action, context)

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
                #self.frame.header['OSCNRN%d' % (ia + 1)] = \
                #    (sdrs, "amp%d RN in e- from oscan" % (ia + 1))

                if self.context.config.instrument.interactive>=1:
                    # plot data and fit
                    fig = self.context.plot
                    # fig = pl.figure(num=0, figsize=(17.0, 6.0))
                    # fig.canvas.set_window_title('KCWI DRP')
                    #pl.ion()
                    #fig = pl.figure(num=0, figsize=(17, 6))
                    fig.canvas.set_window_title('KCWI DRP')

                    pl.plot(osvec)
                    legend = ["oscan", ]
                    pl.plot(osfit)
                    legend.append("fit")
                    pl.xlabel("pixel")
                    pl.ylabel("DN")
                    pl.legend(legend)
                    pl.title("Overscan img #%d amp #%d" % (
                        self.context.data_set.getInfo(self.action.args.name,'FRAMENO'), (ia + 1)))

                    if self.context.config.instrument.interactive >= 2:
                        input("Next? <cr>: ")
                    else:
                        pl.pause(self.context.config.instrument.plotpause)
                    pl.clf()
                # subtract it
                for ix in range(dsec[ia][2], dsec[ia][3] + 1):
                    self.action.args.ccddata.data[y0:y1, ix] = \
                        self.action.args.ccddata.data[y0:y1, ix] - osfit
            performed = True
            #else:
            #    self.log.info("not enough overscan px to fit amp %d")

        #if performed:
        #    self.frame.header[key] = (True, self.keyword_comments[key])
        #else:
        #    self.frame.header[key] = (False, self.keyword_comments[key])
        #logstr = self.subtract_oscan.__module__ + "." + \
        #         self.subtract_oscan.__qualname__
        #self.frame.header['HISTORY'] = logstr
        #self.log.info(self.subtract_oscan.__qualname__)

        new_name = "%s_ovsc" % self.action.args.name
        kcwi_fits_writer(self.action.args.ccddata, table=self.action.args.table, output_file=new_name)
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

class process_contbars(Base_img):

    def __init__(self, action, context):
        Base_img.__init__(self, action, context)

    def _perform(self):
        return self.action.args

