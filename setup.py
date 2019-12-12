import os.path

from setuptools import setup, find_packages

with open(
    os.path.join(os.path.dirname(__file__), 'README.rst')
) as f:
    DESCRIPTION = f.read()

setup(
    name='harness',
    version='0.1.0rc2',
    description='Language-agnostic microservices boilerplate as a code',
    long_description=DESCRIPTION,
    long_description_content_type='text/x-rst',
    author='Vladimir Magamedov',
    author_email='vladimir@magamedov.com',
    url='https://github.com/vmagamedov/harness',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    license='BSD-3-Clause',
    python_requires='>=3.7',
    install_requires=['protobuf'],
    entry_points={
        'console_scripts': [
            'protoc-gen-python_harness=harness.cli.generate:main',
            'harness=harness.cli.run:main',
        ],
        'harness.wires': [
            'python/asyncpg.v1=harness.resources.asyncpg.v1',
            'python/grpclib.v1=harness.resources.grpclib.v1',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
