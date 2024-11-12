import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class SurfaceHistory(object):
    """Process text diagnostic output that was written out with:
        ```
        erf.v           = 1
        erf.data_log    = hist.txt
        ```
    """
    timename = 't' # 'time'
    heightname = 'z' # 'height'
    surfvars = ['t','ustar','tstar','L']

    def __init__(self, histfile, t0=0.0, dt=None, timedelta=False,
                 resample=None):
        """Load diagnostic profile data from 3 datafiles

        Parameters
        ----------
        histfile : string
            Surface time history file to load
        t0 : float, optional
            With `dt`, used to overwrite the timestamps in the text data
            to address issues with insufficient precision
        dt : float, optional
            Overwrite the time dimension coordinate with
            t0 + np.arange(Ntimes)*dt
        timedelta : bool, optional
            If true, convert time index to a TimedeltaIndex
        resample : str, optional
            Calculate rolling mean with given interval; implies
            timedelta=True
        """
        self.df = pd.read_csv(histfile, sep='\s+', names=self.surfvars)
        self.df = self.df.drop_duplicates()
        if dt is not None:
            dt0 = self.df['t'].iloc[0]
            if not dt==dt0:
                print('Warning: inconsistent specified dt and first step',dt,dt0)
            self.df['t'] = t0 + (np.arange(len(self.df))+1)*dt
        if timedelta or (resample is not None):
            self.df['t'] = pd.to_timedelta(self.df['t'],unit='s')
        self.df = self.df.set_index('t')
        if resample:
            assert isinstance(resample, str)
            self.df = self.df.resample(resample).mean()

    def plot(self,*args,**plot_kwargs):
        """Quick plotting function"""
        varns = self.surfvars[1:] if (len(args) == 0) else args
        if isinstance(varns,str):
            varns = [varns]
        tidx = self.df.index
        if isinstance(self.df.index, pd.TimedeltaIndex):
            tidx = tidx.total_seconds()
        fig,axs = plt.subplots(nrows=len(varns),figsize=(5,2.5*len(varns)))
        if len(varns) == 1:
            axs = [axs]
        for varn,ax in zip(varns,axs):
            ax.plot(tidx, self.df[varn], **plot_kwargs)
            ax.set_ylabel(varn)
            ax.grid()
        axs[-1].set_xlabel('simulation time [s]')
        if len(axs) == 1:
            axs = axs[0]
        return fig, axs

    def ustar(self,Tavg=3600.0):
        """Get final time-averaged friction velocity"""
        return self.df.loc[self.df.index[-1]-Tavg:,'ustar'].mean()

