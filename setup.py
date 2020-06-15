#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["pyyaml>=5.1",
                "coloredlogs",
                "six",
                'esm_calendar @ git+https://github.com/esm-tools/esm_calendar.git',
                'esm_rcfile @ git+https://github.com/esm-tools/esm_rcfile.git' ]

setup_requirements = [ ]

test_requirements = [ ]


# esm_calendar
# dependency_links=['https://gitlab.awi.de/esm_tools/esm_calendar.git']


setup(
    author="Paul Gierz",
    author_email='paul.gierz@awi.de',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="ESM Parser for clever parsing of yaml files",
    install_requires=requirements,
    license="GNU General Public License v2",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='esm_parser',
    name='esm_parser',
    packages=find_packages(include=['esm_parser', 'esm_parser.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.awi.de/esm_tools/esm_parser',
    version="4.1.0",
    zip_safe=False,
)
