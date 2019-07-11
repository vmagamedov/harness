from setuptools import setup, find_packages

setup(
    name='harness',
    version='0.0.0rc1',
    description='Runner',
    author='Vladimir Magamedov',
    author_email='vladimir@magamedov.com',
    url='https://github.com/vmagamedov/harness',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    license='BSD-3-Clause',
    python_requires='>=3.6',
    install_requires=[
        'protobuf',
        'dataclasses;python_version<"3.7"',
    ],
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
)
