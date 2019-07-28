from distutils.core import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='senseo_api',
    version='1.0.0',
    author="Ludovic Rivallain",
    author_email='ludovic.rivallain+senseo -> gmail.com',
    packages=setuptools.find_packages(),
    description="Senseo coffee machine API provide a way to remote control a Senseo Coffee Machine through a GPIO module.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "flask-restplus", # API provider
        "RPi.GPIO",       # GPIO interface
        "coloredlogs",    # fancy logs
        "click",          # only for simulator part
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'senseo-api=senseo_api.__main__:main',
            'senseo-simulator=senseo_api.coffee_simulator:main',
        ],
    })
