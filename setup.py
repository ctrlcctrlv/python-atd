from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='python-atd',
      version='0.2',
      description='Unix `at` scheduler, for Python 3 and Python 2. Supports atq, atd, & atrm',
      keywords='atq atrm atd at',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/ctrlcctrlv/python-atd',
      author='Fredrick Brennan',
      author_email='copypaste@kittens.ph',
      license='MIT',
      packages=['atd'],
      test_suite='nose.collector',
      tests_require=['nose'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      package_dir={"":"."},
      zip_safe=False)
