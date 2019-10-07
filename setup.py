import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="threatrack_iocextract",
	version="0.0.9",
	author="",
	author_email="",
	description="IOC extractor",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/threatrack/threatrack_iocextract",
	packages=setuptools.find_packages(),
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)

