"""Install AstroHud"""

from setuptools import setup
from setuptools import find_packages
import os
import json


parent_dir = os.path.dirname(__file__)
with open(os.path.join(parent_dir, 'requirements.txt')) as file:
    requirements = file.readlines()
with open(os.path.join(parent_dir, 'frontend/package.json')) as file:
    version = json.load(file)['version']


setup(
    name='astrohud',
    version=version,
    description='Get and chart astral data',
    author='Zoe Krueger',
    author_email='astrohud@zkrueger.com',
    packages=find_packages(exclude=['frontend']),
    package_data={'astrohud': ['LICENSE.md', 'assets/**', 'submodules/**']},
    include_package_data=True,
    install_requires=requirements,
)
