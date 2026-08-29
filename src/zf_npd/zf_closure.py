"""Colour-change engine (zero-forcing closure) — zf_npd.

Runs the zero-forcing process on the induced subgraph G[host].  The
subgraph is materialised by Graph.induced_subgraph over the SAME vertex
ids (vertices outside host become isolated) and those outside vertices are
marked blue — in the induced graph they are inert, so this is pure
bookkeeping that keeps the final white mask correct without host checks.

The process is carried by the count array

    count[u] = #{ w in G.N(u) : coloured[w] }   (loop invariant; read only
                                                for blue u)

so the colour-change rule becomes: blue u is eligible  <=>
count[u] == deg(u) - 1, i.e. exactly one non-coloured neighbour, found by
one filtered scan of N(u).

The derived colouring is unique ([Barioli et al. 2010]); the forcing order
here follows the paper's canon: one force per step, performed by the
eligible blue vertex of smallest index (min-heap keyed by vertex id).
Deterministic; O((n + m) log n) per call.
"""

from __future__ import annotations

from heapq import heappop, heappush

from .zf_arcset import ArcSet


def closure(g, blue_in, host=None):
    """Run zero forcing on G[host] from blue_in; return (W, A).

    g        Graph over vertices 0..n-1.
    blue_in  bytearray mask of length g.n: initial blue set (read-only;
             never mutated).
    host     bytearray mask of length g.n, or None (= all of g).

    Returns:
        W  bytearray mask of the vertices that remain white.
        A  fresh ArcSet holding one arc u -> v per forcing step, in the
           paper's canonical order (smallest eligible forcer first).
    """
    # ---- early exit: no white vertex can ever exist ------------------------
    # any() over a generator — no mask arithmetic needed; O(n)
    if host is None:
        has_white = any(not b for b in blue_in)
    else:
        has_white = any(host[v] and not blue_in[v] for v in range(g.n))
    if not has_white:
        return bytearray(g.n), ArcSet(g.n)     # empty W and empty A (BOTH outputs)

    # ---- choose the process graph ------------------------------------------
    if host is None:
        G = g
        coloured = bytearray(blue_in)          # builtin copy; caller's mask untouched
    else:
        G = g.induced_subgraph(host)           # same ids; outside vertices isolated
        coloured = bytearray(blue_in)
        for v, bit in enumerate(host):         # outside host = blue (inert in G)
            if not bit:
                coloured[v] = 1

    A = ArcSet(g.n)                            # real class; .add() asserts P1 per arc

    # ---- count invariant: for blue v, count[v] = #{w in G.N(v): coloured[w]} --
    count = [0] * g.n
    heap = []
    for v, bit in enumerate(coloured):
        if bit:
            c = sum(coloured[w] for w in G.N(v))   # builtin sum(); P2
            count[v] = c
            if c == G.deg(v) - 1:                  # exactly one non-coloured neighbour; P3
                heappush(heap, v)                  # smallest id pops first = paper canon

    # ---- forcing loop -------------------------------------------------------
    while heap:
        u = heappop(heap)
        w = next((x for x in G.N(u) if not coloured[x]), None)   # builtin next()
        if w is None:
            continue                       # stale: unique white neighbour already blue
        coloured[w] = 1                    # u forces w
        A.add(u, w)
        for x in G.N(w):                   # blue neighbours of w each lost a white neighbour
            if coloured[x]:
                count[x] += 1
                if count[x] == G.deg(x) - 1:
                    heappush(heap, x)
        count[w] = sum(coloured[x] for x in G.N(w))   # w just turned blue: recompute
        if count[w] == G.deg(w) - 1:
            heappush(heap, w)

    # ---- result: white mask = complement of coloured -------------------------
    W = bytearray(g.n)
    for v, bit in enumerate(coloured):
        if not bit:
            W[v] = 1
    return W, A