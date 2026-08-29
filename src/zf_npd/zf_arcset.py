"""Forcing arc set A for the zf_npd driver (Algorithm 4.2).

Interface contract: docs/HANDOFF.md ("zf_arcset.py — ArcSet").
Driver call sites: L4 / L6c / L6d / L7a / L8 in docs/zf_npd_step_order.md.
"""

from __future__ import annotations

from typing import Optional

NIL = -1


class ArcSet:
    """Partial functional orientation of G: every vertex has in-degree and
    out-degree at most 1 (property P1), asserted at every mutation boundary.

    This is the forcing arc set A of Algorithm 4.2: built empty, grown by
    extend(), flipped by reverse(), pruned by delete_heads(), read by
    sources()/sinks()/arcs().

    Storage
    -------
    out_arc[u]  successor of u: == v iff arc u -> v is present, else NIL
    in_arc[v]   predecessor of v: == u iff arc u -> v is present, else NIL
    _count      |A|; maintained by add/delete_heads, never touched by reverse

    Orientation
    -----------
    reverse() swaps the two array references in O(1); there is NO orientation
    flag — after the swap the arrays ARE the arc set in the new orientation
    (project decision 2026-08-23).
    """

    def __init__(self, n: int) -> None:
        """Empty arc set over vertices 0..n-1. O(n)."""
        self.n = n
        self.out_arc = [NIL] * n          # successor array (current orientation)
        self.in_arc = [NIL] * n           # predecessor array (same arcs)
        self._count = 0

    def add(self, u: int, v: int) -> None:
        """Add arc u -> v. O(1).

        Guards (all fail loud): 0 <= u, v < n; u != v; and P1 —
        in_arc[v] and out_arc[u] are both NIL. P1 is enforced here and only
        here, so extend() inherits it for free.

        Usage: closure (one arc per forcing step) and extend().
        """
        assert 0 <= u < self.n and 0 <= v < self.n, (
            f"vertex id out of range [0, {self.n}): ({u}, {v})"
        )
        assert u != v, f"self-loop arc ({u}, {u}) not allowed (G is simple)"
        assert self.in_arc[v] == NIL and self.out_arc[u] == NIL, (
            f"P1 violation: arc ({u}, {v}) would give in/out-degree > 1"
        )
        self._count += 1
        self.out_arc[u] = v
        self.in_arc[v] = u

    def reverse(self) -> None:
        """Flip every arc's orientation in O(1) by swapping the two arrays.

        _count is untouched: size is orientation-independent.

        Usage: driver step L4, once per segment. The paper flips A here so
        the next segment's forcing arcs extend it consistently; after the
        following delete_heads(X_z) (L6d) no X_z vertex has an in-arc, so
        X_z is the source bag of the next segment (trap T2).
        """
        self.out_arc, self.in_arc = self.in_arc, self.out_arc

    def delete_heads(self, head_mask: bytearray) -> None:
        """Delete exactly the arcs whose head lies in head_mask.

        O(n) scan; removal work is O(#heads).

        Usage: driver step L6d with head_mask = X_z (the current bag).
        Reason (trap T2): after reverse(), every vertex of X_z must become a
        source for the next segment — deleting less leaves an in-arc, deleting
        more changes Sources(A) and breaks the size analysis. Faithful
        execution only.
        """
        assert len(head_mask) == self.n, (
            f"head_mask must have length {self.n}, got {len(head_mask)}"
        )
        for v, bit in enumerate(head_mask):
            if not bit:
                continue
            u = self.in_arc[v]            # unique predecessor (P1), or NIL
            if u != NIL:
                assert self.out_arc[u] == v, (
                    "inconsistent structure: out_arc[in_arc[v]] != v"
                )
                self.out_arc[u] = NIL     # remove u -> v ...
                self.in_arc[v] = NIL      # ... in both arrays
                self._count -= 1

    def __len__(self) -> int:
        """|A| in the current orientation (same after reverse()). O(1)."""
        return self._count

    def extend(self, other: "ArcSet") -> None:
        """Union other into self; a P1 conflict raises AssertionError.

        Iterates other.arcs() — ascending by tail, per the determinism
        convention — and routes every arc through add(), so P1 and _count
        stay consistent in exactly one place. Self-union is a no-op.

        Usage: driver L6c / L7a — merge the fresh forcing arc set returned by
        zf_closure.closure (module-level function) into the running A. O(n).
        """
        if other is self:
            return                      # A ∪ A = A; would trip P1 otherwise
        assert other.n == self.n, (
            f"cannot merge ArcSet over {other.n} vertices into one over {self.n}"
        )
        for u, v in other.arcs():
            self.add(u, v)

    def sources(self, mask: Optional[bytearray] = None) -> bytearray:
        """Mask of in-degree-0 vertices (no in-arc) in the current orientation.

        `mask` only filters the output; the degree test is on the FULL
        orientation (reading (a) — in the driver all arcs already lie inside
        the restricted set, and the driver calls without a mask anyway).

        Usage: driver L8 — the single Sources(A) call at the very end; S is
        the returned zero-forcing set. O(n).
        """
        return self._nil_vertices(self.in_arc, mask)

    def sinks(self, mask: Optional[bytearray] = None) -> bytearray:
        """Mask of out-degree-0 vertices (no out-arc) in the current orientation.

        Same restriction semantics as sources(). Not used by the driver;
        contract member kept for inspection.
        """
        return self._nil_vertices(self.out_arc, mask)

    def _nil_vertices(self, arr: list[int],
                      mask: Optional[bytearray]) -> bytearray:
        """Shared body of sources/sinks: mask of v with arr[v] == NIL.

        Pass self.in_arc for sources (no predecessor => in-degree 0) or
        self.out_arc for sinks (no successor => out-degree 0). Output bits
        are additionally gated by `mask` (output filter only, reading (a)).
        """
        res = bytearray(self.n)
        if mask is None:
            for v in range(self.n):
                if arr[v] == NIL:
                    res[v] = 1
        else:
            assert len(mask) == self.n, (
                f"mask must have length {self.n}, got {len(mask)}"
            )
            for v, bit in enumerate(mask):
                if bit and arr[v] == NIL:
                    res[v] = 1
        return res

    def arcs(self) -> list[tuple[int, int]]:
        """All arcs as (tail, head) pairs, ascending by tail. O(n).

        Ascending order is free — a single range(n) scan of out_arc yields
        tails in id order, and P1 guarantees at most one head per tail.

        Usage: extend() (canonical merge order); public contract member for
        inspection.
        """
        return [(u, self.out_arc[u]) for u in range(self.n)
                if self.out_arc[u] != NIL]
