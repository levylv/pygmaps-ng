from distutils.core import setup

setup(name='pygmaps_ng',
    version='1.0dev',
    author='Elliot Hallmark',
    url='https://github.com/Permafacture/pygmaps-ng/',
    packages=['pygmaps_ng'],
    data_files=[('gmm-up',
                 ['pygmaps_ng/gmm-up/static.html',
                  'pygmaps_ng/gmm-up/javascripts/main.js',
                  'pygmaps_ng/gmm-up/stylesheets/main.css'])]
    )
