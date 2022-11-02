from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in service/__init__.py
from service import __version__ as version

setup(
	name="service",
	version=version,
	description="Service Module",
	author="thirvusoft@gmail.com",
	author_email="thirvusoft@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
