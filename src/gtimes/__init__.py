"""GTimes - High-precision GPS time conversion and processing library."""

__version__ = "0.4.1"
__author__ = "Benedikt Gunnar Ófeigsson"
__email__ = "bgo@vedur.is"

# Import key functions for easy access
from .timefunc import parse_datetime_flexible

# Make functions available at package level
__all__ = ['parse_datetime_flexible']

# __import__('pkg_resources').declare_namespace(__name__)
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
