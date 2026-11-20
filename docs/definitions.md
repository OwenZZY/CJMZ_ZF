# Mathematical definitions — arXiv:2402.08866v1

Reference for the implementation (SPEC Step 2.1). One definition per line (Step 2.3).
Theorems and lemmas are omitted (they live in the paper). Line references are to
`resources/paper/arXiv-2402.08866v1/2024-02-13-Zero_Forcing_Approx_Alg.tex`.
All graphs are finite, simple, undirected unless stated otherwise.

## Zero forcing (tex:L143–146)

- **Blue/white partition**: a partition of `V(G)` into `W` (white) and `B ≠ ∅` (blue) (tex:L144).
- **Color change rule**: a white vertex `v` turns blue iff some blue neighbor `u` of `v` has `N[u] ∩ W = {v}`, i.e. `v` is the only white neighbor of `u`; then `u` **forces** `v` (tex:L144).
- **Derived coloring** of `S ⊆ V`: the coloring obtained by starting with exactly `S` blue and applying the color change rule until no more vertices can change; it is unique, independent of the order of forcing (tex:L144–145).
- **Zero forcing set**: a set `S ⊆ V` whose derived coloring is all blue (tex:L146).
- **Zero forcing number** `Z(G)`: the minimum size of a zero forcing set of `G` (tex:L146).

## Forcing chains and arc sets (tex:L177–247)

