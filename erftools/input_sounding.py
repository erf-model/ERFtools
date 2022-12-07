#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

from .constants import R_d, c_p, g, p0, rvovrd, cvpm


class InputSounding(object):

    def __init__(self,fpath='input_sounding'):
        """See WRF User's Guide for file format"""
        with open(fpath,'r') as f:
            # The first line includes the surface pressure (hPa), potential
            # temperature (K) and moisture mixing ratio (g/kg).
            p_surf, T_surf, qv_surf = [float(val) for val in f.readline().split()]

            # Each subsequent line has five input values: height (meters above
            # sea-level), dry potential temperature (K), vapor mixing ratio
            # (g/kg), x-direction wind component (m/s), and y-direction wind
            # component (m/s)
            init = np.loadtxt(f)

        self.p_surf = p_surf * 100 # [Pa]
        self.th_surf = T_surf # [K]
        self.qv_surf = qv_surf * 0.001 # [g/g]

        self.z  = init[:,0]
        self.th = init[:,1]
        self.qv = init[:,2] * 0.001
        self.u  = init[:,3]
        self.v  = init[:,4]


    def integrate_column_wrf(self,verbose=False,Niter=10):
        """Follow dyn_em/module_initialize_ideal.F (legacy code)

        Notes:
        - `qvf` is not strictly correct as implemented in WRF ideal.exe
          which is consistent with WRF's "moist theta" which is not
          exactly virtual potential temperature. See, e.g.,
          https://github.com/NCAR/WRFV3/issues/4
        - `qv_surf` is ignored
        - WRF ideal.exe also returns dry theta
        """
        qvf = 1. + rvovrd*self.qv[0]
        rho_surf = 1. / ((R_d/p0)*self.th_surf*qvf*((self.p_surf/p0)**cvpm))
        pi_surf = (self.p_surf/p0)**(R_d/c_p)
        if verbose:
            print('surface density, pi =',rho_surf,pi_surf)

        # integrate moist sounding hydrostatically, starting from the specified
        # surface pressure
        N = len(self.th)
        self.rho = np.zeros(N)
        self.thm = np.zeros(N)
        self.pm = np.zeros(N)
        self.p = np.zeros(N)

        # 1. Integrate from surface to lowest level
        qvf = 1. + rvovrd*self.qv[0]
        qvf1 = 1.0 + self.qv[0]
        self.rho[0] = rho_surf
        dz = self.z[0]
        for i in range(Niter):
            self.pm[0] = self.p_surf - 0.5*dz*(rho_surf + self.rho[0])*g*qvf1
            self.rho[0] = 1./((R_d/p0)*self.th[0]*qvf*((self.pm[0]/p0)**cvpm))
        self.thm[0] = self.th[0] * qvf

        # 2. Integrate up the column
        for k in range(1,N):
            self.rho[k] = self.rho[k-1]
            dz = self.z[k] - self.z[k-1]
            qvf1 = 0.5*(2. + (self.qv[k-1] + self.qv[k]))
            qvf = 1. + rvovrd*self.qv[k]
            for i in range(Niter):
                self.pm[k] = self.pm[k-1] \
                        - 0.5*dz*(self.rho[k] + self.rho[k-1])*g*qvf1
                assert self.pm[k] > 0, 'too cold for chosen height'
                self.rho[k] = 1./((R_d/p0)*self.th[k]*qvf*((self.pm[k]/p0)**cvpm))
            self.thm[k] = self.th[k] * qvf
        # we have the moist sounding at this point...

        # 3. Compute the dry sounding using p at the highest level from the
        #    moist sounding and integrating down
        self.p[N-1] = self.pm[N-1]
        for k in range(N-2,-1,-1):
            dz = self.z[k+1] - self.z[k]
            self.p[k] = self.p[k+1] + 0.5*dz*(self.rho[k]+self.rho[k+1])*g

        if verbose:
            print('error',
                  np.max(np.abs(p0 - self.rho*R_d*self.thm*(self.pm/p0)**cvpm)))


    def integrate_column(self,verbose=False,Niter=10):
        """Based on dyn_em/module_initialize_ideal.F

        Here, the "moist" theta is virtual potential temperature:
          thm = th * qvf
        where
          qvf = 1 + (R_v/R_d - 1)*qv
        is the moist air correction factor.

        This returns profiles of total density, moist theta as defined
        above, water vapor mixing ratio, and horizontal wind components.
        """
        #qvf = 1. + rvovrd*self.qv[0] # WRF
        qvf = 1. + (rvovrd-1)*self.qv_surf
        rho_surf = 1. / ((R_d/p0)*self.th_surf*qvf*((self.p_surf/p0)**cvpm))
        pi_surf = (self.p_surf/p0)**(R_d/c_p)
        if verbose:
            print('surface density, pi =',rho_surf,pi_surf)

        # integrate moist sounding hydrostatically, starting from the specified
        # surface pressure
        N = len(self.th)
        self.rho = np.zeros(N)
        self.thm = np.zeros(N)
        self.pm = np.zeros(N)
        self.p = np.zeros(N)

        # 1. Integrate from surface to lowest level
        qvf = 1. + (rvovrd-1)*self.qv[0]
        qvf1 = 1. + self.qv[0]
        self.rho[0] = rho_surf
        dz = self.z[0]
        for i in range(Niter):
            self.pm[0] = self.p_surf - 0.5*dz*(rho_surf + self.rho[0])*g*qvf1
            self.rho[0] = 1./((R_d/p0)*self.th[0]*qvf*((self.pm[0]/p0)**cvpm))
        self.thm[0] = self.th[0] * qvf
        if verbose:
            print(0.0, self.pm[0], self.rho[0], self.thm[0])

        # 2. Integrate up the column
        for k in range(1,N):
            self.rho[k] = self.rho[k-1]
            dz = self.z[k] - self.z[k-1]
            qvf1 = 0.5*(2. + (self.qv[k-1] + self.qv[k]))
            qvf = 1. + (rvovrd-1)*self.qv[k]
            for i in range(Niter):
                self.pm[k] = self.pm[k-1] \
                        - 0.5*dz*(self.rho[k] + self.rho[k-1])*g*qvf1
                assert self.pm[k] > 0, 'too cold for chosen height'
                self.rho[k] = 1./((R_d/p0)*self.th[k]*qvf*((self.pm[k]/p0)**cvpm))
            self.thm[k] = self.th[k] * qvf
            if verbose:
                print(self.z[k], self.pm[k], self.rho[k], self.thm[k])
        # we have the moist sounding at this point...

        # 3. Compute the dry sounding using p at the highest level from the
        #    moist sounding and integrating down
        self.p[N-1] = self.pm[N-1]
        for k in range(N-2,-1,-1):
            dz = self.z[k+1] - self.z[k]
            self.p[k] = self.p[k+1] + 0.5*dz*(self.rho[k]+self.rho[k+1])*g

        if verbose:
            print('error',
                  np.max(np.abs(p0 - self.rho*R_d*self.thm*(self.pm/p0)**cvpm)))


    def plot(self):
        """Call before integrate_column() to plot just the inputs;
        after integrating through the moist air column, this will plot
        additional quantities: rho and p.
        """
        allplots = True if hasattr(self, 'rho') else False
        if allplots:
            fig,ax = plt.subplots(ncols=5,sharey=True,figsize=(15,6))
        else:
            fig,ax = plt.subplots(ncols=3,sharey=True,figsize=(9,6))

        # plot profiles
        ax[0].plot(self.th, self.z, label='dry')
        if allplots:
            ax[0].plot(self.thm, self.z, label='moist')
        ax[0].plot(self.th_surf, 0, 'ko', markerfacecolor='none')
        ax[1].plot(self.qv, self.z)
        ax[1].plot(self.qv_surf, 0, 'ko', markerfacecolor='none')
        ax[2].plot(self.u, self.z, label='u')
        ax[2].plot(self.v, self.z, label='v')
        if allplots:
            ax[3].plot(self.rho, self.z)
            ax[4].plot(self.p, self.z, label='dry')
            ax[4].plot(self.pm, self.z, label='moist')
            ax[4].plot(self.p_surf, 0, 'ko', markerfacecolor='none')

        # labels and legends
        ax[0].set_ylabel('altitude AGL [m]')
        if allplots:
            ax[0].set_xlabel('potential temperature [K]')
            ax[0].legend(loc='best')
        else:
            ax[0].set_xlabel('dry potential temperature [K]')
        ax[1].set_xlabel('water vapor mixing ratio [g/g]')
        ax[2].set_xlabel('horizontal wind component [m/s]')
        ax[2].legend(loc='best')
        if allplots:
            ax[3].set_xlabel('density [kg/m^3]')
            ax[4].set_xlabel('pressure [Pa]')
            ax[4].legend(loc='best')

        for axi in ax:
            axi.grid()

        return fig,ax


#==============================================================================
if __name__ == '__main__':

    inp = InputSounding()
    fig,ax = inp.plot()
    fig.savefig('input_sounding0.png',bbox_inches='tight')

    inp.integrate_column_wrf(verbose=True)
    fig,ax = inp.plot()
    fig.savefig('input_sounding_wrf.png',bbox_inches='tight')

    inp.integrate_column(verbose=True)
    fig,ax = inp.plot()
    fig.savefig('input_sounding.png',bbox_inches='tight')

