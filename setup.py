import os
from setuptools import find_packages, setup

readme_name = os.path.join(os.path.dirname(__file__), 'README.md')

with open(readme_name, 'r', encoding='utf-8') as readme:
    long_description = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='celery-progress',
    version='0.5',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Drop in, configurable, dependency-free progress bars for your Django/Celery applications.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/czue/celery-progress',
    author='Cory Zue',
    author_email='cory@coryzue.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
        'Framework :: Django :: 6.0',
        'Framework :: Django :: 6.1',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    extras_require={
        'websockets': ['channels'],
        'redis': ['channels_redis'],
        'rabbitmq': ['channels_rabbitmq']
    }
)
