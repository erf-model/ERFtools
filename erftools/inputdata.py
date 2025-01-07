"""
Data container for ParmParse data

see https://erf.readthedocs.io/en/latest/Inputs.html
"""

import numpy as np
from dataclasses import field
from typing import List, Tuple, Union
from pydantic.dataclasses import dataclass


@dataclass
class AMRParms:
    """amr.* parameters"""
    n_cell: Tuple[int, int, int] = (0,0,0)
    max_level: int = 0
    ref_ratio: Union[int,List[int]] = 2
    ref_ratio_vect: List[int] = field(default_factory=list)
    v: int = 0  # verbosity

    def __post_init__(self):
        assert all([ival>0 for ival in self.n_cell]), \
                'Need to specify amr.n_cell'
        assert self.max_level >= 0
        if isinstance(self.ref_ratio, list):
            assert len(self.ref_ratio) == self.max_level, \
                    'Need to specify a constant amr.ref_ratio' \
                    ' or one value per level'
            assert all(ratio in [2,3,4] for ratio in self.ref_ratio), \
                    'Invalid refinement ratio(s)'
        else:
            assert self.ref_ratio in [2,3,4], 'Invalid amr.ref_ratio'
        assert len(self.ref_ratio_vect) % 3 == 0, \
                'Need to specify ref ratios for each direction'
        assert all([ival in [2,3,4] for ival in self.ref_ratio_vect]), \
                'Invalid directional refinement ratio(s)'

    
@dataclass
class GeometryParms:
    """geometry.* parameters"""
    prob_lo: Tuple[float, float, float] = (0.,0.,0.)
    prob_hi: List[float] = field(default_factory=list)
    prob_extent: List[float] = field(default_factory=list)
    is_periodic: Tuple[int, int, int] = (0,0,0)

    def __post_init__(self):
        have_prob_hi = (len(self.prob_hi) == 3)
        have_prob_extent = (len(self.prob_extent) == 3)
        assert have_prob_hi or have_prob_extent
        if have_prob_extent:
            self.prob_hi = [self.prob_lo[i] + self.prob_extent[i]
                            for i in range(3)]
        else:
            self.prob_extent = [self.prob_hi[i] - self.prob_lo[i]
                                for i in range(3)]
        assert all([ival==0 or ival==1 for ival in self.is_periodic])


dycore_adv_schemes = [
    'Centered_2nd',
    'Upwind_3rd',
    'Blended_3rd4th',
    'Centered_4th',
    'Upwind_5th',
    'Blended_5th6th',
    'Centered_6th',
]
extra_scalar_adv_schemes = [
    'WENO3',
    'WENOZ3',
    'WENOMZQ3',
    'WENO5',
    'WENOZ5',
    'WENO7'
    'WENOZ7'
]

