# SPEC v1 — zero forcing approximation via nice path decomposition (`zf`)

Supersedes `SPEC.md` (v0), which is kept untouched per `AGENTS.md` rule 7.
Source: Cameron–Janssen–Mathew–Zhang, arXiv:2402.08866v1,
`resources/paper/arXiv-2402.08866v1/2024-02-13-Zero_Forcing_Approx_Alg.tex` (976 lines; cited below as `tex:L`).

**Reading guide.** §1 reviews v0 (Step 1). §2 transcribes the algorithm line by line (Step 2);
the mathematical definitions live in `docs/definitions.md`, one item per line (Step 2.1/2.3).
§3 aligns v0 with the paper and assesses viability (Step 3). §4 is the name proposal (Step 3.1).
§5 is the complete structure: file layout, exact interfaces, and the main loop with its tricks
(Step 3.2). §6 lists issues found in v0 and how they were resolved — no open questions remain.
**§7 is the outside API (round 9): the single public function, the translation layer, and the
nice-ification convention — the only section an outside caller needs.**

**Round 3 (2026-11-21), owner ruling.** The core is lean and internal: inputs are assumed
suitable, and `zf/` contains no validation, no try/except, and no raised exceptions. The
round-2 state (defensive core, tests, examples, README) is preserved verbatim in
`zf-round2-backup.zip`.

**Round 9 (2026-11-21), owner ruling.** The outside API is frozen and implemented (§7): one
public function `zero_forcing_set(graph, bags)` (NetworkX graph + list of bags), a names-based
result object, and a translation layer that trusts suitable inputs and makes the decomposition
nice. The internal core (§5) is unchanged.

---

## 1. Review of SPEC v0 (Step 1)

- v0 correctly identifies the three core objects (`zf_Graph`, `arcs`, `nice_bags`) and the three
  implementation tricks ([L3], [L6b], [L6c]). The object choices match the paper's needs.
- v0 is missing: the `closure()` / `white()` / `fas()` subroutine (the paper's only nontrivial
  primitive, tex:L813–816), the output object (zero forcing set **and** fort packing, tex:L633),
  the bag/region bookkeeping that the [L3] trick requires, and the index convention relating
  `ops` (length 2n) to the paper's `k` (number of non-empty bags).
- v0 has two typos that change the meaning if read literally; both are resolved in §6.
- "In the first step, no coding" is honored: Steps 1–2 are documentation; coding starts at Step 3.2.

## 2. The algorithm, line by line (Step 2.2, tex:L623–665)

Input: a graph `G`, a nice path decomposition `X_0, X_1, ..., X_k, X_{k+1}` of `G`
(`X_0 = X_{k+1} = ∅`; `k` = number of non-empty bags).
Output: a zero forcing set `S` and a fort packing `F` of `G`.

- (L1) Set `t ← 0`, `S ← ∅`, `A ← ∅`, `F ← ∅`.
- (L2) Set `z ← t`, `W ← ∅`.
- (L3) While `W = ∅` and `z ≤ k`:
- (L3a) Set `z ← z + 1`.
- (L3b) Set `W ← white(X_t ∪ X_z, G(t,z))`.
- (L4) Set `A ← reverse(A)`.
- (L5) Set `S ← sources(A, X_0^t)`.
- (L6) If `W ≠ ∅`:
- (L6a) Add `W` to `F`.
- (L6b) Set `S ← S ∪ X_{z-1}`.
- (L6c) Set `A' ← A ∪ fas(X_t ∪ X_{z-1}, G(t,z))`.
- (L6d) Set `A ← {(u,v) ∈ A' : v ∉ X_z}`.
- (L6e) Set `t ← z` and go to (L2).
- (L7) If `W = ∅`:
- (L7a) Set `A ← A ∪ fas(X_t, G(t,z))`.
- (L8) Return `S` and `F`.

Notation used above (full list in `docs/definitions.md`): `X_i^j = ⋃_{τ=i..j} X_τ`,
`G(i,j) = G[X_i^j]`, `white(S,H)` = vertices still white after forcing to fixation on `H` from `S`,
`fas(S,H)` = the forcing arc set of that process, `sources(A,U)` = in-degree-0 vertices of `A` in `U`.

