from setuptools import setup, find_packages

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(
    name="smartfoodscan",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    install_requires = requirements
)
