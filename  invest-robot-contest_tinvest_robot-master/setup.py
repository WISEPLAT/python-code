import setuptools
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open("README.md", "r") as fh:
    long_description = fh.read()


def read_requirements():
    reqs_path = os.path.join(__location__, 'requirements.txt')
    with open(reqs_path, encoding='utf8') as f:
        reqs = [line.strip() for line in f if not line.strip().startswith('#')]

    names = []
    for req in reqs:
        names.append(req)
    return {'install_requires': names}


setuptools.setup(
    name="tinvest-robot-perevalov",
    version="0.1.3",
    author="Aleksandr Perevalov",
    author_email="perevalovproduction@gmail.com",
    description="A package that implements a news sentiment based strategy for trading using Tiknoff Invest API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Perevalov/tinvest_robot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    **read_requirements()
)
