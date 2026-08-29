"""Graph with dual adjacency storage (zf_npd).

Vertices are canonical ids 0..n-1. Input names (non-negative ints) may
come shifted: with n = len(adj) the name range must satisfy
high - low <= n - 1, so the single shift low -> 0 lands every name in
0..n-1. Gaps are isolated vertices and are harmless; a span >= n is
rejected, as are negative names. The applied shift is stored as shift_by
(input name v -> id v - shift_by).

Storage — one representation is the mask of the other:
    adj_list[u]    sorted neighbour list of u, ascending
    adj_rows[u]    bytearray of length n; adj_rows[u][v] == 1 iff uv is an edge

adj_list is canonical (built from the input); adj_rows is derived from it,
so the two cannot drift. Input assumptions: simple graph (both directions
of every edge listed, no duplicates). Self-loops are dropped. The input
list is read only — never stored, never mutated.

Construction entry points (NetworkX-style, classmethods):
    Graph.from_adj_list(adj)          — same as Graph(adj)
    Graph.from_edge_list(edges)       — undirected build from an edge list,
                                        optional n for isolated vertices
"""

from __future__ import annotations


def check_ids(adj: list[list[int]]) -> tuple[int, int]:
    """Return (n, shift_by): n = len(adj); every name v maps to id v - shift_by.

    Reject iff high - low >= n: the window [low, high] then holds >= n+1
    slots, and no single shift can fit them into n mask positions.
    Negative names are rejected (names must be >= 0).
    One pass over the input: type check, negativity check, min and max together.
    """
    n = len(adj)
    low = high = 0
    seen = False
    for row in adj:
        for v in row:
            if not isinstance(v, int):
                raise TypeError("vertex names must be ints")
            if v < 0:
                raise ValueError(
                    f"negative vertex name: {v} — names must be >= 0"
                )
            if not seen:
                low = high = v
                seen = True
            elif v < low:
                low = v
            elif v > high:
                high = v
    if not seen:
        return n, 0                     # edgeless input: any shift is vacuous
    if high - low >= n:
        raise ValueError(
            f"names span {high - low + 1} slots ({low}..{high}) "
            f"but there are only {n} rows; one shift cannot fit them "
            f"into 0..{n - 1}"
        )
    return n, low


class Graph:
    """Graph on vertices 0..n-1 after alignment.

    n         order = len(adj)
    shift_by  input-name shift recorded at construction
    adj_list  list[list[int]], one ascending neighbour row per vertex
    adj_rows  list[bytearray], mask form of adj_list
    Build:    Graph(adj) | from_adj_list(adj) | from_edge_list(edges, n=None)
    """

    def __init__(self, adj: list[list[int]]) -> None:
        """Validate names, record the shift, build both representations."""
        n, shift_by = check_ids(adj)
        self._build(adj, n, shift_by)

    @classmethod
    def from_adj_list(cls, adj: list[list[int]]) -> Graph:
        """Build from an adjacency list; same as Graph(adj)."""
        return cls(adj)

    @classmethod
    def from_edge_list(cls, edges, n: int | None = None) -> Graph:
        """Build an undirected graph from a list of 2-tuples of names.

        n=None: the vertex set is exactly the names present —
                n = high - low + 1, shift_by = low.
        n given: allows isolated vertices; reject iff high - low >= n.
        Negative names rejected. Self-loops dropped; duplicate edges
        collapse (set rows).
        """
        low = high = 0
        seen = False
        for a, b in edges:
            for name in (a, b):
                if not isinstance(name, int):
                    raise TypeError("vertex names must be ints")
                if name < 0:
                    raise ValueError(
                        f"negative vertex name: {name} — names must be >= 0"
                    )
                if not seen:
                    low = high = name
                    seen = True
                elif name < low:
                    low = name
                elif name > high:
                    high = name
        if not seen:
            if n is None:
                raise ValueError("empty edge list requires an explicit n")
            return cls._from_adj0([[] for _ in range(n)])
        if n is None:
            n = high - low + 1
        elif high - low >= n:
            raise ValueError(
                f"names span {high - low + 1} slots ({low}..{high}) "
                f"but n = {n}; one shift cannot fit them into 0..{n - 1}"
            )
        shift_by = low
        rows = [set() for _ in range(n)]
        for a, b in edges:
            u, v = a - shift_by, b - shift_by
            if u == v:
                continue                 # self-loop: never a forcing edge
            rows[u].add(v)
            rows[v].add(u)               # undirected
        return cls._from_adj0([sorted(row) for row in rows], shift_by)

    @classmethod
    def _from_adj0(cls, adj: list[list[int]], shift_by: int = 0) -> Graph:
        """Build from already-canonical rows (0-based, ascending, loop-free).

        Skips __init__ via __new__ so no re-alignment runs: internally
        produced rows (induced_subgraph) may contain no id 0, and the
        aligning path would silently relabel every vertex. shift_by is
        recorded as metadata only (rows are canonical; no shift applied).
        """
        g = cls.__new__(cls)
        g._build(adj, len(adj), 0)
        g.shift_by = shift_by
        return g

    def _build(self, adj: list[list[int]], n: int, shift_by: int) -> None:
        """Shared builder: set n/shift_by, build adj_list, derive adj_rows."""
        self.n = n
        self.shift_by = shift_by

        # walrus computes each shifted id once; filter drops self-loops;
        # sort restores ascending rows (near-linear on filtered rows)
        self.adj_list = [
            sorted(w for v in row if (w := v - shift_by) != u)
            for u, row in enumerate(adj)
        ]

        self.adj_rows = [bytearray(n) for _ in range(n)]
        for u, row in enumerate(self.adj_list):
            for v in row:
                self.adj_rows[u][v] = 1

    def induced_subgraph(self, host: bytearray) -> Graph:
        """New Graph on the SAME ids, edge kept iff both endpoints in host.

        host: bytearray mask of length n, values 0/1. Vertices outside host
        become isolated. O(n + m): each adj_list row is filtered once.
        The result's shift_by is 0 (canonical ids; the parent's shift no
        longer applies). The parent is never mutated.
        """
        if len(host) != self.n:
            raise ValueError(
                f"host must be a mask of length {self.n}, got {len(host)}"
            )
        if any(b not in (0, 1) for b in host):
            raise ValueError("host entries must be 0/1")
        rows = [
            [v for v in row if host[v]] if host[u] else []
            for u, row in enumerate(self.adj_list)
        ]
        return Graph._from_adj0(rows)

    def N(self, u: int) -> list[int]:
        """Neighbours of u, ascending.

        Returns a fresh copy: callers cannot mutate the stored row
        (decision: defensive copy; O(deg(u)) per call).
        """
        return list(self.adj_list[u])

    def deg(self, u: int) -> int:
        """Degree of u, O(1)."""
        return len(self.adj_list[u])
