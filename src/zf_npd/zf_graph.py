"""Graph with dual adjacency storage (zf_npd).

Vertices are canonical ids 0..n-1. Input names (ints) may come shifted:
with n = len(adj) the name range must satisfy high - low <= n - 1, so the
single shift low -> 0 lands every name in 0..n-1. Gaps are isolated
vertices and are harmless; a span >= n is rejected. The applied shift is
stored as shift_by (input name v -> id v - shift_by).

Storage — one representation is the mask of the other:
    adj_list[u]    sorted neighbour list of u, ascending
    adj_rows[u]    bytearray of length n; adj_rows[u][v] == 1 iff uv is an edge

adj_list is canonical (built from the input); adj_rows is derived from it,
so the two cannot drift. Input assumptions: simple graph (both directions
of every edge listed, no duplicates). Self-loops are dropped. The input
list is read only — never stored, never mutated.
"""

from __future__ import annotations


def check_ids(adj: list[list[int]]) -> tuple[int, int]:
    """Return (n, shift_by): n = len(adj); every name v maps to id v - shift_by.

    Reject iff high - low >= n: the window [low, high] then holds >= n+1
    slots, and no single shift can fit them into n mask positions.
    """
    n = len(adj)
    names = [v for row in adj for v in row]
    if not names:
        return n, 0                     # edgeless input: any shift is vacuous
    if not all(isinstance(v, int) for v in names):
        raise TypeError("vertex names must be ints")
    low, high = min(names), max(names)
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
    """

    def __init__(self, adj: list[list[int]]) -> None:
        """Validate names, record the shift, build both representations."""
        n, shift_by = check_ids(adj)
        self._build(adj, n, shift_by)

    @classmethod
    def _from_adj0(cls, adj: list[list[int]]) -> Graph:
        """Build from already-canonical rows (0-based, ascending, loop-free).

        Skips __init__ via __new__ so no re-alignment runs: internally
        produced rows (induced_subgraph) may contain no id 0, and the
        aligning path would silently relabel every vertex.
        """
        g = cls.__new__(cls)
        g._build(adj, len(adj), 0)
        return g

    def _build(self, adj: list[list[int]], n: int, shift_by: int) -> None:
        self.n = n
        self.shift_by = shift_by

        # one pass per entry: the walrus computes the shifted id once, the
        # filter drops self-loops, the sort gives ascending rows (Timsort
        # runs near-linear on the already-ascending filtered rows)
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
        assert len(host) == self.n, (
            f"host must be a mask of length {self.n}, got {len(host)}"
        )
        assert all(b in (0, 1) for b in host), "host entries must be 0/1"
        rows = [
            [v for v in row if host[v]] if host[u] else []
            for u, row in enumerate(self.adj_list)
        ]
        return Graph._from_adj0(rows)

    def N(self, u: int) -> list[int]:
        """Neighbours of u, ascending."""
        return self.adj_list[u]

    def deg(self, u: int) -> int:
        return len(self.adj_list[u])
