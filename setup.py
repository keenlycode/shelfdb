from setuptools import setup, find_packages


setup(
    name='shelfdb',
    version='0.6.7',
    description='Python dictionary database with asyncio server',
    long_description='Python dictionary database with asyncio server',
    url='https://github.com/nitipit/shelfdb',
    author='Nitipit Nontasuwan',
    author_email='nitipit@gmail.com',
    license='MIT',
    classifiers=['Programming Language :: Python :: 3.7'],
    python_requires='>=3.7',
    keywords='dict json database',
    packages=find_packages(),
    install_requires=[
        'dill>=0.3.3',
        'uvloop==0.14.0;platform_system=="Linux"'
    ],
    tests_require=['shelfquery', 'dictify'],
    entry_points={'console_scripts': ['shelfdb=shelfdb.server:main']},
)
