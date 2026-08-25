from __future__ import annotations

from . import zf_arcset
from dataclasses import dataclass
from typing import Iterable, Optional


class zf_closure:
    """Colour-change engine on an induced host (spec §8 rows for White / FAS).

    The host is never materialised.  Every neighbourhood scan is filtered by a
    caller-supplied membership oracle (normally the running union X_t^z).
    White is unique; FAS follows the paper canon: one force per step, least-
    index eligible forcer.
    """

    def __init__(self, adj: list[list[int]]) -> None:
        """Bind the (immutable) adjacency lists of G.
        The engine itself stores no colouring or arc set between calls.
        """
        raise NotImplementedError("interface skeleton — implementation pending")

    def white(self, blue: bytearray, host: bytearray) -> bytearray:
        """Return the set of vertices that remain white after the zero-forcing
        process on the induced host.

        blue  – mask of the initial blue set (X_t ∪ X_z)
        host  – mask of the current vertex set X_t^z
        Both masks have length n; a vertex is considered only when host[v] is true.
        The returned mask has a bit set precisely for the vertices that stay white.
        """
        raise NotImplementedError("interface skeleton — implementation pending")

    def fas(self, blue: bytearray, host: bytearray) -> "zf_arcs":
        """Return one forcing-arc set for the same process (paper canon).

        The returned object is a fresh zf_arcs instance whose arcs all lie
        inside the host and realise a valid forcing sequence from the given
        blue set.  In-/out-degree ≤ 1 is guaranteed by construction.
        """
        raise NotImplementedError("interface skeleton — implementation pending")

    def white_and_fas(self, blue: bytearray, host: bytearray) -> tuple[bytearray, "zf_arcs"]:
        """Convenience: compute both results in a single closure pass.
        (Optional; the two separate methods already satisfy the contract.)
        """
        raise NotImplementedError("interface skeleton — implementation pending")