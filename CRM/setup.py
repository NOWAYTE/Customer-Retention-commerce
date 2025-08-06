# CRM/setup.py

from setuptools import setup, find_packages

setup(
    name="crm_app",
    version="0.1",
    packages=find_packages(include=["app", "app.*"]),
)

