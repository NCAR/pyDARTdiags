from setuptools import setup, find_packages

setup(
    name="pydartdiags",
    version="0.5.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "pydartdiags": ["obs_sequence/composite_types.yaml"],
    },
    author="Helen Kershaw",
    author_email="hkershaw@ucar.edu",
    description="Observation Sequence Diagnostics for DART",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NCAR/pyDARTdiags.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.2.0",
        "numpy>=1.26",
        "plotly>=5.22.0",
        "pyyaml>=6.0.2",
        "matplotlib>=3.9.4"
    ],
)
