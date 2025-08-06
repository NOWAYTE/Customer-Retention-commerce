from setuptools import setup, find_packages

setup(
    name="crm_app",
    version="0.1",
    packages=find_packages(),  # Remove include restriction
    include_package_data=True,  # Add this line
)
