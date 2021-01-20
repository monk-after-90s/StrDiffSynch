import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="StrDiffSynch",
    version="2.2.5",
    author="Antas",
    author_email="",
    description=
    "This module calculates the difference from one string to another. If the origin string absorbs the difference, it"
    "becomes the other string."
    "Thus, two endpoints could synchronize the strings by passing the difference.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/monk-after-90s/StrDiffSynch.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
