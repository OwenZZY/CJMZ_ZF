"""Graph with dual adjacency storage (zf_npd).

Vertices are names (ints). Construction aligns names into 0..n-1 by a single
shift: n = len(adj), and the name range must satisfy

    high - low <= n - 1

so one shift (low -> 0) fits every name into a length-n mask. Gaps in the
range are isolated vertices and are harmless. A span >= n (i.e. >= n+1 slots
in the window) is rejected: no single shift can fit it. The applied shift is
recorded on the object as shift_by.

Dual representation, one the mask of the other:

    adj_list[u]        sorted list of neighbours of u, ascending
    adj_rows[u]        bytearray of length n; adj_rows[u][v] == 1
                       iff v in adj_list[u]

adj_list is the canonical form (built from the input); adj_rows is derived
from it, so the correspondence holds by construction. Self-loops are dropped
at construction (filtered inside the row comprehension). The input is assumed
simple: no duplicate entries, and both directions of every edge listed.

The input adj is only read — never stored, never mutated.
"""

from __future__ import annotations


def check_ids(adj: list[list[int]]) -> tuple[int, int]:
    """Format check only (no graph object is built).

    n is recorded as the row count: n = len(adj).
    Returns (n, shift_by): aligning every name v to v - shift_by lands it in
    0..n-1. For an already-0-based input shift_by == 0, so the shift is the
    identity.

    Boundary: reject iff high - low >= n. The names must span at most n
    consecutive slots; a span of exactly n covers n+1 slots and can never
    fit into n mask positions, shift or no shift.
    """
    n = len(adj)
    names = [v for row in adj for v in row]
    if not names:
        return n, 0                      # edgeless input: any shift vacuous
    if not all(isinstance(v, int) for v in names):
        raise TypeError("vertex names must be ints")
    low = min(names)
    high = max(names)
    if high - low >= n:
        raise ValueError(
            f"names span {high - low + 1} slots ({low}..{high}) "
            f"but there are only {n} rows; one shift cannot fit them "
            f"into 0..{n - 1}"
        )
    return n, low


class Graph:
    """Graph on vertices 0..n-1 after alignment (see module docstring).

    n:        order = len(adj)
    shift_by: shift applied to input names (input name v -> stored id v - shift_by)
    adj_list: list[list[int]], one sorted neighbour row per vertex
    adj_rows: list[bytearray], mask form of adj_list
    induced_subgraph(host): new Graph over the same ids, edges inside host only
    """

    def __init__(self, adj: list[list[int]]) -> None:
        n, shift_by = check_ids(adj)     # order = len(adj); names checked here
        self._build(adj, n, shift_by)

    @classmethod
    def _from_adj0(cls, adj: list[list[int]]) -> Graph:
        """Internal fast path: `adj` is already 0-based, sorted, loop-free
        (e.g. produced by induced_subgraph). No check_ids, no alignment —
        ids are canonical by construction, so no relabelling can occur."""
        g = cls.__new__(cls)             # skip __init__ (no name alignment)
        g._build(adj, len(adj), 0)
        return g

    def _build(self, adj: list[list[int]], n: int, shift_by: int) -> None:
        self.n = n
        self.shift_by = shift_by

        # canonical list form: shift + self-loop filter + sort, one pass
        self.adj_list = [
            sorted(w for v in row if (w := v - shift_by) != u)
            for u, row in enumerate(adj)
        ]

        # derived mask form: one bytearray row per vertex
        # (self-loops already filtered above, so no diagonal handling needed)
        self.adj_rows = [bytearray(n) for _ in range(n)]
        for u, row in enumerate(self.adj_list):
            for v in row:
                self.adj_rows[u][v] = 1

    def induced_subgraph(self, host: bytearray) -> Graph:
        """Graph over the SAME ids 0..n-1, edges restricted to `host`.

        host: bytearray mask of length n, host[v] == 1 iff v is kept.
        Vertices outside host become isolated (empty rows); an edge survives
        iff both endpoints are in host.

        Linear: O(n + m) — each row of adj_list is filtered once; rows stay
        ascending, so the rebuild's sorts are Timsort's near-linear case.
        (Replaces the int-AND over adj_rows: that was O(n^2/64) C-level work
        — cheap, but quadratic, and pure overhead on sparse graphs.)

        Returns a NEW Graph over the same ids. Its shift_by is 0: these are
        internal canonical ids, so the parent's shift_by no longer applies.
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
