from distutils.core import setup
import os


with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as file:
    requirements = file.readlines()


setup(
    name='astrohud',
    version='0.5.1',
    description='Get astrology horoscopes',
    author='Zoe Krueger',
    author_email='zoe@zkrueger.com',
    packages=['astrohud'],
    requires=requirements,
)
