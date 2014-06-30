from distutils.core import setup
from os import path
from glob import glob

name = 'pygmaps_ng'
datadir = path.join(name,'gmmup')
packagefiles = [path.join('gmmup',path.basename(f)) for f in glob(path.join(datadir,'*'))]

print({'%s.gmmup'%name:packagefiles})
setup(name=name,
    version='1.0dev',
    author='Elliot Hallmark',
    url='https://github.com/Permafacture/pygmaps-ng/',
    packages=[name],
    install_requires=['beautifulsoup4==4.3.2','brewer2mpl==1.4','jsmin'],
    #data_files= datafiles,
    package_data = {name:packagefiles}
    )
