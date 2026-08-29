"""zf_npd — zero forcing via nice path decomposition.

Package re-exports of the public API. One import line for all callers:

    from zf_npd import Graph, NicePD, zf_npd

Modules:
    zf_graph.Graph      graph with dual adjacency storage
    nice_pd.NicePD      validated nice path decomposition
    zf_arcset.ArcSet    forcing arc set (P1 functional orientation)
    zf_closure.closure  colour-change closure -> (W, A)
    zf_npd.zf_npd       Algorithm 4.2 driver -> (S, F)
"""

from .zf_arcset import ArcSet
from .zf_graph import Graph
from .nice_pd import NicePD
from .zf_closure import closure
from .zf_npd import zf_npd

__all__ = ["Graph", "NicePD", "ArcSet", "closure", "zf_npd"]
