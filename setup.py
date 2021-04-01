"""
Setup file for easy installation of gpiocmd.
"""

from setuptools import setup

setup(
    name = 'gpiocmd',
    version = '0.9.0',
    description = 'Run arbitrary commands when GPIO buttons are pressed on Raspberry PI.',
    url = 'https://github.com/aheimsbakk/gpiocmd',
    author = 'Arnulf Heimsbakk',
    author_email = 'arnulf.heimsbakk@gmail.com',
    license = 'BSD 3-Clause License',
    scripts = ['scripts/gpiocmd'],
    data_files = [('share/doc/gpiocmd/examples', ['examples/gpiocmd-config-adafruit.yml']),
                  ('share/doc/gpiocmd/examples', ['examples/gpiocmd-config-example.yml']),
                  ('share/doc/gpiocmd', ['README.md']),
                  ],
    install_requires=['pyyaml~=5.4',
                      'RPi.GPIO~=0.7',
                      ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License'
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
    ],
)
