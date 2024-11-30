from distutils.core import setup
import os


with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as file:
    requirements = file.readlines()

print(requirements)
setup(
    name='astrohud',
    version='0.6.0',
    description='Get and chart astral data',
    author='Zoe Krueger',
    author_email='astrohud@zkrueger.com',
    packages=['astrohud'],
    install_requires=requirements,
)
