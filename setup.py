from setuptools import setup, find_packages


setup(
    name='shelfdb',
    version='0.1.4-dev',
    description='Python dict/json DB, Done right for Efficiency and Simplicity',
    url='https://github.com/nitipit/shelfdb',
    author='Nitipit Nontasuwan',
    author_email='nitipit@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
    keywords='dict json database',
    packages=find_packages(),
    install_requires=['dill',],
)
