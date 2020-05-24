from setuptools import setup, find_packages
import sys


setup(
    name='shelfdb',
    version='0.6.4',
    description='Python dictionary database with asyncio server',
    long_description='Python dictionary database with asyncio server',
    url='https://github.com/nitipit/shelfdb',
    author='Nitipit Nontasuwan',
    author_email='nitipit@gmail.com',
    license='MIT',
    classifiers=['Programming Language :: Python :: 3.6'],
    python_requires='>=3.6',
    keywords='dict json database',
    packages=find_packages(),
    install_requires=[
        'dill>=0.3.0',
        'uvloop>=0.12.1;platform_system=="Linux"'
    ],
    tests_require=['shelfquery', 'dictify'],
    entry_points={'console_scripts': ['shelfdb=shelfdb.server:main']},
)
