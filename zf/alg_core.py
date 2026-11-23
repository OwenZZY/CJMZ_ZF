"""Main zero-forcing approximation loop (Algorithm 1, lines L1-L8).

Transcribed from Cameron-Janssen-Mathew-Zhang, arXiv:2402.08866v1,
tex:L623-665, with the three tricks recorded in SPEC-v1.md, section 5.4:

  [L3]  introduce steps (and forgets of vertices already in X_t) keep
        W empty, so they skip the closure call: "add it and continue";
  [L6b] S is not maintained during the loop; it is read off A.sources()
        once at the end (paper remark, tex:L685);
  [L6c] closure runs on the FULL graph, with every vertex outside the
        current region X_t^z assumed blue, instead of building G(t,z).

Internal core: the graph and decomposition are assumed suitable; nothing
is validated. Line numbers in comments refer to the algorithm box.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, FrozenSet

from .arcs import Arcs
from .zf_closure import closure
from .path_decomp import NicePathDecomposition
from .graph import Graph


@dataclass(frozen=True)
class ZFResult:
    """Output of :func:`zf_core`.

    zf_set: sorted tuple of vertex indices forming a zero forcing set S.
    forts: the fort packing F; pairwise disjoint frozensets of indices.
    arcs: the final forcing arc set A; its sources are exactly zf_set.
    """

    zf_set: Tuple[int, ...]
    forts: Tuple[FrozenSet[int], ...]
    arcs: Arcs


def zf_core(graph: Graph, pd: NicePathDecomposition) -> ZFResult:
    """Return a zero forcing set and a fort packing of ``graph``.

    Algorithm 1 of arXiv:2402.08866v1 on the nice path decomposition ``pd``.
    The returned set S satisfies |S| <= (w + 1) * |F|, where w is the width
    of ``pd`` and F the returned fort packing (paper, Thm. ratio).
    """
    n = graph.n
    ops = pd.ops
    k = pd.k
    all_vertices = set(range(n))

    # (L1) t <- 0, S <- empty, A <- empty, F <- empty.
    t = 0
    A = Arcs(n)
    forts = []
    bag = set()      # current bag X_z, maintained incrementally
    region = set()   # current region X_t^z, maintained incrementally

    while True:
        # (L2) z <- t, W <- empty.  Start a new outer iteration at t:
        # X_t^t = X_t, so the region resets to the current bag.
        z = t
        W = []
        xt = frozenset(bag)
        region = set(bag)

        # (L3) while W = empty and z <= k:
        while not W and z <= k:
            z += 1                                  # (L3a)
            v, sign = ops[z - 1]
            if sign == 1:
                # Introduce v: it joins X_z, hence is blue; it was already
                # assumed blue as an outside vertex.  W stays empty.
                # [L3 trick] add it and continue, no closure call.
                bag.add(v)
                region.add(v)
                continue
            # Forget v.
            bag.remove(v)
            if v in xt:
                # X_t ∪ X_z and G(t,z) are unchanged; W stays empty.
                continue
            # (L3b) W <- white(X_t ∪ X_z, G(t,z)), via [L6c]:
            # closure on the full graph, outside vertices assumed blue.
            blue = (all_vertices - region) | xt | bag
            W, _ = closure(graph, blue)

        # (L4) A <- reverse(A).
        A.reverse()
        # (L5) omitted: S is computed once at (L8).  [L6b trick]

        if W:
            # (L6) W non-empty: z is a forget step, G(t,z) = G(t,z-1).
            forts.append(frozenset(W))              # (L6a)
            # (L6b) omitted.  [L6b trick]
            # (L6c) A' <- A ∪ fas(X_t ∪ X_{z-1}, G(t,z)); here
            # X_{z-1} = bag ∪ {v}.  Again closure on the full graph.
            blue = (all_vertices - region) | xt | bag | {v}
            _, new_arcs = closure(graph, blue)
            for i, j in new_arcs:
                A.add(i, j)
            # (L6d) drop arcs whose head lies in X_z.
            A.delete(bag)
            # (L6e) t <- z, go to (L2).
            t = z
            continue

        # (L7) W empty: z = k+1 and bag = X_{k+1} = empty.
        # (L7a) A <- A ∪ fas(X_t, G(t,k+1)), via [L6c].
        blue = (all_vertices - region) | xt
        _, new_arcs = closure(graph, blue)
        for i, j in new_arcs:
            A.add(i, j)
        break

    # (L8) return S and F; S = sources(A) in one call.  [L6b trick]
    return ZFResult(tuple(A.sources()), tuple(forts), A)