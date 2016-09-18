from setuptools import setup, find_packages
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = '0.0.1'
AUTHOR = 'Binyamin Sharet'
EMAIL = 's.binyamin@gmail.com'
URL = 'https://github.com/BinyaminSharet/pyeiotcloud'
DESCRIPTION = read('README.rst')
KEYWORDS = 'eiot'

setup(
    name='pyeiotcloud',
    version=VERSION,
    description='EasyIoT Clout python API',
    long_description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(),
    install_requires=['docopt'],
    keywords=KEYWORDS,
    entry_points={},
    package_data={}
)
