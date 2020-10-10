import os
from setuptools import find_packages, setup

from glob import glob

readme_name = os.path.join(os.path.dirname(__file__), 'README.md')

with open(readme_name, 'r') as readme:
    long_description = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='celery-progress',
    version='0.0.13',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Drop in, configurable, dependency-free progress bars for your Django/Celery applications.',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
    data_files=[
        ('static/celery_progress', glob('celery_progress/static/celery_progress/*', recursive=True)),
    ],
    extras_require={
        'websockets': ['channels'],
        'redis': ['channels_redis'],
        'rabbitmq': ['channels_rabbitmq']
    }
)
