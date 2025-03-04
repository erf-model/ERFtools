# This setup file is based on https://github.com/a2e-mmc/mmctools/blob/master/setup.py
# accessed on April 3, 2020.

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'erftools'
DESCRIPTION = 'Scripts to make life easier for users of the Energy Research & Forecasting model'
URL = 'https://github.com/erf-model/erftools'
EMAIL = 'eliot.quon@nrel.gov'
AUTHOR = 'U.S. Department of Energy'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.1'

# What packages are required for this module to be executed?
REQUIRED = [
    # core
    'numpy>=1.18.1',
    'pandas>=1.0.1',
    'xarray>=0.15.0',
    'netcdf4>=1.5.1',
    'pydantic',
    'f90nml',
    'cartopy',
    #'matplotlib>=3',
    #'scipy>=1.4.1',
    #'dask>=2.10.1',
    #'utm>=0.5.0',
]

EXTRAS = {
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    #packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    py_modules=[NAME],
    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='Apache-2.0',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
    ],
    # $ setup.py publish support.
    #cmdclass={
    #    'upload': UploadCommand,
    #},
)
