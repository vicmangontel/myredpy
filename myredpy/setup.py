
from setuptools import setup, find_packages
from myredpy.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='myredpy',
    version=VERSION,
    description='CLI app to interact with Redmine API',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Victor Gonzalez',
    author_email='victor.gontel@gmail.com',
    url='https://github.com/chevito/myredpy/',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'myredpy': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        myredpy = myredpy.main:main
    """,
)
