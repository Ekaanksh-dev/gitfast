from setuptools import setup, find_packages

setup(
    name="gitblaze",
    version="1.0.0",
    description="42 git shortcuts + auto merge conflict resolver — zero AI, pure Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ekaanksh Patil",
    author_email="pekanksh@gmail.com",
    url="https://github.com/Ekaanksh-dev/gitfast",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "gitfast=gitfast.cli:main",
            "ghelp=gitfast.cli:help_cmd",
            "gmerge=gitfast.merge.resolver:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    keywords="git shortcuts developer-tools merge cli productivity",
)
