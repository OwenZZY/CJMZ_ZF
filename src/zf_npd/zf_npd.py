"""L3 driver — Algorithm 4.2 main loop.

zf-npd: zero forcing via nice path decomposition.

Clean reimplementation (refactor of github.com/OwenZZY/CJMZ_ZF) of Algorithm 4.2
from *An approximation algorithm for zero forcing*
(Cameron-Janssen-Mathew-Zhang, arXiv:2402.08866): a deterministic
(pw(G)+1)-approximation of the zero forcing number, O(nm) time.

STATUS: INTERFACE SKELETON. The authoritative driver design (step order,
host-mask semantics, NicePD.op contract, traps T1-T5) lives in
docs/zf_npd_step_order.md; implement that file literally. Bodies raise
NotImplementedError until implementation is authorized. Nothing here is
implementation logic.

Layers (spec §9):
  L1  build_graph()  — construct and freeze the input
  L2  Graph, ArcSet, white(), fas()  — stateless primitives, bag-agnostic
  L3  zf_npd()       — Algorithm 4.2 main loop (this module)

Conventions (docs/zf_npd_step_order.md):
  - All inputs frozen; the only mutable object crossing calls is ArcSet.
  - Universal vertex-set exchange format: bytearray mask of length n (0/1).
  - host = mask of X_t^z, monotone within a segment (T4); G(t,z) never
    materialized; white()/fas() see only host vertices.
  - S is never materialized in the loop; single sources() at the end.

Authoritative loop (L1..L8, see docs/zf_npd_step_order.md):

    closure = zf_closure(g.adj)
    A = ArcSet(g.n); F = []; t = 0
    while True:
        Xt = npd.mask_of(t)
        host = bytearray(Xt); bag = bytearray(Xt)
        W = bytearray(g.n); z = t
        while not any(W) and z <= npd.k:          # L3; must evaluate z=k+1 (T1)
            z += 1
            v, is_ins = npd.op(z)
            if is_ins:
                host[v] = 1; bag[v] = 1; continue # White() provably empty
            bag[v] = 0                            # host unchanged (T4)
            blue = bytearray(Xt); _mask_or(blue, bag)   # recompute (T3)
            W = closure.white(blue, host)
        A.reverse()                               # L4
        if any(W):                                # L6
            F.append(W)
            blue[v] = 1                           # L6c: X_t U X_{z-1} (T5)
            A.extend(closure.fas(blue, host))
            A.delete_heads(bag)                   # L6d (T2)
            t = z; continue
        A.extend(closure.fas(bytearray(Xt), host)) # L7a (z=k+1)
        return A.sources(), F                     # L5 once, L8
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from zf_graph import Graph
from zf_npd.nice_pd import NicePD
from zf_npd.zf_arcset import ArcSet
from zf_npd.zf_closure import zf_closure


def zf_npd(g: Graph, npd: NicePD) -> tuple[bytearray, list[bytearray]]:
    """Algorithm 4.2 driver: (pw(G)+1)-approximate zero forcing set (L3).

    Preconditions: npd is a validated nice path decomposition of g.
    Returns: (S, F) — S the mask of a zero forcing set, F a list of fort masks
    forming a fort packing, with |S| <= (npd.width + 1)|F|.
    Complexity: O(nm) total (spec §4).
    """

    closure = zf_closure(g.adj)          # bound once; bag-agnostic engine
    A = ArcSet(g.n)                      # empty FAS (all NIL)
    F = []                               # fort packing: list of bytearrays
    t = 0
    while True:
        Xt = bytearray(npd.mask_of(t))   # X_t, fixed for this segment
        host = bytearray(Xt)             # running union X_t^z
        W = bytearray(g.n)               # empty mask
        z = t
        # ---- L3: scan forward -------------------------------------
        while not any(W) and z <= npd.k:
            z += 1
            Xz = npd.mask_of(z)          # bytes
            host |= Xz                   # host = X_t^z
            blue = bytearray(Xt); blue |= Xz
            W = closure.white(blue, host)          # L3b
        # ---- L4: reverse; sources of A become sinks ----------------
        A.reverse()
        if any(W):                                     # L6
            F.append(W)                                # L6a (fort!)
            # L6c: union; precondition below (C1)
            A.extend(closure.fas(bytearray(Xt) | npd.mask_of(z - 1), host))
            # L6d: X_z becomes the new source bag (no-op if z = k+1)
            A.delete_heads(bytearray(npd.mask_of(z)))
            t = z                                      # L6e
        else:                                          # L7: z = k+1
            A.extend(closure.fas(bytearray(Xt), host)) # L7a
            break
    S = A.sources()                                    # one (L5) at the very end
    return S, F