Facts from the paper that the implementation relies on (statements only, no proofs):

- The while loop exits either at `z = k+1` with `W = ∅` (finished), or at the first `z` with
  `W ≠ ∅`; in the latter case `X_z ⊂ X_{z-1}` (a forget step), hence `G(t,z) = G(t,z-1)`
  (tex:L668–682, Lemma "s"). The `W ≠ ∅` case can occur at `z = k+1` itself: if no fort was
  found earlier (`t = 0`), then `W = white(∅, G) = V` and the trivial fort `V` is added —
  paper-faithful; see §7.4.
- (L6d) only ever removes arcs whose head lies in `X_t ∩ X_z`; after it, every vertex of `X_z`
  is a source of `A` (tex:L683).
- `S` need not be maintained: (L5) and (L6b) may be omitted and `S` computed once at the end as
  `sources(A, V)` (tex:L685). This is exactly the [L6b] trick of v0.
- Invariant after each outer iteration: `A` is a forcing arc set of `G(0,t)` and
  `X_t ⊆ sources(A)` (tex:L696–701). At return, `A` is a forcing arc set of `G` and
  `S = sources(A)` (tex:L753).
- Each `W` added to `F` is a fort; the forts are pairwise disjoint (tex:L756–768).
- `|S| ≤ (w+1)·|F|` where `w` is the decomposition width (tex:L769–793).
- The core assumes suitable inputs; the paper assumes connected graphs (tex:L822). The implementation
  only requires the milder condition that the bags cover `V` (the caller's responsibility), so
  edgeless and disconnected graphs work too.

## 3. Alignment and viability (Step 3)

| v0 object | paper role | verdict |
|---|---|---|
| `zf_Graph` (static, 0-based, name bijection, edge list) | `G` | viable as-is; add adjacency lists for `closure` |
| `arcs` (`out_arcs`/`in_arcs` arrays, `add/delete/reverse/extend/source`) | `A`, `reverse(A)`, (L6d), `sources` | viable; the array pair is exactly the "≤1 in, ≤1 out" invariant of forcing arc sets; `delete(heads)` matches (L6d) directly; `reverse` is an O(1)-style swap of the two arrays |
| `nice_bags` (`ops[i] = (v, ±1)`, length 2n) | `X_0..X_{k+1}` | viable; fix convention: `len(ops) = 2n`, bags `X_0..X_{2n}`, `k = 2n−1`, op `z−1` (0-based) turns `X_{z-1}` into `X_z` |
| (missing) | `white`, `fas`, `closure` | add one primitive `closure(graph, blue) -> (white, arcs)`; `white` and `fas` are its two projections |
| (missing) | output `S`, `F` | add result object `ZFResult(zf_set, forts, arcs)`; returning `A` too is free and useful |
| (missing) | bag/region maintenance for [L3]/[L6c] | the loop keeps `bag = X_z`, `region = X_t^z`, `xt = X_t` incrementally |

Flow viability: with `closure` on the **full** graph (the [L6c] trick), no induced subgraph is ever
built; the loop only ever (i) advances `z` by one op, (ii) occasionally calls `closure`,
(iii) reverses/extends/deletes on `arcs`. All v0 operations are used; none is missing except
`closure`, which v0 itself names in the [L6c] note. The structure is implementable as specified.

## 4. Name proposal (Step 3.1)

Public GitHub release; repo `zf-approx`, package `zf` (as in the v0 title). Stdlib only.

| v0 / paper | proposed | note |
|---|---|---|
| `zf_Graph` | `Graph` (`zf/graph.py`) | fields `n`, `names`, `index`, `edges`, `adj` |
| `arcs` | `Arcs` (`zf/arcs.py`) | keep `out_arcs`, `in_arcs`, `count`, `__len__`, `add`, `delete`, `reverse`, `extend`; `source()` → `sources()` |
| `nice_bags` | `NicePathDecomposition` (`zf/decomposition.py`) | fields `ops`, `bags`, `n`, `k`, `width`; ctor `from_bags` |
| `white`/`fas`/`closure` | `closure(graph, blue)` (`zf/closure.py`) | returns `(white, arcs)` |
| main loop | `zero_forcing_set(graph, pd)` (`zf/algorithm.py`) | returns `ZFResult` |
| `S`, `F`, `A`, `W`, `t`, `z` | `zf_set`, `forts`, `arcs`/`A`, `W`, `t`, `z` | loop keeps the paper's letters `t, z, W, A` for traceability to (L1)–(L8) |

## 5. Complete structure (Step 3.2)

### 5.1 File layout

```
zf/__init__.py        # exports ONLY zero_forcing_set (the outside API, from zf/api.py)
zf/api.py             # outside API: zero_forcing_set(graph, bags), ZFResult (names), _to_nice
zf/graph.py           # Graph                      (internal)
zf/arcs.py            # Arcs                       (internal)
zf/decomposition.py   # NicePathDecomposition      (internal)
zf/closure.py         # closure                    (internal)
zf/algorithm.py       # zero_forcing_set, ZFResult (internal, index-based)
```

### 5.2 Interfaces (shared API — fixed)

All vertex arguments are 0-based indices unless stated. Python ≥ 3.9, stdlib only.
**Internal core (round-3 ruling): inputs are assumed suitable; no validation, no try/except,
no exceptions raised.** Suitability is the caller's responsibility.

**`Graph(vertices, edges)`** — static simple graph.
- `vertices`: an `int n` (names are `0..n-1`, edges given as index pairs), or an iterable of
  distinct hashable external names; names are ordered by `sorted()`, giving the bijection
  `names[i] ↔ i` (v0 example: `{1,2,4}` → `names = (1,2,4)`).
- `edges`: iterable of unordered endpoint pairs (external names, or indices when `vertices` is `int`).
  Assumed suitable (simple graph, known endpoints); duplicate pairs collapse in the edge-list set.
- Fields: `n: int`; `names: tuple` (index → name); `index: dict` (name → index);
  `edges: tuple[tuple[int,int]]` with `i < j`, sorted; `adj: tuple[tuple[int,...]]`, sorted neighbors.
- `__len__` returns `n`. No mutation after construction.
- Output views of the bijection (round 4): `to_names(vertices)` returns the external name of one
  index, or a list of names for an iterable of indices; `arcs_to_names(arcs)` returns external-name
  pairs for an iterable of index arcs. The core stays index-based; these translate results back to
  the input names (e.g. `S = [0]` → `['a']`).

**`Arcs(n)`** — arc set on `0..n-1` with in/out-degree ≤ 1.
- Fields: `out_arcs: list[int]`, `in_arcs: list[int]`, both length `n`, entries in `0..n-1` or `-1`,
  initially all `-1`; invariant `out_arcs[i] == j` iff `in_arcs[j] == i`. `count: int` maintained
  dynamically; `__len__` returns `count`.
- `add(i, j)`: insert arc `i → j` — set `out_arcs[i] = j`, `in_arcs[j] = i`, `count += 1`.
  Slot safety and unidirectionality are guaranteed by the algorithm, not checked here.
- `delete(heads)`: `heads` is one head index or an iterable of them. For each head `j` with
  `i = in_arcs[j] != -1`: set `out_arcs[i] = -1`, `in_arcs[j] = -1`, decrement `count`.
  Heads without an in-arc are skipped. Returns the number of arcs removed.
  (v0's wording swaps `i`/`j`; the semantics is "remove the arc whose **head** is `j`" — see §6.)
- `reverse()`: swap `out_arcs` and `in_arcs` in place; `count` unchanged.
- `extend(other)`: add every arc of `other` (an `Arcs` on the same `n`); merges are slot-safe
  by the cut construction (vertices of `X_t` are sinks of the reversed `A`, sources of the new set).
- `sources(vertices=None)`: sorted list of `i` with `in_arcs[i] == -1`, restricted to `vertices`
  (an iterable of indices) when given; includes isolated vertices. One-time call at the end of the
  algorithm (v0 `source()`).
- `arcs()`: list of `(i, j)` pairs, sorted by tail.

**`NicePathDecomposition(ops, n=None)`** — nice path decomposition as operations.
- `ops`: sequence of `(v, sign)` with `sign ∈ {+1, -1}`; op `i` (0-based) turns bag `X_i` into
  `X_{i+1}`. Assumed suitable: `X_0 = ∅`, final bag `∅`, every intermediate bag non-empty, each
  step adds/removes exactly one vertex (D2–D4; D2 contiguity is automatic since each vertex is
  introduced once and forgotten once). Bags are materialized by replay, without checks.
- `n`: vertex count; inferred as `1 + max(v)` when omitted (`0` for empty `ops`).
- Fields: `ops: tuple`; `bags: tuple[frozenset]` of length `len(ops)+1` (materialized once);
  `k = len(ops) − 1` (number of non-empty bags; `k = -1` when `n = 0`);
  `width = max(|X_i| − 1)` over non-empty bags (`-1` when there are none).
- `from_bags(bags)` classmethod: derive `ops` from consecutive bags differing by exactly one vertex,
  with empty first and last bag (assumed).
- Input suitability — `n` matches the graph, every vertex lies in some bag, and (D1) every edge
  has both endpoints in a common bag — is the caller's responsibility; the core does not check it.

**`closure(graph, blue)`** — zero forcing to fixation on the **full** graph.
- `blue`: iterable of initial blue indices.
- Returns `(white, arcs)`: `white` = sorted list of indices still white;
  `arcs` = list of `(u, v)` forcing pairs in the order forced.
- Deterministic, canonical order (tex:L621): at each step the eligible blue vertex of **smallest
  index** forces, via a min-heap keyed by vertex id. Seed the heap with all blue vertices having
  exactly one white neighbor (scanning indices `0..n-1`); when `u` forces its unique white
  neighbor `v`, record `(u,v)`, turn `v` blue, decrement the white-neighbor count of each blue
  neighbor of `v`, push any that reach 1, and push `v` if it has exactly one white neighbor.
  Stale heap entries (count no longer 1) are skipped. Each vertex forces at most once and is
  forced at most once, so `arcs` is a forcing arc set with sources = the initial blue set that
  actually forced something, plus idle blues. The count engine is Brimkov–Fast–Hicks (EJOR 2019,
  Algorithm 1) in complementary form (white counts instead of colored counts); the min-index
  canon matches the parallel project's `zf_closure.py` (owner decision, 2026-11-21; see
  `docs/closure-review.md`).
- `white(S, H)` and `fas(S, H)` of the paper are the two projections of `closure`; with the [L6c]
  trick, `H` is always the full `G` and `S` is augmented by all vertices outside the region.

**`zero_forcing_set(graph, pd)`** — Algorithm (L1)–(L8) with the tricks (§5.3).
- Returns **`ZFResult`** (frozen dataclass): `zf_set: tuple[int, ...]` (sorted `S`),
  `forts: tuple[frozenset[int], ...]` (the packing `F`), `arcs: Arcs` (final `A`, `sources == S`).

### 5.3 Main loop with the tricks

State kept across the loop: `A: Arcs`, `forts: list`, `t`, and the incremental bag bookkeeping
`xt = X_t` (fixed per outer iteration), `bag = X_z`, `region = X_t^z`.
`V` is `range(n)`; "outside" means `V \ region`.

```
L1  t = 0; A = Arcs(n); forts = []; bag = ∅; region = ∅
L2  z = t; W = ∅; xt = bag; region = set(bag)          # X_t^t = X_t
L3  while W == ∅ and z <= k:
        z += 1
        v, sign = ops[z-1]
        if sign == +1:                                  # introduce v
            bag.add(v); region.add(v)
            continue                                    # [L3 trick]: W stays ∅, no closure call
        bag.remove(v)                                   # forget v
        if v in xt:
            continue                                    # blue set unchanged, W stays ∅
        blue = (V \ region) | xt | bag                  # [L6c]: outside assumed blue
        W, _ = closure(graph, blue)
L4  A.reverse()
L6  if W != ∅:                                          # z is a forget step; G(t,z) = G(t,z-1)
        forts.append(frozenset(W))                      # L6a
        # L6b omitted: S is not maintained (paper remark tex:L685)
        blue = (V \ region) | xt | bag | {v}            # X_{z-1} = bag ∪ {v}; [L6c] again
        _, new_arcs = closure(graph, blue)              # = fas(X_t ∪ X_{z-1}, G(t,z))
        for (i, j) in new_arcs: A.add(i, j)             # L6c: A' = A ∪ fas(...)
        A.delete(bag)                                   # L6d: drop arcs with head in X_z
        t = z                                           # L6e
        go to L2
L7  else:                                               # W == ∅, z == k+1, bag == ∅
        blue = (V \ region) | xt
        _, new_arcs = closure(graph, blue)              # = fas(X_t, G(t,k+1))
        for (i, j) in new_arcs: A.add(i, j)             # L7a
L8  return ZFResult(tuple(A.sources()), tuple(forts), A)   # L5 once, at the end
```

### 5.4 Trick report (required by v0)

- **[L3] "add it and continue".** When op `z−1` introduces `v`, the vertex `v` joins `X_z`, so it is
  blue in `X_t ∪ X_z`; it was already assumed blue as an "outside" vertex under [L6c]. Adding a blue
  vertex can never invalidate a forcing move, and `W = ∅` before the step, so `W` stays `∅`:
  the loop adds `v` to `bag`/`region` and continues **without calling `closure`**.
  (This is the contrapositive content of Lemma "s", tex:L668–676: only a forget step can make `W`
  non-empty.) The same argument gives a second skip: forgetting `v ∈ X_t` leaves both the blue set
  `X_t ∪ X_z` and the graph `G(t,z)` unchanged, so `W` stays `∅` there too. Closure is therefore
  called only when forgetting a vertex `v ∉ X_t`. This is the "update in the [L3] part" that
  maintains the [L6c] coloring as `z` advances.
- **[L6b] not needed.** `S` is never maintained during the loop; (L5) and (L6b) are omitted and `S`
  is computed once at (L8) as `A.sources()` (paper remark, tex:L685).
- **[L6c] closure on the full graph.** Instead of building the induced subgraph `G(t,z)`, call
  `closure(graph, blue)` with `blue = (V \ X_t^z) ∪ X_t ∪ X_z`: all vertices outside `G(t,z)` are
  assumed blue, `X_t ∪ X_z` is blue, the rest white. This is exact, in plain terms: an outside
  vertex only touches the region through `X_t ∪ X_z` (contiguity D2 guarantees every inside-neighbor
  of an outside vertex lies in `X_t ∪ X_z`), and those are blue — so an outside vertex has no white
  neighbor and never forces, and the process inside the region is identical to the one on `G(t,z)`.
  The same trick computes `fas(X_t ∪ X_{z-1}, G(t,z))` at (L6c) and `fas(X_t, G(t,k+1))`
  at (L7a); all arcs produced lie inside the current region, so `extend`/`add` merges are slot-safe
  (vertices of `X_t` are sinks of the reversed `A` and sources of the new arc set).
  (v0 writes the blue set as `V \ V(G(t,z)) ∪ X_t^z`; read literally that is all of `V`. The intended
  set is `(V \ X_t^z) ∪ X_t ∪ X_z`, matching (L3b) — see §6.)

## 6. Issues found in v0, and resolutions (no open questions)

1. **[L6c] blue-set typo.** v0: "`V(G) \setminus V(G(t,z)) ∪ X_t^z`". Since `X_t^z = V(G(t,z))`,
   the literal reading blues every vertex and forces `W = ∅` always. Resolution: the blue set is
   `(V \ X_t^z) ∪ X_t ∪ X_z`, forced by consistency with (L3b)'s `white(X_t ∪ X_z, G(t,z))`.
2. **`arcs.delete` wording.** v0: "removes `out_arcs[j]` and simultaneously `in_arc[i]` where `i`
   corresponds to `j`", with `j` the head. The indices are swapped: removing the arc with head `j`
   clears `in_arcs[j]` and `out_arcs[i]` for `i = in_arcs[j]`. Resolution: implement head-based
   deletion as stated in §5.2; this is exactly what (L6d) needs (`A.delete(X_z)`).
3. **`source()` vs `sources()`** (plain). v0's one-time `source()` lists every vertex with no
   in-arc. The paper writes `sources(A, U)`: the sources *inside a chosen vertex set* `U` (during
   the loop the arc set lives on only part of the graph, so one sometimes wants sources restricted
   to that part). Resolution: one method `sources(vertices=None)` — no argument gives all sources
   (exactly v0's `source()`); a vertex set restricts. The algorithm calls it once, at (L8), over all
   vertices, so in practice it is v0's one-time call.
   Why the mask matters (owner, round 5): with the [L6c] full-graph closure, outside vertices are
   blued, so they have no in-arc and appear as spurious sources if `sources()` is taken over all
   `n` vertices. The derived colors and the arcs inside the region are still correct; only the
   source set is polluted. `sources(region)` returns `sources ∩ region`, the region's true sources
   (demonstrated in `examples.py`, block 8: P6 region {1,2,3} gives `sources()=[0,1,4,5]` but
   `sources(region)=[1]`). The main algorithm does not need this mid-loop — it merges arcs into `A`
   and computes `sources(A)` once at (L8) over all `V`, where `A` spans `G`.
4. **Index convention** (plain). v0 says `ops` has length `2n` (each of the `n` vertices is added
   once and removed once). The paper labels bags `X_0, X_1, ..., X_k, X_{k+1}` with `X_0 = X_{k+1} = ∅`
   and `k` = number of non-empty bags. Reconciling: `2n` ops produce `2n+1` bags `X_0..X_{2n}`; the
   first and last are empty, so `k = 2n − 1`. Op number `z−1` (counting ops from 0) is the step that
   turns `X_{z-1}` into `X_z`. Example, `n=3` path: `ops = [(0,+),(1,+),(0,−),(2,+),(1,−),(2,−)]`
   (6 = 2n ops) gives bags `X_0=∅, X_1={0}, X_2={0,1}, X_3={1}, X_4={1,2}, X_5={2}, X_6=∅`, so
   `k=5=2n−1`. This is bookkeeping to line the code's indices up with the paper's; nothing
   mathematical changes. `n=0` gives `k=−1` and the loop body never runs.
   Sign set and offset (round 5): op signs are exactly `{+1, −1}` (introduce / forget) — there is
   no `0` op. Ops are 0-based: op `z−1` produces `X_z` (equivalently, 1-based op `z` produces
   `X_z`). Audited consistent across `zf/decomposition.py`, `zf/algorithm.py`, and this report;
   no off-by-one present.
5. **Isolated vertices / disconnected graphs.** (D1) alone does not force isolated vertices into
   bags. Resolution: the precise "suitable input" condition is D1–D4 plus every vertex lying in
   some bag — weaker than the paper's connectedness assumption. It is the caller's responsibility;
   the lean core (round 3) does not check it.
6. **`S` maintenance.** v0 keeps `S` in the loop; the paper (tex:L685) explicitly allows dropping
   (L5)/(L6b). Resolution: drop them (the [L6b] trick); `ZFResult.zf_set` is computed once at the end.
7. **Forcing-order canon (round 2, 2026-11-21).** v0/v1 initially used a FIFO queue; the parallel
   project's closure uses the smallest-eligible-index canon (min-heap), which is the paper's
   example canon (tex:L621). Owner approved alignment: `closure` now pops the smallest eligible
   index, giving arc-for-arc parity with the parallel project (verified 960/960 trials). The
   white set and fort packing are canon-independent; only the arcs and hence `S` can depend on it.
   Review and evidence: `docs/closure-review.md`.

---

## 7. Outside API (round 9, 2026-11-21 — frozen by owner, implemented)

The only section an outside caller needs. The internal core (§5) is unchanged.

### 7.1 The single function

**`zf.zero_forcing_set(graph, bags)`** — the only package export (`__all__`).

- `graph`: a `networkx.Graph` — simple, undirected; its nodes are the vertex names
  (distinct, sortable; isolated vertices included).
- `bags`: a list of sets of vertex names forming a path decomposition of `graph`:
  (D1) every edge has both endpoints in some bag; (D2) each vertex's bags are contiguous;
  every vertex lies in some bag. The bags need **not** be nice.
- Suitability is the caller's responsibility (owner ruling, 2026-11-21): the layer trusts
  suitable inputs exactly as the core does; nothing is validated.
- Returns a frozen **`ZFResult`** (defined in `zf/api.py`) in the **original names**:
  - `zf_set: tuple` of names, sorted — a zero forcing set `S`;
  - `forts: tuple[frozenset]` of names — the fort packing `F`, in discovery order;
  - `arcs: tuple` of `(name, name)` pairs, sorted by tail — the final forcing arc set `A`;
    its sources are exactly `zf_set`.
- Guarantee: `|S| ≤ (w + 1)·|F|` with `w = max|bag| − 1` of the given bags.

```python
import networkx as nx
import zf

G = nx.path_graph(["a", "b", "c"])
r = zf.zero_forcing_set(G, [{"a", "b"}, {"b", "c"}])   # bags need not be nice
r.zf_set    # ('a',)
r.forts     # (frozenset({'a', 'b', 'c'}),)  — see §7.4 on the trivial fort
r.arcs      # (('a', 'b'), ('b', 'c'))
```

### 7.2 Translation layer (`zf/api.py`)

The only place that touches external formats. Steps:
1. `Graph(graph.nodes, graph.edges)` — reuses the core's sorted name↔index bijection.
   The layer **never imports networkx** (it reads `.nodes`/`.edges`, trusted): `import zf`
   stays standard-library-only; networkx is needed only to construct inputs.
2. Bags → index sets → `_to_nice(bags, n)` → `NicePathDecomposition` (§7.3).
3. Run the unchanged core `zf.algorithm.zero_forcing_set`.
4. Translate the index result back to names via `Graph.to_names` / `Graph.arcs_to_names`.

### 7.3 Nice-ification convention (`_to_nice`)

- Drop empty bags and consecutive duplicates; empty end bags are implicit (the op sequence
  starts from `∅` and ends at `∅`).
- Between consecutive bags `X_i, X_{i+1}`: **forget** the vertices of `X_i \ X_{i+1}` in
  increasing index order, **then introduce** the vertices of `X_{i+1} \ X_i` in increasing
  index order.
- Forget-first is forced by width preservation: intermediate bags stay subsets of `X_i`
  (during forgets) or of `X_{i+1}` (during introduces); introduce-first could inflate a bag
  to `|X_i ∪ X_{i+1}|`. Every input bag appears verbatim in the nice sequence, so D1/D2 and
  the width are preserved; each vertex is introduced once and forgotten once (`2n` ops,
  `k = 2n−1`).
- Empty intersections: for disconnected graphs, consecutive bags may be disjoint; the
  width-preserving sequence then passes through an empty intermediate bag (D3 relaxed).
  The core replays ops without D3 checks; verified correct (round-9 trials including
  disconnected and edgeless graphs).
- This is the paper's cited transformation: Bodlaender–Kloks 1994, Lemma 13.1.3
  (tex:L580–581): width preserved, `O(n)` time, at most `4n` bags.
- Deterministic: sorted order at every transition. Nice-ification of already-nice bags is
  the identity (verified: layer == core, arc-for-arc, on nice inputs).
- The nice-ified decomposition need not equal a hand-made one; `S`, forts, and arcs can
  differ between valid decompositions — the guarantee holds for all of them.

### 7.4 Recorded behavior notes (round 9)

- The loop evaluates `W` at `z = k+1` (tex:L639–642). If no fort was found earlier (`t = 0`),
  then `W = white(∅, G) = V`, so the trivial fort `V` is added and the final `A.reverse()`
  flips the last chain — paper-faithful (traced against the algorithm box). Hence for
  `n ≥ 1` every run returns at least one fort.
- API provenance (HANDOFF §6/§8): owner point 1 = the shape (round 8); point 2 =
  decomposition provenance (HANDOFF §4.2) — building a decomposition from a graph
  (pathwidth) is **out of scope unless asked**: the caller supplies bags, the layer makes
  them nice. Point 3: not stated; fold in when given.