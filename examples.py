"""Explicit worked examples.  Run:  python3 examples.py

These examples exercise the INTERNAL core directly (submodule imports);
the single outside interface is zf.zf_via_path_decomp (networkx graph +
list of bags; see SPEC-v1.md section 7).

Graphs are built with external names; the core works on 0-based indices
internally; results are translated back to names with Graph.to_names and
Graph.arcs_to_names.  "Derived coloring" = the final BLUE set after forcing
to fixation (closure); its complement is the white set.
"""

from zf.arcs import Arcs
from zf.graph import Graph
from zf.path_decomp import NicePathDecomposition
from zf.zf_closure import closure
from zf.alg_core import zf_core


def is_fort(graph, fort):
    """A fort: no vertex outside it has exactly one neighbor inside it."""
    fort = set(fort)
    return all(sum(1 for w in graph.adj[v] if w in fort) != 1
               for v in range(graph.n) if v not in fort)


def show_closure(title, graph, blue_names):
    blue_idx = [graph.index[v] for v in blue_names]
    white, arcs = closure(graph, blue_idx)
    white_set = set(white)
    derived = [i for i in range(graph.n) if i not in white_set]
    print(title)
    print(f"  vertices (names): {list(graph.names)}")
    print(f"  edges (names):    {graph.arcs_to_names(graph.edges)}")
    print(f"  internal edges:   {list(graph.edges)}")
    print(f"  initial blue:     {blue_names}")
    print(f"  derived coloring: {graph.to_names(derived)}")
    print(f"  white remaining:  {graph.to_names(white)}")
    print(f"  forcing arcs:     {graph.arcs_to_names(arcs)}")
    print()
    return graph.to_names(derived)


def show_algorithm(title, graph, pd):
    r = zf_core(graph, pd)
    print(title)
    print(f"  zero forcing set S (names): {graph.to_names(r.zf_set)}")
    print(f"  fort packing F (names):     {[graph.to_names(sorted(f)) for f in r.forts]}")
    print(f"  forcing arcs A (names):     {graph.arcs_to_names(r.arcs.arcs())}")
    print()
    return r


# 1. Path on names a, b, c — the name-translation example.
abc = Graph(["a", "b", "c"], [["a", "b"], ["b", "c"]])
d = show_closure("Path a-b-c, initial blue [a]", abc, ["a"])
assert d == ["a", "b", "c"]
abc_pd = NicePathDecomposition.from_bags(
    [set(), {0}, {0, 1}, {1}, {1, 2}, {2}, set()])
r = show_algorithm("Path a-b-c, main algorithm", abc, abc_pd)
assert abc.to_names(r.zf_set) == ["a"]

# 2. P3 on {1,2,3} (3 vertices): edges [[1,2],[2,3]], A=[1] -> derived [1,2,3].
p3 = Graph([1, 2, 3], [[1, 2], [2, 3]])
d = show_closure("P3 on {1,2,3}, initial blue [1]", p3, [1])
assert d == [1, 2, 3]

# 3. P4 on {1,2,3,4} (the edge list as written): A=[1] -> derived [1,2,3,4].
p4 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4]])
d = show_closure("P4 on {1,2,3,4}, initial blue [1]", p4, [1])
assert d == [1, 2, 3, 4]

# 4. C5 on {0,1,2,3,4}: A=[0] -> derived [0]; B=[0,1] -> derived whole graph.
c5 = Graph(5, [[0, 1], [1, 2], [2, 3], [3, 4], [0, 4]])
d = show_closure("C5, initial blue A=[0]", c5, [0])
assert d == [0]
d = show_closure("C5, initial blue B=[0,1]", c5, [0, 1])
assert d == [0, 1, 2, 3, 4]

# 5. Star: center c, leaves l1,l2,l3.  Two leaves force everything; the
#    center alone is stuck (three white neighbors).
star = Graph(["c", "l1", "l2", "l3"],
             [["c", "l1"], ["c", "l2"], ["c", "l3"]])
d = show_closure("Star, initial blue [l1,l2]", star, ["l1", "l2"])
assert d == ["c", "l1", "l2", "l3"]
d = show_closure("Star, initial blue [c]", star, ["c"])
assert d == ["c"]

# 6. K4 on {1,2,3,4}: two vertices are stuck; three force the fourth.
k4 = Graph([1, 2, 3, 4],
           [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]])
d = show_closure("K4, initial blue [1,2]", k4, [1, 2])
assert d == [1, 2]
d = show_closure("K4, initial blue [1,2,3]", k4, [1, 2, 3])
assert d == [1, 2, 3, 4]

# 7. C5: initial blue [0] leaves white [1,2,3,4], which is a FORT.
#    (The white set remaining after forcing is always a fort.)
white, _ = closure(c5, [0])
fort_names = c5.to_names(white)
print("C5 fort from initial blue [0]")
print(f"  derived coloring (blue): {[0]}")
print(f"  white remaining = fort:  {fort_names}")
print(f"  is_fort({fort_names}) = {is_fort(c5, white)}")
print(f"  check: outside vertex 0 has neighbors {[c5.to_names(w) for w in c5.adj[0]]}"
      f" in the fort -> {sum(1 for w in c5.adj[0] if w in set(white))} (not 1), so it is a fort")
print()
assert fort_names == [1, 2, 3, 4]
assert is_fort(c5, white)

# 8. Sources mask (Item 3): full-graph closure with outside vertices blued
#    gives the correct derived colors AND arcs inside the region, but
#    sources() over ALL vertices spuriously includes the outside vertices.
#    Restricting with sources(region) returns the region's true sources.
p6 = Graph(6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]])
region = {1, 2, 3}
white, arcs = closure(p6, [0, 1, 4, 5])   # outside {0,4,5} blued, inside blue {1}
a = Arcs(6)
for u, v in arcs:
    a.add(u, v)
print("Sources mask: P6, region {1,2,3}, inside blue {1}, outside {0,4,5} blued")
print(f"  forcing arcs (names):      {p6.arcs_to_names(arcs)}")
print(f"  sources() over all vertices: {p6.to_names(a.sources())}   <- includes outside 0,4,5")
print(f"  sources(region) = sources ∩ mask: {p6.to_names(a.sources(region))}   <- true source of fas({{1}}, G[region])")
print()
assert a.sources() == [0, 1, 4, 5]
assert a.sources(region) == [1]

print("All example assertions passed.")