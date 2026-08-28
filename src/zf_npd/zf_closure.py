"""Colour-change engine (zero-forcing closure) on an induced-host view.

Implements the exact design in docs/zf_npd_step_order.md, section
"Closure engine — exact design". The induced subgraph G(t,z) is never
materialised as a graph object: it is the pair (self.adj, host), where
host is a 0/1 bytearray mask and the neighbour relation inside the host is

    w is a host-neighbour of u  <=>  w in adj[u] and host[w] == 1.

The process is carried by the count array

    cnt[u] = #{ w in adj[u] : host[w] == 1 and w is white }   (loop invariant)

so the colour-change rule becomes: blue u is eligible  <=>  cnt[u] == 1,
and its unique white neighbour is found by one filtered scan of adj[u].

white() is order-independent (the derived colouring is unique, [Barioli et
al. 2010]); fas() applies the paper's canon: one force per step, performed
by the eligible blue vertex of smallest index (min-heap keyed by vertex id).
Both are deterministic and O(n + m) per call (fas: O((n+m) log n)).
"""

from __future__ import annotations


from heapq import heapify, heappop, heappush

from zf_arcset import ArcSet


# ----------------------------------------------------------------------------
# closure(g, blue_in, host=None) -> (W: bytearray, A: ArcSet)
# Snippet only — not written to any file.
# Mask convention (repo): bytearray of length g.n, one byte per vertex, 0/1.
# ----------------------------------------------------------------------------
from heapq import heappush, heappop            # stdlib, built-in priority queue

def closure(g, blue_in, host=None):
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
        G = g.induced_subgraph(host)           # PLACEHOLDER P1 (contract below)
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