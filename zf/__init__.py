"""zf — zero forcing approximation via nice path decompositions.

Implementation of the algorithm of Cameron-Janssen-Mathew-Zhang,
"An approximation algorithm for zero forcing", arXiv:2402.08866v1.
See SPEC-v1.md for the interface contract and docs/definitions.md for
the mathematical definitions.
"""

from .graph import Graph
from .arcs import Arcs
from .decomposition import NicePathDecomposition
from .closure import closure
from .algorithm import zero_forcing_set, ZFResult

__all__ = [
    "Graph",
    "Arcs",
    "NicePathDecomposition",
    "closure",
    "zero_forcing_set",
    "ZFResult",
]

__version__ = "0.1.0"