import sys
import numpy as np
import contextlib
from collections.abc import MutableMapping


# https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
@contextlib.contextmanager
def smart_open(fpath=None):
    if (fpath is not None):
        f = open(fpath, 'w')
    else:
        f = sys.stdout
    try:
        yield f
    finally:
        if f is not sys.stdout:
            f.close()


class ERFInputFile(MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        self.verbose = kwargs.pop('verbose',True)
        self.store = dict({
            'amr.refinement_indicators': '',
            # retrieved from wrfinput_d01 
            'erf.most.z0': None,
            'erf.most.surf_temp': None,
            'erf.latitude': None,
            'erf.rotational_time_period': None,
            # estimated quuantities
            'erf.z_levels': [],  # can estimate from wrfinput_d01
        })
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __str__(self):
        #return '\n'.join([f'{key} = {str(val)}' for key,val in self.items()])
        s = ''
        for key,val in self.items():
            if isinstance(val, (list,tuple,np.ndarray)):
                val = ' '.join([str(v) for v in val])
            s += f'{key} = {str(val)}\n'
        return s.rstrip()

    def __getitem__(self, key):
        return self.store[self._keytransform(key)]

    def __setitem__(self, key, value):
        try:
            oldval = self[key]
        except KeyError:
            pass
        else:
            if self.verbose:
                print(f'Overriding existing `{key}` with {value}')
        finally:
            self.store[self._keytransform(key)] = value

    def __delitem__(self, key):
        del self.store[self._keytransform(key)]

    def __iter__(self):
        return iter(self.store)
    
    def __len__(self):
        return len(self.store)

    def _keytransform(self, key):
        return key

    def write(self,fpath=None,ideal=False):
        refinement_boxes = ''
        boxes = self.store['amr.refinement_indicators'].split()
        for box in boxes:
            loindices = ' '.join([str(val) for val in self.store[f'amr.{box}.in_box_lo']])
            hiindices = ' '.join([str(val) for val in self.store[f'amr.{box}.in_box_hi']])
            refinement_boxes += f'amr.{box}.in_box_lo = {loindices}\n' 
            refinement_boxes += f'amr.{box}.in_box_hi = {hiindices}\n' 

        with smart_open(fpath) as f:

            f.write('# ------------------  INPUTS TO MAIN PROGRAM  -------------------\n')
            f.write('# generated by https://github.com/erf-model/erftools\n')
            f.write(f"""
amrex.fpe_trap_invalid = 1
fabarray.mfiter_tile_size = 1024 1024 1024

# PROBLEM SIZE & GEOMETRY
amr.n_cell           = {' '.join([str(v) for v in self.store['amr.n_cell']])}
geometry.prob_extent = {' '.join([str(v) for v in self.store['geometry.prob_extent']])} # zmax estimated from WRF `p_top_requested`
geometry.is_periodic = {' '.join([str(int(b)) for b in self.store['geometry.is_periodic']])}
""")
            if len(self.store['erf.z_levels']) > 0:
                f.write(f"""
#erf.z_levels = {' '.join([str(v) for v in self.store['erf.z_levels']])}  # TODO: need to implement this input
""")
            f.write(f"""
# TIME STEP CONTROL
max_step           = 0
stop_time          = {self.store['stop_time']}
erf.fixed_dt       = {self.store['erf.fixed_dt']}  # fixed time step depending on grid resolution
erf.use_native_mri = 1

# REFINEMENT / REGRIDDING
amr.max_level      = {self.store['amr.max_level']}  # maximum level number allowed
""")
            if self.store['amr.refinement_indicators'] != '':  
                f.write("""
amr.ref_ratio_vect = {' '.join([str(v) for v in self.store['amr.ref_ratio_vect']])}
amr.refinement_indicators = {self.store['amr.refinement_indicators']}
{refinement_boxes.rstrip()}
""")

            f.write(f"""
# BOUNDARY CONDITIONS
zlo.type = "{self.store['zlo.type']}"
zhi.type = "SlipWall"
""")
            if self.store['zlo.type'] == 'MOST':
                f.write(f"""
erf.most.z0 = {self.store['erf.most.z0']}  # TODO: use roughness map
erf.most.zref = 200.0
erf.most.surf_temp = {self.store['erf.most.surf_temp']}  # TODO: use surface temperature map
""")

            if ideal:
                f.write("""
# INITIAL CONDITIONS
erf.init_type           = "input_sounding"
erf.input_sounding_file = "input_sounding"
""")
            else:
                bdylist = ' '.join([f'"wrfbdy_d{idom+1:02d}"'
                                    for idom in
                                    range(self.store['amr.max_level']+1)])
                f.write(f"""
# INITIAL CONDITIONS
erf.init_type    = "real"
erf.nc_init_file = "wrfinput_d01"
erf.nc_bdy_file  = {bdylist}
""")

            f.write(f"""
# PHYSICS OPTIONS
erf.les_type = "None"
erf.pbl_type = "{self.store['erf.pbl_type']}"  # TODO: specify for each level
erf.abl_driver_type = "None"
erf.use_gravity = true
erf.use_coriolis = true
erf.latitutde = {self.store['erf.latitude']}
erf.rotational_time_period = {self.store['erf.rotational_time_period']}

erf.molec_diff_type = "{self.store['erf.molec_diff_type']}"
erf.rho0_trans = {self.store['erf.rho0_trans']}  # i.e., dynamic == kinematic coefficients
erf.dynamicViscosity = {self.store['erf.dynamicViscosity']}  # TODO: specify for each level
erf.alpha_T = {self.store['erf.alpha_T']}  # TODO: specify for each level
erf.alpha_C = {self.store['erf.alpha_C']}  # TODO: specify for each level

# SOLVER CHOICES
erf.spatial_order = 2

# DIAGNOSTICS & VERBOSITY
erf.sum_interval = 1  # timesteps between computing mass
erf.v            = 1  # verbosity in ERF.cpp
amr.v            = 1  # verbosity in Amr.cpp

""")
        if fpath is not None:
            print('Wrote',fpath)
            
