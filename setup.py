from setuptools import setup, find_packages

setup(
    name='robot',
    version='1.0.0',
    description='an API to interface with the SourceBots robot daemon',
    url='https://github.com/sourcebots/robot-api',
    author='SourceBots',
    license='MIT',
    install_requires=[],
    dependency_links=[],
    tests_require=["robotd", "sb-vision"],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
