from setuptools import setup, find_packages

setup(
    name="anti-preempter",
    packages=find_packages(where='.'),
    include_package_data=True,
    package_dir={'': '.'}
)
