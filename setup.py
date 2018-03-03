from setuptools import setup, find_packages
from robot import __VERSION__

setup(
    name='robot',
    version=__VERSION__,
    description='an API to interface with the SourceBots robot daemon',
    url='https://github.com/sourcebots/robot-api',
    author='SourceBots',
    license='MIT',
    install_requires=[],
    dependency_links=[],
    tests_require=["robotd", "sb-vision"],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
