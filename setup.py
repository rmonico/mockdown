from setuptools import setup

setup(name='iTask',
      version='0.3.2',
      description='Creates wireframe mocks converting yaml files to HTML',
      url='https://github.com/rmonico/mockdown',
      author='Rafael Monico',
      author_email='rmonico1@gmail.com',
      license='GPL3',
      packages=['mockdown'],
      entry_points={
          'console_scripts': ['mockdown=mockdown:main'],
      },
      zip_safe=False)
