"""Install AstroHud"""

from setuptools import setup
from setuptools import find_packages
import os


with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as file:
    requirements = file.readlines()


setup(
    name='astrohud',
    version='0.6.1',
    description='Get and chart astral data',
    author='Zoe Krueger',
    author_email='astrohud@zkrueger.com',
    packages=find_packages(exclude=['frontend']),
    package_data={'astrohud': ['LICENSE.md', 'assets/**', 'submodules/**']},
    include_package_data=True,
    install_requires=requirements,
)
