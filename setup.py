from setuptools import setup, find_packages

setup(
    name='sky_main',
    version='1.0',
    packages=['app'],
    zip_safe=False,
    install_requires=[
        'Flask',
    ]
)