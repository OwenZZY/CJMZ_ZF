"""Run the two handoff test cases through the full zf_npd pipeline.

Purpose: a plain runnable smoke file — construct the real objects with the
real initializers and call the real driver, then print what comes out.
No input tricks, no corner cases; just "does it run, and what does it say".

Cases (provided during onboarding):
    P5  path 0-1-2-3-4 with its nice path decomposition (0-based names)
    G   11-vertex graph, 1-based names {1..11}, with its decomposition

Run from the repo root:
    python3 examples/run_test_cases.py

(The file shims src/ onto sys.path; after `pip install -e .` that shim is
unnecessary but harmless.)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from zf_npd import Graph, NicePD, zf_npd, closure

# ---------------------------------------------------------------------------
# Case 1: P5 — path 0-1-2-3-4 (0-based names, shift_by will be 0)
# ---------------------------------------------------------------------------
P5 = [(0, 1), (1, 2), (2, 3), (3, 4)]

P5_NPD = [[], [0], [0, 1], [1], [1, 2], [2], [2, 3], [3], [3, 4], [4], []]

# ---------------------------------------------------------------------------
# Case 2: G — 11 vertices, 1-based names {1..11} (shift_by will be 1)
# ---------------------------------------------------------------------------
G = [(1, 2), (2, 3), (1, 3),
     (3, 5), (5, 6), (6, 8), (4, 8), (3, 4),
     (6, 7), (8, 9), (9, 10), (9, 11)]

G_NPD = [
    [],
    [1],
    [1, 2],
    [1, 2, 3],
    [2, 3],
    [3],
    [3, 4],
    [3, 4, 5],
    [4, 5],
    [4, 5, 6],
    [4, 6],
    [4, 6, 7],
    [4, 6],
    [4, 6, 8],
    [6, 8],
    [8],
    [8, 9],
    [9],
    [9, 10],
    [9, 10, 11],
    [10, 11],
    [11],
    [],
]


def run_case(name, edges, bags):
    """Build the real objects and run the real driver end to end."""
    print("=" * 72)
    print(f"Case: {name}")

    # Construction recipe from docs/HANDOFF.md (same name space both sides):
    g = Graph.from_edge_list(edges)                       # dirty input -> dedupe
    npd = NicePD(g.n, bags, shift_by=g.shift_by)          # full bag list, sentinels

    print(f"  graph:      n = {g.n}, shift_by = {g.shift_by}")
    print(f"  adjacency:  {g.adj_list}")
    print(f"  NicePD:     k = {npd.k}, width = {npd.width}")

    # The algorithm.
    S, F = zf_npd(g, npd)

    print(f"  S (zero forcing set, names): {S}")
    print(f"  F (fort packing, names):     {F}")

    # Documented guarantee, asserted in every driver test per the handoff:
    guarantee = len(S) <= (npd.width + 1) * len(F)
    print(f"  guarantee:  |S| = {len(S)} <= (width+1)*|F| = "
          f"({npd.width}+1)*{len(F)} = {(npd.width + 1) * len(F)}  -> {guarantee}")
    assert guarantee, "zf_npd guarantee violated"

    # Independent check that S really forces all of g (test-as-checker role):
    blue = bytearray(g.n)
    for v in S:
        blue[v - g.shift_by] = 1          # names -> ids
    W, _ = closure(g, blue)               # host=None: whole graph
    print(f"  checker:    closure(g, S) leaves W empty? -> {not any(W)}")
    print("=" * 72)


if __name__ == "__main__":
    run_case("P5 (path 0-1-2-3-4)", P5, P5_NPD)
    print()
    run_case("G (1-based names 1..11)", G, G_NPD)
