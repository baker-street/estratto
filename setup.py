from setuptools import setup, find_packages

THE_LONG_DESCRIPTION = """
Makes misc files usable for nlp.
"""

PACKAGES = ['gentrify']

setup(
    name='gentrify',
    version='0.1.0',
    description="Makes misc files usable for nlp.",
    long_description=THE_LONG_DESCRIPTION,
    classifiers=['Topic :: NLP',
                 'Topic :: Text cleaning',
                 'Intended Audience :: Developers',
                 'Development Status :: 3 - Alpha',
                 'Programming Language :: Python :: 2.7',
                 'License :: MIT License',
                 ],
    keywords='nlp encoding text plaintext preprocessing',
    author='Steven Cutting',
    author_email='steven.e.cutting@linux.com',
    license='MIT',
    packages=PACKAGES,
    # zip_safe=False,
    install_requires=[
    ],
)

""" for cython
from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

extensions = [Extension('*', ['gentrify/*.pyx'],
                        include_dirs=['gentrify'],
                        # libraries=['gentrify'],
                        # library_dirs=['/home/steven_c/projects/gentrify/gentrify/']
                        )]
setup(name="ellis_island",
      ext_modules=cythonize(extensions),
      )
"""
