from setuptools import setup, find_packages

setup(
    name="smartfoodscan",
    version="0.1.0",
    description="",
    long_description=open("README.md").read(),
    author="",
    author_email="",
    url="",
    packages=find_packages(where="src"),
    license="",
    package_dir={"": "src"},
    install_requires = open("requirements.txt").read().splitlines()
)
