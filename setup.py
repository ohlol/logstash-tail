#!/usr/bin/env python

from setuptools import setup, find_packages

version = "0.0.3"

setup(
    name="logstash-tail",
    url="http://github.com/ohlol/logstash-tail",
    version=version,
    description="Tail logstash tcp output",
    long_description="Tail logstash tcp output",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Topic :: System :: Networking :: Monitoring"
    ],
    keywords="",
    author="Scott Smith",
    author_email="scott@ohlol.net",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["colorama"],
    scripts=["bin/logstash-tail"]
)
