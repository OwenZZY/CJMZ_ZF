"""Nice path decomposition — fresh implementation.

A nice path decomposition of a graph on ids 0..n-1 is a bag sequence
X_0, ..., X_k, X_{k+1} such that

    * X_0 = X_{k+1} = empty (the two sentinels), and
    * consecutive bags differ in exactly one vertex.

Every transition is therefore an introduce (one vertex added) or a forget
(one vertex removed).  The module stores such a decomposition and serves
it to the driver entirely in id space; no graph object is involved.

Validation scope (deliberately minimal): the two sentinels are empty and
consecutive bags differ by exactly one vertex.  Lifetime discipline (each
vertex introduced/forgotten exactly once), interior-bag nonemptiness, and
edge coverage (D1) are NOT checked; callers own well-formedness beyond
this.
"""

from __future__ import annotations

from collections.abc import Sequence


class NicePD:
    """A validated nice path decomposition over n vertices (ids 0..n-1).

    Input contract (constructor):
        n         number of vertices; ids are 0..n-1.
        calX      the FULL bag list X_0..X_{k+1} as vertex NAMES,
                  including the two empty sentinel bags.  List of lists
                  of ints (tuples equally accepted: Sequence[Sequence[int]]).
        shift_by  name -> id map: id = name - shift_by.  Use 0 for
                  0-based names, 1 for 1-based names, or the graph's own
                  shift_by when names come from a Graph object.

    Construction order — validation runs FIRST, so an invalid input
    raises before any derived attribute (k, masks, ops, width) exists:
        1. _parse_and_check: names -> id sets; sentinels empty; every
           pair of consecutive bags differs in exactly one vertex.
           RESERVED: the except clause is the future slot where a
           make_npd repair of bad bags hooks in (repair, re-validate,
           then proceed).  Not wired yet.
        2. masks:  frozen bytes, one byte per id, value 0/1.
        3. ops:    ops[z] = transition X_z -> X_{z+1} for z = 0..k, as
                   (v, is_insert) with v the differing id.
        4. width:  max |X_i| - 1 over the interior bags.

    Stored interface (all in id space):
        n, shift_by   construction parameters (kept for traceability).
        k             number of interior bags; k+2 bags in total.
        width         max bag size - 1.
        masks         tuple of k+2 frozen bytes masks, sentinels included.
        ops           tuple of k+1 transitions; ops[0] = X_0 -> X_1.
    """

    def __init__(self, n: int, calX: Sequence[Sequence[int]],
                 shift_by: int = 0) -> None:
        self.n: int = n
        self.shift_by: int = shift_by

        # ---- Phase 1: validate BEFORE any derived attribute exists ----
        try:
            bags = _parse_and_check(calX, n, shift_by)   # ids, X_0..X_{k+1}
        except ValueError:
            # RESERVED repair slot: bad bags -> make_npd(calX, n, shift_by)
            # -> _parse_and_check again, then proceed.  Not wired yet.
            raise

        # ---- Phase 2: only a validated bag list reaches this point ----
        self.k: int = len(bags) - 2
        self.masks: tuple[bytes, ...] = tuple(_to_mask(b, n) for b in bags)
        self.ops: tuple[tuple[int, bool], ...] = tuple(
            _ops_of(bags[i], bags[i + 1]) for i in range(self.k + 1)
        )                                    # ops[0] = X_0 -> X_1
        self.width: int = max(
            (m.count(1) for m in self.masks[1:-1]), default=0
        ) - 1

    def mask_of(self, i: int) -> bytes:
        """Frozen mask of bag X_i, for 0 <= i <= k+1.

        O(1).  Sentinels are all-zero.  Returns the stored bytes object
        (immutable by type), so callers cannot corrupt the decomposition
        through it.
        """
        return self.masks[i]

    def op(self, z: int) -> tuple[int, bool]:
        """Transition X_z -> X_{z+1} as (v, is_insert), for 0 <= z <= k.

        v is the differing id (post-shift); is_insert is True iff
        X_{z+1} = X_z u {v} (False: X_{z+1} = X_z \\ {v}).  O(1).  The
        driver replays these transitions to grow/shrink its host and bag
        masks without recomputing symmetric differences.
        """
        return self.ops[z]


# ---------------------------------------------------------------------------
# construction helpers (module-private)
# ---------------------------------------------------------------------------

def _parse_and_check(calX: Sequence[Sequence[int]], n: int,
                     shift_by: int) -> list[set[int]]:
    """Phase 1: map names to ids and validate; return bags as id-sets.

    Each bag becomes a set (intra-bag order irrelevant, duplicates
    rejected), so the differ-by-one check is just len(prev ^ cur).
    Raises ValueError if the first or last bag is not empty, a name maps
    outside [0, n), a bag holds a duplicate vertex, or two consecutive
    bags differ in a number of vertices != 1.
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
    """Encode an id-set as a frozen 0/1 mask of length n (one byte per id).

    bytes rather than bytearray on purpose: masks served to the driver
    must be immutable, so no consumer can mutate the stored bags.
    """
    m = bytearray(n)
    for v in bag:
        m[v] = 1
    return bytes(m)


def _ops_of(prev: set[int], cur: set[int]) -> tuple[int, bool]:
    """One transition X_i -> X_{i+1} as (v, is_insert).

    Validation guarantees |prev ^ cur| == 1, so the symmetric difference
    is a singleton: unpacking yields the differing id v, and v in cur
    decides introduce (True) vs forget (False).
    """
    (v,) = prev ^ cur
    return v, v in cur
