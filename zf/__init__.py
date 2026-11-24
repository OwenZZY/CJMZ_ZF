"""zf — zero forcing approximation via nice path decompositions.

Implementation of the algorithm of Cameron-Janssen-Mathew-Zhang,
"An approximation algorithm for zero forcing", arXiv:2402.08866v1.

One interface with the outside: zf_via_path_decomp(graph, bags), where
graph is a networkx.Graph (its nodes are the vertex names) and bags is
a list of sets of names forming a path decomposition (not necessarily
nice; checked by the layer, which halts with ValueError if not).
Returns a names-based ZFResult (zf_set, forts, arcs). The translation
layer lives in zf/api.py; the index-based core is internal
(importable from its submodules, not exported here).
See SPEC-v1.md for the contract and docs/definitions.md for the math.
"""

from .api import zf_via_path_decomp

__all__ = ["zf_via_path_decomp"]

__version__ = "0.3.0"