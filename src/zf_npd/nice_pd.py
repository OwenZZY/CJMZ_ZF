"""Nice path decomposition — fresh implementation.

A nice path decomposition is a bag sequence X_0, ..., X_k, X_{k+1} with
empty sentinels X_0 = X_{k+1} = empty and consecutive bags differing in
exactly one vertex.  This module stores such a decomposition and serves it
to the driver entirely in id space (0..n-1); no graph object is involved.

Constructor contract
--------------------
NicePD(n, calX, shift_by=0)
    n         int                     number of vertices; ids are 0..n-1
    calX      sequence of sequences  the FULL bag list X_0..X_{k+1} given
                                       as vertex NAMES, including the two
                                       empty sentinel bags; both ends are
                                       verified to be empty (so the
                                       sentinels are never synthesized)
    shift_by  int = 0                 name -> id map:  id = name - shift_by
                                       (0-based, 1-based, or any other base)

Authoritative order inside __init__:
    1. parse + VALIDATE only: the first and the last bag of calX must be
       empty, and consecutive bags must differ in exactly one vertex; on
       failure the constructor raises and no derived attribute
       (k, masks, ops, width) is assigned.
       RESERVED: this is the future slot for a make_npd repair of invalid
       bags, followed by a re-validation.  Not wired yet.
    2. masks: frozen bytes, one byte per id, value 0/1.
    3. ops:   ops[0] = X_0 -> X_1, ..., ops[k] = X_k -> X_{k+1}; each
       entry is (v, is_insert) with v the differing id (post-shift).
    4. width: max |X_i| - 1 over the interior bags.

Only the empty-sentinel condition and the differ-by-one criterion are
validated here; no lifetime checks (D2/D3) and no edge-coverage check
(D1).  Callers own well-formedness beyond these.
"""

from __future__ import annotations

from collections.abc import Sequence


class NicePD:
    def __init__(self, n: int, calX: Sequence[Sequence[int]],
                 shift_by: int = 0) -> None:
        self.n = n
        self.shift_by = shift_by

        # ---- Phase 1: validate BEFORE any derived attribute exists ----
        try:
            bags = _parse_and_check(calX, n, shift_by)   # ids, X_0..X_{k+1}
        except ValueError:
            # RESERVED repair slot: bags = make_npd(calX, n, shift_by);
            # bags = _parse_and_check(bags, n, shift_by); then proceed.
            raise

        # ---- Phase 2: only a validated bag list reaches this point ----
        self.k = len(bags) - 2
        self.masks = tuple(_to_mask(bag, n) for bag in bags)
        self.ops = tuple(_ops_of(bags[i], bags[i + 1])
                         for i in range(self.k + 1))     # ops[0] = X_0 -> X_1
        self.width = max((m.count(1) for m in self.masks[1:-1]),
                         default=0) - 1

    def mask_of(self, i: int) -> bytes:
        """Frozen mask of bag X_i, for 0 <= i <= k+1 (sentinels all-zero)."""
        return self.masks[i]

    def op(self, z: int) -> tuple[int, bool]:
        """Transition X_z -> X_{z+1}, for 0 <= z <= k."""
        return self.ops[z]


# ---------------------------------------------------------------------------
# construction helpers
# ---------------------------------------------------------------------------

def _parse_and_check(calX: Sequence[Sequence[int]], n: int,
                     shift_by: int) -> list[set[int]]:
    """Names -> ids, then validation (Phase 1).

    Returns the bag list in id space, exactly as given.
    Raises ValueError if:
      - the first or the last bag is not empty, or
      - a name outside [0, n) after the shift appears, or
      - a bag contains a duplicate vertex, or
      - two consecutive bags differ in a number of vertices != 1.
    """
    if len(calX) < 2 or len(calX[0]) != 0 or len(calX[-1]) != 0:
        raise ValueError(
            "calX must be the full bag list X_0..X_{k+1}; its first and "
            "last bags must both be empty (the two sentinels)"
        )

    bags: list[set[int]] = []
    for bag in calX:
        ids = {v - shift_by for v in bag}
        if len(ids) != len(bag):
            raise ValueError(
                f"bag {bag} contains a duplicate vertex (after shift_by)"
            )
        if any(v < 0 or v >= n for v in ids):
            raise ValueError(
                f"bag {bag} with shift_by={shift_by} contains an id "
                f"outside [0, {n})"
            )
        bags.append(ids)

    for i in range(1, len(bags)):
        diff = bags[i - 1] ^ bags[i]
        if len(diff) != 1:
            raise ValueError(
                f"transition X_{i-1} -> X_{i} changes {len(diff)} vertices; "
                f"a nice path decomposition requires exactly 1"
            )
    return bags


def _to_mask(bag: set[int], n: int) -> bytes:
    m = bytearray(n)
    for v in bag:
        m[v] = 1
    return bytes(m)


def _ops_of(prev: set[int], cur: set[int]) -> tuple[int, bool]:
    (v,) = prev ^ cur        # validation guarantees a singleton
    return v, v in cur       # differing id set in X_{i+1} => introduce
