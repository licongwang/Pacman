from setuptools import setup, find_packages
import re

def get_property(prop, project):
    result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), open(project + '/__init__.py').read())
    return result.group(1)

setup(
    name='pacman',
    version=get_property('__version__', 'pacman'),
    description='pacman game simulator',
    author='licong',
    url='',
    license='',
    packages=find_packages(),
    package_data={},
    install_requires=[
        'numpy'
    ]
)

