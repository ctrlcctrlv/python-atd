from setuptools import setup

#def readme():
 #   with open('README.rst') as f:
  #      return f.read()

setup(name='python-atd',
      version='0.1',
      description='Unix `at` scheduler in Python 2. Supports atq, atd, & atrm',
      keywords='atq atrm atd at',
      #long_description=readme(),
      url='http://github.com/ctrlcctrlv/python-atd',
      author='Fredrick Brennan',
      author_email='admin@8chan.co',
      license='MIT',
      packages=['atd'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
