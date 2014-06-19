from setuptools import setup
from os import path
from glob import glob

name = 'pygmaps_ng'
datadir = path.join(name,'gmm-up')
datafiles = [(datadir, [f for f in glob(path.join(datadir, '*'))])]

setup(name=name,
    version='1.0dev',
    author='Elliot Hallmark',
    url='https://github.com/Permafacture/pygmaps-ng/',
    packages=[name],
    install_requires=['beautifulsoup4==4.3.2','brewer2mpl==1.4'],
    data_files= datafiles
    )
