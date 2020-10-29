import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="StrDiffSynch",
    version="1.0.0",
    author="Antas",
    author_email="",
    description="One of two strings can change into the other when absorbing the difference among them. Vice versa.",
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
