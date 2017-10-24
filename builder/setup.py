from setuptools import setup, find_packages

setup(
    name='builder',
    version='0.1.0',
    description='it builds containers',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'docker',
        'pyyaml'
    ]
)
