import xarray as xr

def stagger_profile(ds,field,surfval=0.0):
    """Interpolate cell-centered field to staggered z locations on the
    interior; extrapolate to domain top; and set the surface value.
    """
    assert 'z' in ds[field].dims, 'Expected unstaggered field'
    assert 'zstag' not in ds[field].dims, 'Should not have both z and zstag'

    zbot = ds.coords['zstag'].values[0]
    ztop = ds.coords['zstag'].values[-1]

    top = 1.5*ds[field].isel(z=-1) - 0.5*ds[field].isel(z=-2)
    top = top.expand_dims({'z':[ztop]})

    interior = xr.DataArray(
        0.5*(  ds[field].isel(z=slice(0,  -1)).values
             + ds[field].isel(z=slice(1,None)).values),
        coords={'t': ds.coords['t'],
                'z': ds.coords['zstag'].values[1:-1]},
        dims=('t','z')
    )

    surface = surfval * xr.ones_like(top)
    surface = surface.assign_coords(z=[zbot])

    da = xr.concat((surface,interior,top), dim='z')
    da = da.transpose('t','z')
    da = da.rename(z='zstag')
    return da

def destagger_profile(ds,field):
    """Interpolate staggered field to cell-centered z locations."""
    assert 'zstag' in ds[field].dims, 'Expected staggered field'
    assert 'z' not in ds[field].dims, 'Should not have both z and zstag'

    da = xr.DataArray(
        0.5*(  ds[field].isel(zstag=slice(0,  -1)).values
             + ds[field].isel(zstag=slice(1,None)).values),
        coords={'t': ds.coords['t'],
                'z': ds.coords['z'].values},
        dims=('t','z')
    )
    return da
