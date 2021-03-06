"""
Archan package.

The purpose of this package is to make possible the analysis of a problem
using a DSM (Design Structure Matrix) on which certain criteria will be
verified.
"""

from typing import List

from .dsm import DesignStructureMatrix, DomainMappingMatrix, MultipleDomainMatrix
from .logging import Logger
from .plugins import Argument, Checker, Provider

__all__: List[str] = [
    "DesignStructureMatrix",
    "DomainMappingMatrix",
    "MultipleDomainMatrix",
    "Provider",
    "Checker",
    "Argument",
    "Logger",
]  # noqa: WPS410
__version__ = "3.0.0"  # noqa: WPS410 (the only __variables__ we use)

# TODO: DSM class should have more methods (see wiki DSM, adjacency matrix)
# FIXME: use if not sys.stdin.isatty() to detect stdin input or not
# TODO: update docs with new ignore param on all checkers
# TODO: update docs with new identifier class attributes on every plugin
# TODO: update docs with usage of self.logger in plugins
# TODO: update docs with new YAML format: identifier, name and description
# FIXME: stronger verification method for configuration
