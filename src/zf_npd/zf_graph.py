from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class Graph:
    """Frozen input graph (spec §9).

    Attributes:
        n: number of vertices; vertices are ints 0..n-1.
        adj: tuple-of-tuples adjacency; adj[u] is the ascending tuple of
            neighbours of u (sorted -> deterministic iteration order).
        edge_set: frozenset of int-encoded edges u*n+v with u<v; O(1) edge
            membership for validation/assertions only (never the hot path).
    """

    n: int
    adj: tuple[tuple[int, ...], ...]
    edge_set: frozenset[int]

