# Complete, self-contained snippet: paste into ONE Jupyter cell and run.
# (Also saved as docs/standalone_H.py; needs: pip install networkx matplotlib)
import sys
sys.path.insert(0, "/Users/OwenZhang/DeepSeekHarness/zf-approx")  # drop if notebook is in the repo

import networkx as nx
import matplotlib.pyplot as plt
import zf                      # our implementation: stdlib-only, one export

%matplotlib inline


def present(G, pos, r):
    """One figure: zero forcing set S in green, forcing arcs as purple arrows.
    Forts are printed below, not drawn."""
    S = set(r.zf_set)
    fig, ax = plt.subplots(figsize=(5.6, 4.6 if G.number_of_edges() else 2.6))
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
    ax.set_title(f"S = {sorted(S)} (green)\nforcing arcs A = {list(r.arcs)} (purple)")
    ax.margins(0.15)
    fig.tight_layout()
    plt.show()


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
print("S =", r.zf_set, "| forts =", [sorted(f) for f in r.forts], "| arcs =", r.arcs)
w = max(map(len, bags)) - 1
print(f"guarantee: |S| = {len(r.zf_set)} <= ({w}+1)*{len(r.forts)} = {(w+1)*len(r.forts)}")
present(H, pos, r)
