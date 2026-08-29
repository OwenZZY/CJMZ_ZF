"""L3 driver — Algorithm 4.2 main loop (zf_npd).

zf-npd: zero forcing via nice path decomposition.

Implementation of Algorithm 4.2 from *An approximation algorithm for zero
forcing* (Cameron-Janssen-Mathew-Zhang, arXiv:2402.08866v1): a deterministic
(pw(G)+1)-approximation of the zero forcing number.

Design record: docs/zf_npd_step_order.md (step order, traps T1-T6).
Interface contracts: docs/HANDOFF.md.

Class contracts in use:
  - Graph:      n, induced_subgraph, N, deg
  - NicePD:     k, mask_of(i), op(i)    (op(i) = transition X_i -> X_{i+1})
  - ArcSet:     extend, reverse, delete_heads, sources
  - zf_closure: closure(g, blue, host=None) -> (W: bytearray, A: ArcSet)

Conventions:
  - Masks are bytes/bytearray of length n, one byte per vertex, 0/1.
    CPython bytearrays have no |/&/~ between masks — use _mask_or.
  - S is never materialized in the loop; a single sources() at the end.

A_keep invariant (per segment): after each scan step z with W empty
(evaluated or skipped), A_keep is a FAS of G(t,z) whose sources are
X_t ∪ X_z. At an exit with W ≠ ∅ (always a forget step), A_keep is
exactly FAS(X_t ∪ X_{z-1}, G(t,z)) — the L6c object — so no closure
call is ever repeated, including in the final L7a branch.
"""

from __future__ import annotations

from .zf_arcset import ArcSet
from .zf_closure import closure


def _mask_or(dst: bytearray, src) -> None:
    """Union in place: dst[v] = 1 wherever src[v] == 1."""
    for i, b in enumerate(src):
        if b:
            dst[i] = 1


def _unpack(mask: bytearray) -> list[int]:
    """Vertices with bit set, ascending — output form of a mask."""
    return [v for v, bit in enumerate(mask) if bit]


def zf_npd(g, npd) -> tuple[list[int], list[list[int]]]:
    """Algorithm 4.2 driver: (pw(G)+1)-approximate zero forcing set.

    Preconditions: npd is a validated nice path decomposition of g, and
    both describe the same vertex-name space (g.shift_by == npd.shift_by;
    the driver raises ValueError otherwise).
    Returns: (S, F) — S a zero forcing set as a list of vertex NAMES
    (ascending, id + g.shift_by); F a list of forts, each a list of vertex
    names (ascending), forming a fort packing, with |S| <= (npd.width+1)|F|.

    Edge case: Graph infers shift_by as the minimum adjacency entry, so an
    edgeless graph gets shift_by = 0 and its outputs are ids; the caller
    owns the name mapping in that case.
    """
    if g.shift_by != npd.shift_by:       # input precondition: same name space
        raise ValueError(
            f"g.shift_by ({g.shift_by}) != npd.shift_by ({npd.shift_by}); "
            "construct NicePD with shift_by=g.shift_by"
        )
    A = ArcSet(g.n)                      # L1
    F = []                               # L1
    t = 0                                # L1

    while True:                          # segment (L2)
        Xt = npd.mask_of(t)              # frozen bytes mask of X_t
        host = bytearray(Xt)             # running union X_t^z (grows only, T4)
        Xz = bytearray(Xt)               # current bag X_z
        W = bytearray(g.n)               # empty mask
        z = t
        A_keep = ArcSet(g.n)             # FAS of G(t,t) with sources X_t

        while not any(W) and z <= npd.k:  # L3: body increments FIRST, so the
            z += 1                        # last evaluated bag is z = k+1 (T1)
            v, is_insert = npd.op(z - 1)  # op(i) = transition X_i -> X_{i+1}
            if is_insert:
                host[v] = 1              # union grows (T4)
                Xz[v] = 1
                continue                 # W provably empty; A_keep unchanged
            Xz[v] = 0                    # forget: only the bag shrinks (T4)
            blue = bytearray(Xt)         # recompute every step (T3)
            _mask_or(blue, Xz)           # blue = X_t ∪ X_z
            W, A_step = closure(g, blue, host)
            if not any(W):
                A_keep = A_step          # last good FAS of G(t,z)

        A.reverse()                      # L4
        if any(W):                       # L6: exit was a forget with W ≠ ∅
            F.append(_unpack(W))         # L6a: id form internally; names at L8
            A.extend(A_keep)             # L6c: A_keep = FAS(X_t ∪ X_{z-1}, G(t,z))
            A.delete_heads(Xz)           # L6d: exactly the heads in X_z (T2)
            t = z                        # L6e
            continue
        # L7: z = k+1, W = ∅
        A.extend(A_keep)                 # L7a: A_keep = FAS(X_t, G(t,k+1))
        # L5 once, then L8 — outputs in the graph's NAME space (id + shift_by)
        shift = g.shift_by
        return ([v + shift for v in _unpack(A.sources())],
                [[v + shift for v in fort] for fort in F])
