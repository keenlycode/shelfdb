from setuptools import setup, find_packages


setup(
    name='shelfdb',
    version='0.1.0',
    description='JSON Python DB store as files for simplicity,' +
        'based on Python built-in `shelve`, inspired by RethinkDB API',
    url='https://github.com/nitipit/shelfdb',
    author='Nitipit Nontasuwan',
    author_email='nitipit@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.5',
    ],
    keywords='JSON Database',
    packages=find_packages(),
)
