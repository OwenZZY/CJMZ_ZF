# %% [1] Setup — imports (paste as the first notebook cell)
# Our implementation lives in the repo folder zf-approx. If your notebook is
# OUTSIDE that folder, keep the sys.path line (adjust the path on another
# machine); if the notebook is inside the repo, you may delete it.
import sys
sys.path.insert(0, "/Users/OwenZhang/DeepSeekHarness/zf-approx")

import networkx as nx
import matplotlib.pyplot as plt
import zf                      # our implementation: stdlib-only, one export

%matplotlib inline
# One-time environment need (zf itself needs nothing beyond the stdlib):
#   pip install networkx matplotlib

# %% [2] Graph definition — the "house" (square 1-2-3-4-1, roof vertex 5)
G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4, 5])
G.add_edges_from([(1, 2), (2, 3), (3, 4), (1, 4),   # the square
                  (2, 5), (3, 5)])                  # the roof
pos = {1: (0, 0), 2: (0, 1), 3: (1, 1), 4: (1, 0), 5: (0.5, 1.8)}

# %% [3] Bags — a path decomposition of G (width 2). NOT nice: two bag-to-bag
# changes move two vertices; the layer nicifies them (forget-first).
bags = [{1, 4}, {1, 3, 4}, {1, 2, 3}, {2, 3, 5}]

# %% [4] Run our algorithm
r = zf.zf_via_path_decomp(G, bags)
print("zero forcing set S:", r.zf_set)
print("fort packing F:    ", [sorted(f) for f in r.forts])
print("forcing arcs A:    ", r.arcs)
w = max(map(len, bags)) - 1
print(f"guarantee: |S| = {len(r.zf_set)} <= (w+1)*|F| = ({w}+1)*{len(r.forts)} = {(w+1)*len(r.forts)}")
# Invalid bags halt immediately: zf.zf_via_path_decomp raises ValueError
# unless the bags satisfy D1 (edge coverage), D2 (contiguity) and cover V.

# %% [5] Present with NetworkX drawing tools: S + forts (left), arcs (right)
from matplotlib.patches import Patch

def present(G, pos, r):
    """Draw the result of zf.zf_via_path_decomp: S green, forts amber, arcs purple."""
    S = set(r.zf_set)
    fort_nodes = set().union(*r.forts) if r.forts else set()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

    colors = ["#2ca02c" if v in S else "#ffbf00" if v in fort_nodes else "#cfcfcf"
              for v in G.nodes]
    nx.draw_networkx(G, pos, ax=ax1, node_color=colors, node_size=750,
                     font_weight="bold", edge_color="#888888")
    ax1.set_title(f"Zero forcing set S = {sorted(S)} (green)\n"
                  f"Fort packing F = {[sorted(f) for f in r.forts]} (amber)")
    ax1.legend(handles=[Patch(color="#2ca02c", label="S (zero forcing set)"),
                        Patch(color="#ffbf00", label="fort (not in S)")],
               loc="upper left")

    nx.draw_networkx(G, pos, ax=ax2, node_color="#cfcfcf", node_size=750,
                     font_weight="bold", edge_color="#888888")
    nx.draw_networkx_edges(G, pos, edgelist=list(r.arcs), ax=ax2,
                           edge_color="#7c3aed", width=2.5, arrows=True,
                           arrowstyle="-|>", arrowsize=22,
                           connectionstyle="arc3,rad=0.12",
                           min_source_margin=20, min_target_margin=20)
    nx.draw_networkx_nodes(G, pos, nodelist=sorted(S), ax=ax2,
                           node_color="#2ca02c", node_size=750)
    nx.draw_networkx_labels(G, pos, ax=ax2, font_weight="bold")
    ax2.set_title(f"Forcing arcs A = {list(r.arcs)}\n"
                  "sources = S; every other vertex forced exactly once")
    for ax in (ax1, ax2):
        ax.margins(0.15)
    fig.tight_layout()
    plt.show()

present(G, pos, r)

# %% [6] A second example: C5 (the cycle from spec2), same procedure
G2 = nx.cycle_graph(5)                                # nodes 0..4
bags2 = [{0, 1}, {0, 1, 2}, {0, 2, 3}, {0, 3, 4}]     # width 2, not nice
r2 = zf.zf_via_path_decomp(G2, bags2)
print("S =", r2.zf_set, " forts =", [sorted(f) for f in r2.forts], " arcs =", r2.arcs)
present(G2, nx.circular_layout(G2), r2)
