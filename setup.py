from setuptools import find_packages, setup


setup(
    name='robot',
    version='1.0.0',
    description='an API to interface with the SourceBots robot daemon',
    url='https://github.com/sourcebots/robot-api',
    author='SourceBots',
    license='MIT',
    install_requires=['pyserial'],
    dependency_links=['git+ssh://git@github.com/sourcebots/robotd.git#egg=robotd'],
    tests_require=['cffi', 'nose'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    test_suite='nose.collector',
)
