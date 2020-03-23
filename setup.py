from setuptools import setup, find_packages


setup(
    name='shelfdb',
    version='0.6.0',
    description='Python dict/json DB, Done right for Efficiency and Simplicity',
    long_description='Python dict/json DB `done right` to make your job done',
    url='https://github.com/nitipit/shelfdb',
    author='Nitipit Nontasuwan',
    author_email='nitipit@gmail.com',
    license='MIT',
    classifiers=['Programming Language :: Python :: 3.6'],
    python_requires='>=3.6',
    keywords='dict json database',
    packages=find_packages(),
    install_requires=['uvloop>=0.12.1', 'dill>=0.2.9'],
    tests_require=['shelfquery'],
    entry_points={'console_scripts': ['shelfdb=shelfdb.server:main']},
)
