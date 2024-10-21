from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("geoprocessing_utils")
except PackageNotFoundError:
    # package is not installed
    pass
