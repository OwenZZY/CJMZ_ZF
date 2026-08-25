"""L3 driver — Algorithm 4.2 main loop.

zf-npd: zero forcing via nice path decomposition.

Clean reimplementation (refactor of github.com/OwenZZY/CJMZ_ZF) of Algorithm 4.2
from *An approximation algorithm for zero forcing*
(Cameron-Janssen-Mathew-Zhang, arXiv:2402.08866): a deterministic
(pw(G)+1)-approximation of the zero forcing number, O(nm) time.

STATUS: INTERFACE SKELETON (design artifact, step 1 of the approved workflow).
Signatures, docstrings and complexity promises follow spec §9 of
zf-npd-summary.md. Bodies raise NotImplementedError until implementation is
authorized (step 3). Nothing here is implementation logic.

Layers (spec §9):
  L1  build_graph()  — construct and freeze the input
  L2  Graph, ArcSet, white(), fas()  — stateless primitives, bag-agnostic
  L3  zf_npd()       — Algorithm 4.2 main loop (this module)

Conventions (spec §9, "boundary conventions"):
  - All inputs frozen; the only mutable object crossing calls is ArcSet.
  - Universal vertex-set exchange format: bytearray mask of length n (0/1).
  - Inactive vertices are invisible in white()/fas() (spec §6 item 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


def zf_npd(g: "Graph", npd: "NicePD") -> tuple[bytearray, list[bytearray]]:
    """Algorithm 4.2 driver: (pw(G)+1)-approximate zero forcing set (L3).

    Preconditions: npd is a validated nice path decomposition of g.
    Returns: (S, F) — S the mask of a zero forcing set, F a list of fort masks
    forming a fort packing, with |S| <= (npd.width + 1)|F|.
    Complexity: O(nm) total (spec §4).
    """
    raise NotImplementedError("interface skeleton — implementation pending")
