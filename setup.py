import os
from setuptools import find_packages, setup

# convert md to rst for pypi https://stackoverflow.com/a/23265673/8207
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

readme_name = os.path.join(os.path.dirname(__file__), 'README.md')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='celery-progress',
    version='0.0.7',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Drop in, configurable, dependency-free progress bars for your Django/Celery applications.',
    long_description=read_md(readme_name),
    url='https://github.com/czue/celery-progress',
    author='Cory Zue',
    author_email='cory@coryzue.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    extras_require={
        'websockets': ['channels'],
        'redis': ['channels_redis'],
        'rabbitmq': ['channels_rabbitmq']
    }
)