@dataclass
class ERFParms:
    """erf.* parameters"""

    # Governing Equations
    anelastic: bool = False  # solv anelastic eqns instead of compressible
    use_fft: bool = False  # use FFT rather than multigrid to solve Poisson eqns
    mg_v: int = 0  # multigrid solver verbosiy when solving Poisson

    # Refinement
    refinement_indicators: List[str] = field(default_factory=list)

    # Grid Stretching
    use_terrain: bool = False
    grid_stretching_ratio: float = 1.
    initial_dz: float = np.nan
    terrain_z_levels: List[float] = field(default_factory=list)

    # Time Step
    no_substepping: int = 0
    cfl: float = 0.8
    substepping_cfl: float = 1.0
    fixed_dt: float = np.nan
    fixed_fast_dt: float = np.nan
    fixed_mri_dt_ratio: int = -1

    # Restart
    restart: str = ''
    check_file: str = 'chk'
    check_int: int = -1
    check_per: float = -1.

    # PlotFiles
    plotfile_type: str = 'amrex'
    plot_file_1: str = 'plt_1_'
    plot_file_2: str = 'plt_2_'
    plot_int_1: int = -1
    plot_int_2: int = -1
    plot_per_1: float = -1.
    plot_per_2: float = -1.
    plot_vars_1: List[str] = field(default_factory=list)
    plot_vars_2: List[str] = field(default_factory=list)

    # Screen Output
    v: int = 0  # verbosity
    sum_interval: int = -1

    # Diagnostic Ouptuts
    data_log: List[str] = field(default_factory=list)
    profile_int: int = -1
    destag_profiles: bool = True

    # Advection Schemes
    dycore_horiz_adv_type: str = 'Upwind_3rd'
    dycore_vert_adv_type: str = 'Upwind_3rd'
    dryscal_horiz_adv_type: str = 'Upwind_3rd'
    dryscal_vert_adv_type: str = 'Upwind_3rd'
    moistscal_horiz_adv_type: str = 'Upwind_3rd'
    moistscal_vert_adv_type: str = 'Upwind_3rd'
    dycore_horiz_upw_frac: float = 1.
    dycore_vert_upw_frac: float = 1.
    dryscal_horiz_upw_frac: float = 1.
    dryscal_vert_upw_frac: float = 1.
    moistscal_horiz_upw_frac: float = 1.
    moistscal_vert_upw_frac: float = 1.
    use_efficient_advection: bool = False
    use_mono_advection: bool = False

    # Diffusive Physics
    molec_diff_type: str = 'None'
    dynamic_viscosity: float = 0.
    rho0_trans: float = 0.
    alpha_T: float = 0.
    alpha_C: float = 0.

    les_type: str = 'None'
    Pr_t: float = 1.0
    Sc_t: float = 1.0

    # - Smagorinsky SGS model
    Cs: float = 0.

    # - Deardorff SGS model
    Ck: float = 0.1
    Ce: float = 0.93
    Ce_wall: float = -1.
    sigma_k: float = 0.5
    theta_ref: float = 300.

    # - numerical diffusion
    num_diff_coeff: float = 0.

    # PBL Scheme
    pbl_type: str = 'None'

    # Forcing Terms
    use_gravity: bool = False
    use_coriolis: bool = False
    rotational_time_period: float = 86400.
    latitude: float = 90.
    coriolis_3d: bool= True

    abl_driver_type: str = 'None'
    abl_pressure_grad: Tuple[float,float,float] = (0.,0.,0.)
    abl_geo_wind: Tuple[float,float,float] = (0.,0.,0.)
    abl_geo_wind_table: str = ''

    nudging_from_input_sounding: bool = False
    input_sounding_file: Union[str,List[str]] = field(default_factory=list)
    input_sounding_time: List[float] = field(default_factory=list)

    rayleigh_damp_U: bool = False
    rayleigh_damp_V: bool = False
    rayleigh_damp_W: bool = False
    rayleigh_damp_T: bool = False
    rayleigh_dampcoef: float = 0.2
    rayleigh_zdamp: float = 500.

    # BCs
    use_explicit_most: bool = False

    # Initialization
    init_type: str = 'None'
    init_sounding_ideal: bool = False
    nc_init_file_0: Union[str,List[str]] = ''
    nc_bdy_file: str = ''
    project_initial_velocity: bool = False
    use_real_bcs: bool = False
    real_width: int = 0
    real_set_width: int = 0

    # Terrain
    terrain_type: str = 'Static'
    terrain_smoothing: int = 0
    terrain_file_name: str = ''

    # Moisture
    moisture_model: str = 'none'
    do_cloud: bool = True
    do_precip: bool = True

    def __post_init__(self):
        if self.anelastic:
            assert self.use_fft
            assert self.no_substepping
            assert self.project_initial_velocity
        assert self.cfl > 0 and self.cfl <= 1, 'erf.cfl out of range'
        assert self.substepping_cfl > 0 and self.substepping_cfl <= 1, \
                'erf.substepping_cfl out of range'
        if self.fixed_mri_dt_ratio > 0:
            assert self.fixed_mri_dt_ratio % 2 == 0, \
                    'erf.fixed_mri_dt_ratio should be even'
        if (self.fixed_dt is not np.nan) and (self.fixed_fast_dt is not np.nan):
            self.fixed_mri_dt_ratio = int(self.fixed_dt / self.fixed_fast_dt)
            assert self.fixed_mri_dt_ratio % 2 == 0, \
                    'erf.fixed_dt/erf.fixed_fast_dt should be even'
        assert len(self.data_log) <= 4, 'Unexpected number of data_log files'
        for vartype in ['dycore','dryscal','moistscal']:
            for advdir in ['horiz','vert']:
                advinp = f'{vartype}_{advdir}_adv_type'
                advscheme = getattr(self, advinp)
                if vartype == 'dycore':
                    assert advscheme in dycore_adv_schemes, \
                            f'Unexpected erf.{advinp}: {advscheme}'
                else:
                    assert advscheme in (dycore_adv_schemes
                                         +extra_scalar_adv_schemes), \
                            f'Unexpected erf.{advinp}: {advscheme}'
                if advscheme.startswith('Blended'):
                    upwinding = getattr(self, f'{vartype}_{advdir}_upw_frac')
                    assert (upwinding >= 0) and (upwinding <= 1)
        assert self.molec_diff_type in ['None','Constant','ConstantAlpha'], \
                'Unexpected erf.molec_diff_type'
        assert self.les_type in ['None','Smagorinsky','Deardorff'], \
                'Unexpected erf.les_type'
        if self.les_type == 'Smagorinsky':
            assert self.Cs > 0, 'Need to specify valid Smagorinsky Cs'
        assert self.pbl_type in ['None','MYNN25','YSU'], \
                'Unexpected erf.pbl_type'
        assert self.abl_driver_type in \
                ['None','PressureGradient','GeostrophicWind'], \
                'Unexpected erf.abl_driver_type'
        if self.nudging_from_input_sounding \
                and (len(self.input_sounding_file) > 1):
            assert len(self.input_sounding_file) == len(self.input_sounding_time), \
                    'Need to specify corresponding erf.input_sounding_time'
        elif isinstance(self.input_sounding_file, list) \
                and (len(self.input_sounding_file) > 0):
            self.input_sounding_file = self.input_sounding_file[0]
        assert self.init_type.lower() in \
                ['none','ideal','real','input_sounding','metgrid','uniform'], \
                'Invalid erf.init_type'
        if self.init_type.lower() == 'real':
            assert isinstance(self.nc_init_file_0, str), \
                    'should only have one nc_init_file_0'
        elif self.init_type.lower() == 'metgrid' \
                and isinstance(self.nc_init_file_0, str):
            self.nc_init_file_0 = [self.nc_init_file_0]
        assert self.terrain_type.lower() in ['static','moving'], \
                'Invalid erf.terrain_type'
        assert (self.terrain_smoothing >= 0) and (self.terrain_smoothing <= 2),\
                'Invalid erf.terrain_smoothing option'
        assert self.moisture_model.lower() in \
                ['sam','sam_noice',
                 'kessler','kessler_norain',
                 'satadj',
                 'none'], \
                'Unexpected erf.moisture_model'
