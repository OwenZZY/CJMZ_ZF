"""Arc set on 0..n-1 with in/out-degree at most one (vertex-disjoint dipaths)."""


class Arcs:
    """out_arcs[i] == j iff in_arcs[j] == i; -1 means absent.

    Internal core: the algorithm guarantees the invariant and the slot
    safety of every merge; operations perform the array updates directly,
    without checks. count is maintained dynamically; len(self) == count.
    """

    def __init__(self, n):
        self.n = n
        self.out_arcs = [-1] * n
        self.in_arcs = [-1] * n
        self.count = 0

    def __len__(self):
        return self.count

    def add(self, i, j):
        """Insert arc i -> j."""
        self.out_arcs[i] = j
        self.in_arcs[j] = i
        self.count += 1

    def delete(self, heads):
        """Remove the arc whose head is j, for each head j (int or iterable).

        Heads without an in-arc are skipped. Returns the number removed.
        """
        if isinstance(heads, int):
            heads = (heads,)
        removed = 0
        for j in heads:
            i = self.in_arcs[j]
            if i != -1:
                self.out_arcs[i] = -1
                self.in_arcs[j] = -1
                self.count -= 1
                removed += 1
        return removed

    def reverse(self):
        """Swap out_arcs and in_arcs; count unchanged."""
        self.out_arcs, self.in_arcs = self.in_arcs, self.out_arcs

    def extend(self, other):
        """Join every arc of other (an Arcs on the same n) into self."""
        for i, j in enumerate(other.out_arcs):
            if j != -1:
                self.add(i, j)

    def sources(self, vertices=None):
        """Sorted indices with in_arcs[i] == -1 (isolated vertices included),
        restricted to vertices when given."""
        if vertices is None:
            return [i for i in range(self.n) if self.in_arcs[i] == -1]
        return sorted(i for i in set(vertices) if self.in_arcs[i] == -1)

    def arcs(self):
        """List of (i, j) pairs sorted by tail."""
        return [(i, j) for i, j in enumerate(self.out_arcs) if j != -1]