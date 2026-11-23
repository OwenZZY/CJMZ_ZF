"""Nice path decomposition stored as introduce/forget operations."""


class NicePathDecomposition:
    """ops[i] = (v, +1 | -1) turns bag X_i into X_{i+1}.

    X_0 and the final bag are empty, intermediate bags are non-empty, and
    each vertex is introduced once and forgotten once (D2-D4; contiguity is
    automatic). Internal core: ops are assumed suitable; nothing is
    validated.

    Fields: ops, bags (frozensets X_0..X_{k+1}, materialized once), n,
    k = len(ops) - 1 (number of non-empty bags; -1 for empty ops),
    width = max |X_i| - 1 over non-empty bags (-1 when there are none).
    """

    def __init__(self, ops, n=None):
        self.ops = tuple(ops)
        if n is None:
            n = 1 + max((v for v, _ in self.ops), default=-1)
        self.n = n
        bag = set()
        bags = [frozenset()]
        for v, sign in self.ops:
            if sign == 1:
                bag.add(v)
            else:
                bag.discard(v)
            bags.append(frozenset(bag))
        self.bags = tuple(bags)
        self.k = len(self.ops) - 1
        self.width = max((len(b) - 1 for b in bags if b), default=-1)

    @classmethod
    def from_bags(cls, bags):
        """Derive ops from bags differing by exactly one vertex per step,
        with empty first and last bag."""
        bags = [frozenset(b) for b in bags]
        ops = []
        for i in range(len(bags) - 1):
            v = next(iter(bags[i] ^ bags[i + 1]))
            ops.append((v, 1 if v in bags[i + 1] else -1))
        union = set().union(*bags)
        n = 1 + max(union) if union else 0
        return cls(ops, n=n)