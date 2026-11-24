# %% [1] Setup — imports + drawing helper (paste as the first notebook cell)
# Our implementation lives in the repo folder zf-approx. If your notebook is
# OUTSIDE that folder, keep the sys.path line (adjust the path on another
# machine); if the notebook is inside the repo, you may delete it.
import sys
sys.path.insert(0, "/Users/OwenZhang/DeepSeekHarness/zf-approx")

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import zf                      # our implementation: stdlib-only, one export

%matplotlib inline
# One-time environment need (zf itself needs nothing beyond the stdlib):
#   pip install networkx matplotlib


def report(r, bags):
    """Line-by-line results, with the guarantee bound aligned and checked."""
    w = max(map(len, bags)) - 1
    nS, nF = len(r.zf_set), len(r.forts)
    print(f"S        = {r.zf_set}")
    print(f"forts    = {[sorted(f) for f in r.forts]}")
    print(f"arcs     = {r.arcs}")
    print(f"|S|      = {nS}")
    print(f"w        = {w}")
    print(f"|F|      = {nF}")
    print(f"(w+1)|F| = {(w + 1) * nF}")
    print(f"|S| <= (w+1)|F| : {nS} <= {(w + 1) * nF}  "
          f"{'OK' if nS <= (w + 1) * nF else 'VIOLATED'}")


def present(G, pos, r):
    """One figure per case: S green, forcing arcs purple arrows.
    The explanation lives in the legend (outside the axes, never over nodes)."""
    S = set(r.zf_set)
    fig, ax = plt.subplots(figsize=(7.6, 4.6 if G.number_of_edges() else 2.8))
    colors = ["#2ca02c" if v in S else "#cfcfcf" for v in G.nodes]
    nx.draw_networkx(G, pos, ax=ax, node_color=colors, node_size=750,
                     font_weight="bold", edge_color="#888888")
    if r.arcs:
        nx.draw_networkx_edges(G, pos, edgelist=list(r.arcs), ax=ax,
                               edge_color="#7c3aed", width=2.5, arrows=True,
                               arrowstyle="-|>", arrowsize=22,
                               connectionstyle="arc3,rad=0.12",
                               min_source_margin=20, min_target_margin=20)
        nx.draw_networkx_nodes(G, pos, nodelist=sorted(S), ax=ax,
                               node_color="#2ca02c", node_size=750)
        nx.draw_networkx_labels(G, pos, ax=ax, font_weight="bold")
    ax.legend(handles=[Patch(color="#2ca02c", label="S (zero forcing set)"),
                       Line2D([0], [0], color="#7c3aed", lw=2.5, marker=">",
                              markersize=7, label="forcing arcs A"),
                       Patch(color="#cfcfcf", label="other vertices")],
              loc="center left", bbox_to_anchor=(1.0, 0.5))
    ax.margins(0.15)
    fig.tight_layout()
    plt.show()

# %% [2] Case: the house — square 1-2-3-4-1, roof vertex 5 (demo §§1-4)
G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4, 5])
G.add_edges_from([(1, 2), (2, 3), (3, 4), (1, 4),   # the square
                  (2, 5), (3, 5)])                  # the roof
pos = {1: (0, 0), 2: (0, 1), 3: (1, 1), 4: (1, 0), 5: (0.5, 1.8)}
bags = [{1, 4}, {1, 3, 4}, {1, 2, 3}, {2, 3, 5}]    # width 2, not nice

r = zf.zf_via_path_decomp(G, bags)
report(r, bags)
present(G, pos, r)

# %% [3] Case: C5 — the cycle from spec2 (demo §5)
G = nx.cycle_graph(5)                               # nodes 0..4
pos = nx.circular_layout(G)
bags = [{0, 1}, {0, 1, 2}, {0, 2, 3}, {0, 3, 4}]    # width 2, not nice

r = zf.zf_via_path_decomp(G, bags)
report(r, bags)
present(G, pos, r)

# %% [4] Case: the owner's graph H — 11 vertices, bags already nice
H = nx.Graph()

E = [(1,2), (2,3), (1,3),
    (3,5), (5,6), (6,8), (4,8),   (3,4),
    (6,7), (8,9), (9, 10), (9,11)]
H.add_edges_from(E)
bags = [
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
    []
]
pos = {1: (0, 2), 2: (0, 1), 3: (1, 1.5),
       4: (2, 1), 5: (2, 2),
       6: (3, 2), 7: (3, 3), 8: (3, 1),
       9: (4, 1.5), 10: (5, 2), 11: (5, 1)}

r = zf.zf_via_path_decomp(H, bags)
report(r, bags)
present(H, pos, r)
