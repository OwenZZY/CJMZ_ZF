NIL = -1

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

class ArcSet:
    """Forcing arc set with P1 guarantees (spec §8 row for A; §9).

    Storage: in_arc[v] (predecessor or -1), out_arc[v] (successor or -1).
    Invariant: in/out-degree <= 1 for every vertex (asserted at every mutation
    boundary); arcs always follow edges of G. reverse() swaps the two arrays —
    there is NO orientation flag: after a reversal the swapped arrays ARE the
    arc set (the driver only ever needs the current orientation; decision
    2026-08-23).
    """

    def __init__(self, n: int) -> None:
        """Empty arc set over n vertices."""
        self.n = n
        self.out_arc = [NIL] * n          # this is A
        self.in_arc = [NIL] * n      # this is A_rev
        self._count = 0

    def add(self, u: int, v: int) -> None:
        """Add arc u -> v; assert P1: in_arc[v] = d= -1 and out_arc[u] == -1."""
        assert self.in_arc[v] == -1 and self.out_arc[u] == -1, (
            f"P1 violation: arc ({u}, {v}) would give in/out-degree > 1"
        )
        self._count += 1
        self.out_arc[u] = v
        self.in_arc[v] = u

    def reverse(self) -> None:
        """Reverse all arcs: swap the in_arc/out_arc references in O(1)"""
        self.out_arc, self.in_arc = self.in_arc, self.out_arc

    def delete_heads(self, head_mask: bytearray) -> None:
        """Delete every arc whose head lies in head_mask;
        that is, if v in head_mask, then remove (u, v) in A, where u = in_arc[v].
        O(|head_mask|) deletions."""
        for v, bit in enumerate(head_mask):  # v is a head
            if not bit:
                continue
            u = self.in_arc[v]
            if u != NIL:
                assert self.out_arc[u] == v # suggested assertion, for impossible broken structure
                self.out_arc[u] = NIL  # remove (u, v) in A
                self.in_arc[v] = NIL  # remove (v, u) in A
                self._count -= 1

    def __len__(self) -> int:
        """Number of arcs (orientation-independent)."""
        return self._count

    def extend(self, other: "ArcSet") -> None:
        """Merge `other` into this arc set; assert no P1 conflict."""
        raise NotImplementedError("interface skeleton — implementation pending")

    def sources(self, mask: Optional[bytearray] = None) -> bytearray:
        """Mask of vertices with in-degree 0 under the current orientation,
        restricted to the vertex set given by mask (default: all n vertices).
        (In the driver's usage all arcs lie inside the restricted set.)"""
        raise NotImplementedError("interface skeleton — implementation pending")

    def sinks(self, mask: Optional[bytearray] = None) -> bytearray:
        """Mask of vertices with out-degree 0 under the current orientation,
        restricted to the vertex set given by mask (default: all n vertices)."""
        raise NotImplementedError("interface skeleton — implementation pending")

    def arcs(self) -> list[tuple[int, int]]:
        """All arcs in the current orientation, as (tail, head) pairs."""
        raise NotImplementedError("interface skeleton — implementation pending")