- **Forcing chain**: a directed path `v_1 v_2 ... v_k` with `v_1 ∈ B_0` (the initial blue set) such that `v_i` forces `v_{i+1}` for all `i < k`; forcing chains of one process are vertex-disjoint, and each is an induced path of `G` (tex:L179, L253).
- **Path cover number** `P(G)`: the minimum number of induced paths such that every vertex of `G` lies on exactly one of them (tex:L182).
- **Arc set of `G`**: a collection `A ⊆ V × V` of arcs `(u,v)` with `uv ∈ E`, required to be unidirectional: `(u,v) ∈ A` implies `(v,u) ∉ A` (tex:L234).
- **Source / sink**: a source is a vertex of in-degree zero, a sink a vertex of out-degree zero (in the digraph `H = (V,A)` when the context is clear) (tex:L233, L235).
- **Forcing arc set (FAS)**, Definition 2.1: an arc set `A` of `G` such that (P1) `H = (V,A)` is a collection of vertex-disjoint dipaths, and (P2) there is a zero forcing process on `G` in which `(u,v) ∈ A` precisely when blue `u` forces white `v`; `A` **represents** that process, and the sources of `A` form its zero forcing set (tex:L236–245).
- **Convention on ambiguity**: each white vertex is forced by one neighbor only, so one process may be represented by different arc sets; each vertex has at most one in-neighbor and at most one out-neighbor, and zero-forcing-set vertices have in-degree zero (tex:L231, L247).
- **Chain twist**, Definition 2.3: a cycle `v_0 v_1 ... v_{k-1} v_0` in `G` such that for all `i` (indices mod `k`): `(v_i, v_{i+1}) ∉ A` implies `(v_{i-1}, v_i) ∈ A` and `(v_{i+1}, v_{i+2}) ∈ A` (condition (CT)); `A` **contains a chain twist** if such a cycle exists (tex:L300–307).
- **FAS, structural form**: an arc set satisfying (P1) and (Q2) "`A` contains no chain twist" (equivalent to Definition 2.1 by the paper's characterization theorem) (tex:L381–385).
- **Reverse of an arc set**: `reverse(A) = {(v,u) : (u,v) ∈ A}`; the sources of `reverse(A)` are the sinks of `A` (tex:L436–439, L447).
- **Optimal forcing arc set**: a forcing arc set attaining `|A| = n − Z(G)` (the maximum possible size) (tex:L428–434).

## Forts (tex:L538–541)

- **Fort**: a set `F ⊆ V` such that no vertex in `V \ F` has exactly one neighbor in `F` (equivalently: even with all of `V \ F` blue, no vertex of `F` can be forced) (tex:L538).
- **Fort packing**: a collection of mutually disjoint forts (tex:L539).
- **Fort number** `ft(G)`: the largest size of a fort packing of `G`, `ft(G) = max{|F| : F is a fort packing}` (tex:L540–541).

## Path decompositions (tex:L549–569)

- **Path decomposition**: a collection of vertex subsets ("bags") satisfying (D1) and (D2) below (tex:L549–550, L562).
- **Nice path decomposition**, definition at tex:L554–567: bags `X_0, X_1, ..., X_k, X_{k+1} ⊆ V` such that:
- **(D1)** for each edge `uv ∈ E` there is some `1 ≤ i ≤ k` with `{u,v} ⊆ X_i` (tex:L557).
- **(D2)** for each `v` and `1 ≤ i < j ≤ k`, if `v ∈ X_i ∩ X_j` then `v ∈ X_s` for all `i ≤ s ≤ j` (contiguity) (tex:L558).
- **(D3)** `X_0 = X_{k+1} = ∅` and all `X_i`, `1 ≤ i ≤ k`, are non-empty (tex:L559).
- **(D4)** for all `0 ≤ i ≤ k`, either `X_{i+1} = X_i ∪ {v}` for some `v ∉ X_i` (introduce) or `X_{i+1} = X_i \ {v}` for some `v ∈ X_i` (forget) (tex:L560).
- **Width** of a path decomposition: `max{|X_i| − 1 : 1 ≤ i ≤ k}` (tex:L563).
- **Pathwidth** `pw(G)`: the least width of any path decomposition of `G` (tex:L564).
- **Optimal path decomposition**: one whose width equals `pw(G)` (tex:L565).
- **End set**: a bag `X_i` with `⋃_{j<i} X_j ⊆ X_i` or `⋃_{j>i} X_j ⊆ X_i` (tex:L566).
- **Notation `X_k` (calligraphic)**: shorthand for the whole nice path decomposition `X_0, ..., X_{k+1}` with `X_0 = X_{k+1} = ∅` and `k` non-empty bags (tex:L569).

## Algorithm notation (tex:L600–621, L813)

- **`X_i^j`**: `⋃_{τ=i..j} X_τ`, for `0 ≤ i ≤ j ≤ k+1` (tex:L600–602).
- **`G(i,j)`**: the induced subgraph `G[X_i^j]` (tex:L602–603).
- **Induced subgraph `G[S]`**: the subgraph of `G` on vertex set `S` with all edges of `G` between vertices of `S` (standard; used throughout).
- **`sources(A, V)` / `sinks(A, V)`**: the sources / sinks of `H = (V,A)`; both are zero forcing sets when `A` is a forcing arc set (tex:L614).
- **`white(S, G)`**: the set of vertices remaining white after the zero forcing process on `G` from initial blue set `S` (the derived coloring's white part); well-defined since the derived coloring is unique; `S` is a zero forcing set iff `white(S,G) = ∅`; `white(S,G)` is always a fort (tex:L616–618).
- **`fas(S, G)`**: the forcing arc set of the zero forcing process on `G` from initial blue set `S`; made unique by a canonical choice, e.g. one force per step, choosing the eligible blue vertex of lowest index (tex:L620–621).
- **Closure** of `S ⊆ V`: the set of all blue vertices after applying all possible forcing from `S`; `white(S,G)` is its complement (tex:L813).
- **Vertex cut**: a set `C ⊆ V` whose removal increases the number of connected components (standard notion, used without formal definition in the paper); in the cut setup, `V_1` is the vertex set of one component of `G − C`, `V_2 = V \ (V_1 ∪ C)`, `G_1 = G[V_1 ∪ C]`, `G_2 = G[V_2 ∪ C]` (tex:L460–461).

## Peripheral definitions (not used by the core algorithm)

- **Circumference**: the length of the longest cycle of a graph containing at least one cycle (tex:L213).
- **Clique cover**: a collection of cliques such that every edge has both endpoints in some clique of the collection; **clique cover number** `cc(G)`: the minimum size of a clique cover (tex:L843).
- **Interval graph**: a graph whose vertices map to intervals on the real line, adjacent iff the intervals intersect; **unit interval graph**: all intervals have unit length; **proper interval graph**: no interval properly contains another; the two notions coincide (tex:L851–852).
- **Strong product** `G ⊠ G'`: vertex set `V × V'`; `(u,u')(v,v')` is an edge iff (a) `u = v` and `u'v' ∈ E'`, or (b) `uv ∈ E` and `u' = v'`, or (c) `uv ∈ E` and `u'v' ∈ E'` (tex:L879–887).
- **PSD zero forcing color change rule**: with blue set `B` and `G_i = G[V_i ∪ B]` for each component `V_i` of `G − B`, a blue `u` forces white `v ∈ V_i` if `v` is the only white neighbor of `u` in `G_i`; forcing arcs form directed trees (tex:L953–957).