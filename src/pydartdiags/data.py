"""
Data file utilities for pyDARTdiags examples.

This module provides functions to locate, download,
and cache example files used in pyDARTdiags examples.
The data files are cached in the users home directory
under ~/.pydartdiags/data.

"""

import os
from pathlib import Path
import urllib.request
import zipfile
import shutil

# Zenodo DOI/URL for the data archive
ZENODO_RECORD_ID = "18135062"
ZENODO_RECORD_URL = f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}/files-archive"
ZENODO_DOI = f"https://doi.org/10.5281/zenodo.{ZENODO_RECORD_ID}"


def get_data_cache_dir():
    """Get the cache directory for downloaded data files."""
    cache_dir = Path.home() / ".pydartdiags" / "data"
    return cache_dir


def get_example_data(filename, auto_download=True):
    """
    Get path to a data file, checking multiple locations.

    Searches for data files in the following order:
        1. Development location (../../data from package GitHub repo)
        2. Environment variable PYDARTDIAGS_DATA
        3. User cache directory (~/.pydartdiags/data)
        4. Downloads from Zenodo if auto_download=True

    Parameters
    ----------
    filename : str
        Name of the data file to locate
    auto_download : bool, optional
        If True, automatically download from Zenodo if not found locally.
        Default is True.

    Returns
    -------
    str
        Absolute path to the data file

    Raises
    ------
    FileNotFoundError
        If the file is not found and auto_download=False

    Examples
    --------

    .. code-block:: python

        data_file = get_example_data("obs_seq.final.lorenz_96")

    """
    # 1. Check development location (for contributors/developers)
    try:
        package_dir = Path(__file__).parent.parent.parent
        dev_data = package_dir / "data" / filename
        print(f"package_dir: {package_dir}")
        if dev_data.exists():
            print(f"Using development data file: {dev_data}")
            return str(dev_data)
    except:
        pass

    # 2. Check environment variable
    if "PYDARTDIAGS_DATA" in os.environ:
        env_data = Path(os.environ["PYDARTDIAGS_DATA"]) / filename
        if env_data.exists():
            print(f"Using data file from PYDARTDIAGS_DATA: {env_data}")
            return str(env_data)

    # 3. Check cache directory
    cache_dir = get_data_cache_dir()
    cache_file = cache_dir / filename
    if cache_file.exists():
        print(f"Using cached data file: {cache_file}")
        return str(cache_file)

    # 4. File not found
    if not auto_download:
        raise FileNotFoundError(
            f"Data file '{filename}' not found.\n\n"
            f"To download example data:\n"
            f"  Option 1: Automatic download\n"
            f"    >>> from pydartdiags.data import download_all_data\n"
            f"    >>> download_all_data()\n\n"
            f"  Option 2: Manual download\n"
            f"    Download from: {ZENODO_DOI}\n"
            f"    Extract to: {cache_dir}\n\n"
            f"  Option 3: Set environment variable\n"
            f"    export PYDARTDIAGS_DATA=/path/to/your/data\n"
        )

    # Auto-download
    print(f"Data file '{filename}' not found locally.")
    print("Downloading all example data from Zenodo...")
    download_all_data()

    # Check again after download
    if cache_file.exists():
        return str(cache_file)
    else:
        raise FileNotFoundError(
            f"Downloaded data but '{filename}' still not found. "
            f"Please check {ZENODO_RECORD_URL}"
        )


def download_all_data(force=False):
    """
    Download all example data files from Zenodo.

    Downloads and extracts the complete data archive to the user's
    cache directory (~/.pydartdiags/data).

    Parameters
    ----------
    force : bool, optional
        If True, re-download even if data already exists. Default is False.

    Examples
    --------

    .. code-block:: python

        from pydartdiags.data import download_all_data
        download_all_data()

    """
    cache_dir = get_data_cache_dir()

    if cache_dir.exists() and not force:
        print(f"Data directory already exists: {cache_dir}")
        print("Use force=True to re-download.")
        return

    cache_dir.mkdir(parents=True, exist_ok=True)

    # Download archive
    archive_file = cache_dir.parent / f"{ZENODO_RECORD_ID}.zip"

    print(f"Downloading data from Zenodo ({ZENODO_DOI})...")
    print(f"This may take a few minutes (approx. 85 MB)...")

    try:
        urllib.request.urlretrieve(ZENODO_RECORD_URL, archive_file)
        print(f"Download complete: {archive_file}")

        # Extract archive
        print(f"Extracting to {cache_dir}...")
        with zipfile.ZipFile(archive_file, "r") as zip_ref:
            zip_ref.extractall(path=cache_dir)

        # Clean up archive
        archive_file.unlink()

        print(f"Data successfully installed to {cache_dir}")
        print(f"Found {len(list(cache_dir.glob('*')))} data files")

    except Exception as e:
        print(f"Error downloading data: {e}")
        print(f"\nManual download instructions:")
        print(f"1. Download from: {ZENODO_DOI}")
        print(f"2. Extract to: {cache_dir}")
        raise


def list_available_data():
    """
    List all available data files.

    Returns
    -------
    list of str
        List of available data file names

    Examples
    --------

    .. code-block:: python

        from pydartdiags.data import list_available_data
        files = list_available_data()
        print(files)

    """
    locations = []

    # Check development location
    try:
        package_dir = Path(__file__).parent.parent.parent
        dev_data = package_dir / "data"
        if dev_data.exists():
            locations.append(dev_data)
    except:
        pass

    # Check environment variable
    if "PYDARTDIAGS_DATA" in os.environ:
        env_data = Path(os.environ["PYDARTDIAGS_DATA"])
        if env_data.exists():
            locations.append(env_data)

    # Check cache
    cache_dir = get_data_cache_dir()
    if cache_dir.exists():
        locations.append(cache_dir)

    # Collect all files
    files = set()
    for loc in locations:
        files.update([f.name for f in loc.glob("*") if f.is_file()])

    return sorted(list(files))


def clear_cache():
    """
    Remove all downloaded data from the cache directory.

    Examples
    --------

    .. code-block:: python

        from pydartdiags.data import clear_cache
        clear_cache()

    """
    cache_dir = get_data_cache_dir()
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        print(f"Cleared cache: {cache_dir}")
    else:
        print("Cache directory does not exist.")
