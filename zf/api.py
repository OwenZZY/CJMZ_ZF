"""Outside API: the single public function and its translation layer.

The only place that touches external formats (`SPEC-v1.md` §7). The outside gives a NetworkX graph (its nodes are
the vertex names) and a list of bags (sets of names) forming a path
decomposition — not necessarily nice. This layer CHECKS that the graph is
connected (_is_connected, owner ruling round 16) and that the bags really
are a path decomposition (_is_path_decomp, owner ruling round 11), halting
with ValueError if either fails; then it translates both inputs to the
internal index-based objects, makes the decomposition nice, runs the
unchanged core, and translates the answer back to the original names.

The core itself still trusts its inputs: no validation, no try/except,
no exceptions inside the core modules. The only raise in the package is
the layer's input halt below. networkx itself is never imported here —
the layer only reads graph.nodes and graph.edges — so the package stays
standard-library-only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, FrozenSet, Tuple

from .alg_core import zf_core as _core
from .path_decomp import NicePathDecomposition
from .graph import Graph


@dataclass(frozen=True)
class ZFResult:
    """Output of the outside :func:`zf_via_path_decomp`, in original names.

    zf_set: tuple of vertex names (sorted) forming a zero forcing set S.
    forts: the fort packing F; pairwise disjoint frozensets of names,
        in discovery order.
    arcs: the final forcing arc set A as (name, name) pairs, sorted by
        tail; its sources are exactly zf_set.
    """

    zf_set: Tuple[Any, ...]
    forts: Tuple[FrozenSet[Any], ...]
    arcs: Tuple[Tuple[Any, Any], ...]


def _is_connected(graph):
    """True iff graph is connected (vacuously True for 0 or 1 vertices).

    Layer-level check (owner ruling, round 16): the outside API requires a
    connected graph, as the paper does (tex:L822). The core itself still
    trusts its inputs and handles disconnected graphs if called directly.
    Depth-first reachability over the edge list; no networkx import.
    """
    nodes = set(graph.nodes)
    if len(nodes) <= 1:
        return True
    adj = {v: [] for v in nodes}
    for u, v in graph.edges:
        adj[u].append(v)
        adj[v].append(u)
    start = next(iter(nodes))
    seen = {start}
    stack = [start]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return seen == nodes


def _is_path_decomp(graph, bags):
    """True iff the bags form a path decomposition of graph.

    Checks the suitability contract, in names: every bag element is a
    vertex of graph; every vertex lies in some bag; (D1) every edge has
    both endpoints in a common bag; (D2) each vertex's bags are
    contiguous. Layer-level check only (owner ruling, round 11) — the
    core still trusts its inputs.
    """
    nodes = set(graph.nodes)
    bags = [set(b) for b in bags]
    covered = set()
    for b in bags:
        if not b <= nodes:
            return False
        covered |= b
    if covered != nodes:
        return False
    for u, v in graph.edges:
        if not any(u in b and v in b for b in bags):
            return False
    for v in nodes:
        pos = [i for i, b in enumerate(bags) if v in b]
        if pos != list(range(pos[0], pos[-1] + 1)):
            return False
    return True


def _to_nice(bags, n):
    """Make a path decomposition nice (forget-first, width-preserving).

    bags: iterable of index sets — a path decomposition of the graph on
    0..n-1, assumed suitable (D1/D2, every vertex in some bag). Returns
    a NicePathDecomposition.

    Convention: drop empty and consecutive-duplicate bags; between
    consecutive bags, forget the old-only vertices in increasing index
    order, then introduce the new-only vertices in increasing index
    order. Forget-first is forced by width preservation: every
    intermediate bag stays a subset of one of the two input bags. Each
    input bag appears verbatim in the nice sequence, so D1/D2 and the
    width are preserved; each vertex is introduced once and forgotten
    once. When consecutive bags have empty intersection (disconnected
    graphs), the sequence passes through an empty intermediate bag; the
    core replays ops without D3 checks and handles this correctly.
    """
    cleaned = []
    for bag in bags:
        bag = frozenset(bag)
        if bag and (not cleaned or bag != cleaned[-1]):
            cleaned.append(bag)
    ops = []
    prev = frozenset()
    for bag in cleaned + [frozenset()]:
        for v in sorted(prev - bag):
            ops.append((v, -1))
        for v in sorted(bag - prev):
            ops.append((v, +1))
        prev = bag
    return NicePathDecomposition(ops, n=n)


def zf_via_path_decomp(graph, bags):
    """Return a zero forcing set and a fort packing of ``graph``.

    Zero forcing via a path decomposition (the approximation algorithm
    of arXiv:2402.08866v1).

    graph: a networkx.Graph (simple, undirected, CONNECTED); its nodes are
        the vertex names.
    bags: a list of sets of vertex names forming a path decomposition
        of graph — not necessarily nice; every vertex must lie in some
        bag. Checked by _is_connected and _is_path_decomp; if the graph is
        disconnected or the bags are not a path decomposition, the call
        halts with ValueError.

    Returns ZFResult in the original names: zf_set (sorted names),
    forts (frozensets of names), arcs ((name, name) pairs). The returned
    set S satisfies |S| <= (w + 1) * |F|, where w is the width of the
    bags and F the returned fort packing.
    """
    if not _is_connected(graph):
        raise ValueError(
            "graph is not connected; the outside API requires a connected "
            "graph (the paper's assumption); the core itself trusts inputs")
    if not _is_path_decomp(graph, bags):
        raise ValueError(
            "bags are not a path decomposition of the graph "
            "(need: bag elements are vertices, every vertex covered, "
            "D1 edge coverage, D2 contiguity)")
    g = Graph(graph.nodes, graph.edges)
    index_bags = [frozenset(g.index[v] for v in bag) for bag in bags]
    pd = _to_nice(index_bags, g.n)
    r = _core(g, pd)
    return ZFResult(
        zf_set=tuple(g.to_names(r.zf_set)),
        forts=tuple(frozenset(g.to_names(f)) for f in r.forts),
        arcs=tuple(g.arcs_to_names(r.arcs.arcs())),
    )
