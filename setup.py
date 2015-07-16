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
