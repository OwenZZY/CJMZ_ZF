"""Outside API: the single public function and its translation layer.

The only place that touches external formats (HANDOFF.md section 8,
SPEC-v1.md section 7). The outside gives a NetworkX graph (its nodes are
the vertex names) and a list of bags (sets of names) forming a path
decomposition — not necessarily nice. This layer translates both to the
internal index-based objects, makes the decomposition nice, runs the
unchanged core, and translates the answer back to the original names.

Internal-core rules carry over: inputs are assumed suitable (simple
undirected graph; bags satisfy D1/D2 and cover every vertex); nothing is
validated. networkx itself is never imported here — the layer only reads
graph.nodes and graph.edges — so the package stays standard-library-only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, FrozenSet, Tuple

from .algorithm import zero_forcing_set as _core
from .decomposition import NicePathDecomposition
from .graph import Graph


@dataclass(frozen=True)
class ZFResult:
    """Output of the outside :func:`zero_forcing_set`, in original names.

    zf_set: tuple of vertex names (sorted) forming a zero forcing set S.
    forts: the fort packing F; pairwise disjoint frozensets of names,
        in discovery order.
    arcs: the final forcing arc set A as (name, name) pairs, sorted by
        tail; its sources are exactly zf_set.
    """

    zf_set: Tuple[Any, ...]
    forts: Tuple[FrozenSet[Any], ...]
    arcs: Tuple[Tuple[Any, Any], ...]


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


def zero_forcing_set(graph, bags):
    """Return a zero forcing set and a fort packing of ``graph``.

    graph: a networkx.Graph (simple, undirected); its nodes are the
        vertex names.
    bags: a list of sets of vertex names forming a path decomposition
        of graph — not necessarily nice; every vertex must lie in some
        bag. Assumed suitable; nothing is validated.

    Returns ZFResult in the original names: zf_set (sorted names),
    forts (frozensets of names), arcs ((name, name) pairs). The returned
    set S satisfies |S| <= (w + 1) * |F|, where w is the width of the
    bags and F the returned fort packing.
    """
    g = Graph(graph.nodes, graph.edges)
    index_bags = [frozenset(g.index[v] for v in bag) for bag in bags]
    pd = _to_nice(index_bags, g.n)
    r = _core(g, pd)
    return ZFResult(
        zf_set=tuple(g.to_names(r.zf_set)),
        forts=tuple(frozenset(g.to_names(f)) for f in r.forts),
        arcs=tuple(g.arcs_to_names(r.arcs.arcs())),
    )
