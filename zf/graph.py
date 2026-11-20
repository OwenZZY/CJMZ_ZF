"""Static simple graph on 0..n-1 with a bijection to external vertex names."""


class Graph:
    """Graph(vertices, edges).

    vertices: an int n (edges given as index pairs), or an iterable of
    distinct external names, ordered by sorted() so that names[i] is the
    name of index i (e.g. {1,2,4} -> names (1,2,4)).
    edges: unordered endpoint pairs, in names or indices accordingly.

    Internal core: inputs are assumed suitable (simple graph, known
    endpoints); nothing is validated. Fields: n, names, index, edges
    (i < j, sorted), adj (sorted neighbor tuples). Static after construction.
    """

    def __init__(self, vertices, edges):
        if isinstance(vertices, int):
            self.names = tuple(range(vertices))
        else:
            self.names = tuple(sorted(vertices))
        self.index = {name: i for i, name in enumerate(self.names)}
        self.n = len(self.names)
        edge_set = set()
        for a, b in edges:
            i, j = self.index[a], self.index[b]
            edge_set.add((i, j) if i < j else (j, i))
        self.edges = tuple(sorted(edge_set))
        adj = [[] for _ in range(self.n)]
        for i, j in self.edges:
            adj[i].append(j)
            adj[j].append(i)
        self.adj = tuple(tuple(sorted(row)) for row in adj)

    def __len__(self):
        return self.n

    def to_names(self, vertices):
        """Output view of the bijection: external name of one vertex index,
        or a list of external names for an iterable of indices. The core
        stays index-based; this translates results back to input names."""
        if isinstance(vertices, int):
            return self.names[vertices]
        return [self.names[i] for i in vertices]

    def arcs_to_names(self, arcs):
        """External-name pairs of an iterable of index arcs (i, j)."""
        return [(self.names[i], self.names[j]) for i, j in arcs]