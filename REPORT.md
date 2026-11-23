# Report — zf-approx (round 11: 2026-11-23; rounds 9–10: 2026-11-21/23; rounds 1–5: 2026-11-20/21; rounds 6–8: see HANDOFF.md)

**What you need to read: nothing — no pending decisions.** Round 11 (2026-11-23): your naming
requests and the input gate are implemented — public function `zf.zf_via_path_decomp(graph, bags)`,
modules `path_decomp.py` / `zf_closure.py` / `alg_core.py`, and `_is_path_decomp` in the layer
halting with `ValueError` when the bags are not a path decomposition; the core is untouched.
Point 3 is closed as none; extras are deferred to your notebook phase.
Round 10 (2026-11-23): the requested
visual demonstration — [docs/pipeline-demo.html](docs/pipeline-demo.html), a self-contained
figure of the whole one-way procedure (input → translation layer → core loop → names-based
result), every state traced from the shipped code. Open it in a browser.
Round 9 (2026-11-21): implemented
the outside API per your answers (recorded in [HANDOFF.md](HANDOFF.md) §6) — one function
`zf.zero_forcing_set(networkx graph, list of bags)`, a names-based result object, and a
translation layer with forget-first nice-ification; the core is unchanged and everything is
verified. Your API point 2 was identified (= HANDOFF §4.2: pathwidth construction out of
scope unless asked); point 3 was not stated — fold it in whenever given.
Round 5: answered the sources-mask
question (viable; already implemented as `sources(vertices)`), added the C5 fort example
(initial `[0]` → fort `[1,2,3,4]`) and a sources-mask demo to [examples.py](examples.py),
audited the index/sign convention (correct; no `+0`/off-by-one), and **committed** the work.
Round 4: name-output interface + explicit examples + plain-language explanations.
Round 3: lean internal core; prior state preserved in [zf-round2-backup.zip](zf-round2-backup.zip).
Technical detail: [docs/closure-review.md](docs/closure-review.md) (no need to read unless
auditing). Deliverables: [SPEC-v1.md](SPEC-v1.md), [docs/definitions.md](docs/definitions.md).

---

## 1. What needs to be done (by whom)

- **Nothing required.** Round 11 (renames + input gate) is complete and verified; rounds 1–5
  and 9–10 were already complete (rounds 6–8: see [HANDOFF.md](HANDOFF.md)).
- Optional, owner: the name proposal in [SPEC-v1.md](SPEC-v1.md) §4 before a public release
  (default: keep the names); `graph.py`/`arcs.py` could also take a `zf_` prefix if you prefer
  uniformity (agent recommendation: keep them generic — they are general-purpose structures).
- Deferred by you (round 11): more worked examples and the guarantee display — to your
  Jupyter-notebook presentation phase. Out of scope unless you ask: building a path
  decomposition from a graph (pathwidth — your API point 2, default stands).

## 2. What is done

- **Round 11 (2026-11-23): renames + input gate (owner request; answers in HANDOFF §6).**
  Modules renamed with `git mv` (history preserved): `decomposition.py` →
  [zf/path_decomp.py](zf/path_decomp.py) (Python module names are identifiers — lowercase with
  underscores; a hyphen cannot be imported), `closure.py` → [zf/zf_closure.py](zf/zf_closure.py),
  `algorithm.py` → [zf/alg_core.py](zf/alg_core.py). Public function `zero_forcing_set` →
  **`zf_via_path_decomp`** (says "zero forcing via path decomposition"; the old name said
  nothing about the pd); internal loop function → `zf_core`. `graph.py`/`arcs.py` kept generic
  (general-purpose structures; offer to rename stands). Class names unchanged.
  **Input gate:** `_is_path_decomp(graph, bags) -> bool` in [zf/api.py](zf/api.py) checks bag
  elements are vertices, every vertex covered, D1 edge coverage, D2 contiguity; the public call
  halts with `ValueError` on False (your "halt immediately"). The core is untouched — still
  zero try/except/raise in the five core modules; the gate is the only raise in the package.
  [examples.py](examples.py) imports updated; [SPEC-v1.md](SPEC-v1.md) §§4–7 and
  [HANDOFF.md](HANDOFF.md) §6/§8 updated; [docs/pipeline-demo.html](docs/pipeline-demo.html)
  updated (names, gate, file map) and an index/name mix-up in its nice-bag timeline fixed.
  Point 3 closed as none (you do not recognize it; origin explained in HANDOFF §6).
  Verification (throwaway, deleted): 250 nice-input parity trials, 250 coarse-PD invariant
  trials vs brute-force Z(G), 125 invalid-input halts (random mutations + the two historically
  invalid inputs: non-contiguous triangle bags, K4 bags missing edge 0-3); examples pass;
  `import zf` still stdlib-only. v0.3.0.
- **Round 10 (2026-11-23): visual pipeline demonstration (owner request).**
  [docs/pipeline-demo.html](docs/pipeline-demo.html) — self-contained HTML + inline SVG, no
  dependencies, opens in any browser. §0: the whole pipeline in one figure (names → indices →
  names, trust boundary marked). §§1–4: the house graph (square 1-2-3-4-1 + roof 5, coarse
  width-2 bags) walked through every stage: the sorted bijection and the internal objects;
  `_to_nice` forget-first nicification shown as bag timelines; the L1–L8 loop step by step
  (all [L3] skips, four closure calls with the [L6c] coloring drawn — solid blue = region,
  pale blue = outside assumed blue); the fort {1,2,3,4} found at z=9; the L6 arc build with
  the min-index forcing sequence; the final `A.reverse()` drawn before/after; the output
  ZFResult in names with the guarantee 2 ≤ (2+1)·1 and the live out_arcs/in_arcs arrays.
  §5: three more inputs (C5, disconnected two-triangles with empty intermediate bags, two
  isolates). §6: file map. Every state was produced by running the shipped code at 88d1196
  and cross-checked arc-for-arc against `zf.zero_forcing_set`; the trace/generator scripts
  were deleted after use. No code change.
- **Round 9 (2026-11-21): outside API implemented (HANDOFF §8, frozen by your answers).**
  One export: `zf.zero_forcing_set(graph, bags)` — `graph` a NetworkX graph (nodes = vertex
  names), `bags` a list of sets of names forming a path decomposition (not necessarily nice).
  Returns a frozen names-based `ZFResult` (`zf_set`, `forts`, `arcs` as name pairs). New
  translation layer [zf/api.py](zf/api.py): NetworkX → internal `Graph` (sorted bijection
  reused), bags → nice decomposition via `_to_nice` (forget-first, width-preserving), run the
  unchanged core, translate back to names. The layer never imports networkx (reads
  `.nodes`/`.edges`), so `import zf` stays stdlib-only. [zf/__init__.py](zf/__init__.py) now
  exports only the one function (v0.2.0); [examples.py](examples.py) imports the internal
  core from submodules (all 8 blocks still pass). Your answers (HANDOFF §6): names-based
  result object; no suitability checking (trust, like the core); the layer must contain the
  PD→nice-PD function; point 2 = HANDOFF §4.2 (pathwidth out of scope unless asked); point 3
  not stated. Verification (throwaway script, deleted after use): 300 nice-input parity
  trials (layer == core, arc-for-arc); 300 coarse-PD invariant trials, each also on a second
  (order-based) PD shape when n ≥ 1 — S forces G via an independent simulator, forts
  valid/disjoint, |F| ≤ Z(G) ≤ |S| ≤ (w+1)|F| with brute-force Z(G), arcs replay as a forcing
  process from S, width preserved, 2n ops, determinism; explicit edge cases (empty graph,
  single vertex, isolates, disconnected two-triangles with empty intermediate bags,
  edgeless, empty/duplicate bags, star, coarse P5, K4, Petersen). Two early failures were
  invalid test inputs (an uncovered isolated vertex in the generator; non-contiguous
  triangle bags), not code bugs — fixed in the script. Core untouched. Docs: SPEC-v1 §7
  added; two stale lines in §3 below corrected.
- **Round 5 (2026-11-21): sources mask, cycle fort, index audit, commit.**
  (Item 3) Your diagnosis is right: the [L6c] full-graph closure gives correct derived colors and
  correct arcs inside the region, but `sources()` over all vertices spuriously includes the blued
  outside vertices. Your mask suggestion is viable and **already implemented**: `sources(vertices)`
  returns `sources ∩ vertices`. Demo in [examples.py](examples.py) block 8 (P6, region {1,2,3}:
  `sources()=[0,1,4,5]` vs `sources(region)=[1]`). The main algorithm needs no mid-loop mask — it
  computes `sources(A)` once at the end over all `V`. (Item 4) Audited the index/sign convention
  in code and report: `k=2n−1`, 0-based op `z−1` produces `X_z`, signs exactly `{+1,−1}` (no `0`
  op); consistent everywhere, no off-by-one to fix; SPEC §6.4 now states the sign set explicitly.
  (Point 3) Added the C5 fort example: initial blue `[0]` → white `[1,2,3,4]`, verified a fort
  (outside vertex 0 has 2 neighbors in it, not 1). Your P4 typo confirmed; both P3/P4 readings
  remain pinned. **Committed** the deliverables locally (no push, no remote change).
- **Round 4 (2026-11-21): names back + explicit examples + plain explanations.**
  (1) `Graph.to_names(vertices)` and `Graph.arcs_to_names(arcs)` translate index results back to
  the input names (the bijection was already stored both ways as `names`/`index`; these are the
  output helpers). E.g. path `a-b-c` → `S=['a']`, arcs `[('a','b'),('b','c')]`.
  (2) [examples.py](examples.py): explicit graph constructions in your notation with derived
  colorings (final blue set) in names — path `a-b-c`, P3 on `{1,2,3}`, P4 on `{1,2,3,4}`, C5
  (A=[0]→[0]; B=[0,1]→whole), star, K4; all assertions pass (`python3 examples.py`). Your P3
  example mixed 3- and 4-vertex readings (edges `[[1,2],[2,3],[3,4]]` = P4, but derived `[1,2,3]`
  = P3); both consistent readings are pinned. (3) SPEC §6 items 3–4 and the [L6c] "boundary"
  wording rewritten in plain language (no jargon); see §4 below.
- **Round 3 (2026-11-21): lean internal core, per owner ruling.** All five `zf/` modules
  rewritten: inputs are trusted as suitable; **zero** `try`/`except`/`raise`/`ValueError` in
  `zf/` (verified by scan). Removed: all input checks in `Graph`/`Arcs`/`closure`,
  `NicePathDecomposition`'s `check` parameter and `validate()`, `Arcs.copy()`, and the
  algorithm's `validate` flag. Kept unchanged: the L1–L8 loop with the [L3]/[L6b]/[L6c] tricks,
  the min-index closure canon, the name bijection, `ZFResult`. Core is now 349 lines total
  (was ~500). [SPEC-v1.md](SPEC-v1.md) §5.2 updated to the lean contract. Per your instruction
  "keep what you have into another file": the complete round-2 state (defensive core, tests,
  examples, README, then-current spec/docs/report — 16 files) is preserved verbatim in
  [zf-round2-backup.zip](zf-round2-backup.zip); `tests/`, `examples/`, `README.md` were removed
  from the active tree (they live in the backup). Verification of the lean core (throwaway
  script, deleted after use): hand cases + canon pin, **420 random invariant trials** against
  brute-force Z(G) (S forces all; forts disjoint/valid; |F| ≤ Z ≤ |S| ≤ (w+1)|F|; arcs a FAS
  with sources S), determinism, and **480 parity trials** vs the parallel project's closure
  (white + arcs identical). Active tree: `zf/`, `SPEC-v1.md`, `docs/`, `REPORT.md`, backup zip.
- **Round 2 (2026-11-21): review of the parallel project's closure**
  (`CJMZ_ZF/src/zf_npd/zf_closure.py`, read as provided, origin not investigated). Identified its
  published source: Brimkov–Fast–Hicks, EJOR 273(3):889–903, 2019, Algorithm 1 — the exact work
  our paper cites for closure (tex:L813–816); transcribed from the PDF you added
  (`resources/brimkov2018computational.pdf`). Cross-checked empirically: 960 closure trials
  (540 full-graph + 420 region-shaped) and 240 full-algorithm trials. Full write-up:
  [docs/closure-review.md](docs/closure-review.md). Verdict: same engine and same white sets
  (100%); the only behavioral difference is the forcing-order canon (§1 decision); host handling
  differs by design (reference materializes `G[host]`; this repo implements the [L6c] full-graph
  trick SPEC v0 requires). **Canon alignment approved by owner and implemented**:
  [zf/closure.py](zf/closure.py) now uses the smallest-eligible-index min-heap canon (tex:L621);
  [SPEC-v1.md](SPEC-v1.md) §5.2/§6.7 updated; one pinned-arc test updated, one canon-regression
  test added. Post-alignment: **112/112 tests pass**; shipped closure == reference arc-for-arc
  in **960/960** re-run trials; full-algorithm outputs unchanged vs the verified heap variant
  (240/240); demo correct.
- **Round 1 (2026-11-20)** — SPEC Steps 1–3 plus implementation, as below.

- **Step 1** — v0 reviewed; gaps and typos listed in [SPEC-v1.md](SPEC-v1.md) §1, §6.
- **Step 2** — paper read in full; every mathematical definition recorded one item per line in
  [docs/definitions.md](docs/definitions.md), with tex line references; the algorithm box
  (tex:L623–665) transcribed line by line (L1–L8, including sub-lines) in [SPEC-v1.md](SPEC-v1.md) §2.
- **Step 3** — v0 aligned with the paper and assessed viable (§3); names proposed (§4); the entire
  structure completed (§5): interfaces, file layout, and the main loop with all three tricks.
- **Implementation** — package `zf/` (6 modules, stdlib only):
  [graph.py](zf/graph.py) (static graph, 0-based indices, external-name bijection, edge list),
  [arcs.py](zf/arcs.py) (`out_arcs`/`in_arcs` arrays, dynamic `count`, `add`/`delete(heads)`/
  `reverse`/`extend`/`sources`), [decomposition.py](zf/decomposition.py) (`ops=(v,±1)` of length 2n,
  bags, width, D1–D4 validation), [closure.py](zf/closure.py) (queue-based forcing to fixation,
  returns white set + forcing arcs), [algorithm.py](zf/algorithm.py) (the L1–L8 loop with the
  [L3]/[L6b]/[L6c] tricks), [\_\_init\_\_.py](zf/__init__.py).
- **Verification** — 111 unit tests pass (`python3 -m unittest discover -s tests -v`):
  73 structure tests (incl. a 600-step randomized Arcs fuzz), 16 closure tests (incl. 400 random
  graph trials and 600 region checks against an independent naive simulator), 22 algorithm tests
  (280 random graphs n≤8 with random decomposition orders, plus paths/cycles/cliques/stars/
  Petersen/grids/disconnected/edgeless/empty). Every algorithm output is checked against exact
  brute-force `Z(G)`: `S` forces the whole graph; forts are non-empty, pairwise disjoint, and valid;
  `|F| ≤ Z(G) ≤ |S| ≤ (w+1)|F|`; the returned arcs form a forcing arc set with sources exactly `S`
  and `|A| = n − |S|`. Extra evidence beyond the suite: 336 trials of a standalone loop prototype
  (since deleted) and 36 extended stress trials at n=9–11, all passing.
- **Docs/examples** — [README.md](README.md) (quickstart, layout), [examples/demo.py](examples/demo.py)
  (house graph on names {1..5}: returns S={1,3}, one fort, width 2, `2 ≤ 3 = (w+1)|F|`).
- Work was parallelized per AGENTS.md rule 2: the shared API was fixed first (SPEC-v1 §5.2), then
  two subagents wrote disjoint file sets (structures; closure); I wrote the main loop, integration
  tests and docs, reviewed both agents' code, and ran the combined suite.

## 3. What is known / decided (recorded rulings — no action needed)

- **Lean internal core (decided 2026-11-21, owner):** the implementation is the core only —
  it assumes all inputs are suitable and does not touch/validate external inputs; no
  try/except, no defensive exceptions; no unasked extras in the active tree. Superseded work
  is kept in [zf-round2-backup.zip](zf-round2-backup.zip), not deleted. Recorded in SPEC-v1
  §5.2 and in project memory.
- You already know the mathematics — you are the paper's author. Nothing here asks you to confirm
  a fact from the paper; the paper statements the code relies on are cited by tex line in
  [SPEC-v1.md](SPEC-v1.md) §2.
- **Forcing-order canon (decided 2026-11-21, owner-approved):** smallest eligible index via
  min-heap, matching the parallel project and the paper's example canon (tex:L621). White sets
  and fort packings are canon-independent; arcs and hence `S` can depend on it — alignment buys
  cross-project output identity. Evidence and the B-F-H Algorithm 1 transcription:
  [docs/closure-review.md](docs/closure-review.md).
- `SPEC.md` and `resources/` are untouched (AGENTS.md rule 7); the updated spec is the new file
  [SPEC-v1.md](SPEC-v1.md). No git state was changed.
- **[L3] trick, as implemented:** an introduce step keeps `W = ∅` (the new vertex joins the bag
  blue, and adding a blue vertex never invalidates a forcing move), so the loop adds it to
  `bag`/`region` and continues without calling `closure`. Same argument, second skip: forgetting a
  vertex already in `X_t` leaves the blue set and the graph unchanged. Closure is called only when
  forgetting a vertex outside `X_t`. This is the "[L3] update" that maintains the [L6c] coloring.
- **[L6b] trick:** `S` is never maintained; (L5)/(L6b) omitted, `S = A.sources()` once at the end
  (paper remark tex:L685).
- **[L6c] trick:** no induced subgraph is ever built; `closure` runs on the full graph with
  blue = `(V \ X_t^z) ∪ X_t ∪ X_z`. Exact because contiguity (D2) forces every inside-neighbor of an
  outside vertex into `X_t ∪ X_z` (blue), so outside vertices never force. Used at (L3b), (L6c), (L7a).
- Index convention: `len(ops) = 2n`, bags `X_0..X_{2n}`, `k = 2n−1`, op `z−1` (0-based) produces `X_z`.
- Input suitability = D1–D4 + every vertex in some bag (the caller's responsibility; the lean
  core does not check it — round-3 ruling); this is weaker than the paper's connectedness
  assumption, so edgeless/disconnected graphs also work.
- **Outside API (decided 2026-11-21, owner; implemented round 9; renamed + gated round 11):**
  one public function `zf.zf_via_path_decomp(graph, bags)` (NetworkX graph + list of bags, not
  necessarily nice); frozen names-based result (`zf_set`, `forts`, `arcs`); the translation
  layer contains the PD→nice-PD function (`_to_nice`, forget-first, width-preserving) and,
  since round 11, the input gate `_is_path_decomp` (halt with `ValueError` on False — the only
  raise in the package; the core still trusts its inputs). Building a decomposition from a
  graph (pathwidth) is out of scope unless asked (owner API point 2 = HANDOFF §4.2). Point 3
  closed as none (round 11). Contract: [SPEC-v1.md](SPEC-v1.md) §7; answers:
  [HANDOFF.md](HANDOFF.md) §6.
- The whole algorithm is deterministic (the forcing-order canon is the min-index ruling
  above; the round-1 FIFO queue was superseded in round 2).

## 4. Agent findings (informational — no need to read unless auditing)

- **Round 11: path vs tree decomposition (your question).** `NicePathDecomposition` is
  path-specific: `ops` is a linear sequence and the loop's regions `X_t^z` are intervals of it;
  Algorithm 1 is stated for path decompositions. A tree decomposition would need a different
  traversal and region bookkeeping — a different algorithm, not a rename. Recorded in
  SPEC-v1 §7.4.
- **Round 11: demo bug found and fixed while updating.** The nice-bag timeline in
  [docs/pipeline-demo.html](docs/pipeline-demo.html) showed index bags under name op badges;
  now consistently in names. All other panels were already name-based.
- **Round 9: forget-first nice-ification is forced, not a preference.** Introducing before
  forgetting can inflate an intermediate bag to |X_i ∪ X_{i+1}| (e.g. {a,b}→{c,d} at width 1
  would pass through a 3-vertex bag); forgetting first keeps every intermediate bag a subset
  of one input bag, preserving width (Bodlaender–Kloks 1994, Lemma 13.1.3, tex:L580–581).
  Recorded as the convention in [SPEC-v1.md](SPEC-v1.md) §7.3.
- **Round 9: the trivial fort V is paper-faithful.** The loop evaluates W at z=k+1
  (tex:L639–642); with t=0, W = white(∅, G) = V, so V is added as a fort and the final
  A.reverse() flips the last chain (traced on P3: S={0}, arcs 0→1→2, F={V}). Hence every run
  on n≥1 returns at least one fort. SPEC-v1 §2/§7.4 updated.
- **Round 9: disconnected inputs can force empty intermediate bags.** Consecutive bags with
  empty intersection (possible only when disconnected) pass through ∅ under width-preserving
  nice-ification; the core replays ops without D3 checks and handles it correctly (verified:
  two-triangles, edgeless, isolate cases + random disconnected trials).
- **Round 9: the layer never imports networkx.** It reads graph.nodes/graph.edges (trusted,
  duck-typed), so `import zf` is stdlib-only; networkx is needed only to construct inputs
  (verified with the system python3, which has no networkx).
- **v0 typo 1 ([L6c] blue set).** v0 wrote `V \ V(G(t,z)) ∪ X_t^z`, which literally is all of `V`
  (since `X_t^z = V(G(t,z))`) and would make `W = ∅` always. Resolved to `(V \ X_t^z) ∪ X_t ∪ X_z`,
  forced by consistency with (L3b). Recorded in [SPEC-v1.md](SPEC-v1.md) §6.1.
- **v0 typo 2 (`arcs.delete`).** v0's "removes `out_arcs[j]` and `in_arc[i]`" swaps the indices;
  deleting by head `j` clears `in_arcs[j]` and `out_arcs[i]` for `i = in_arcs[j]`. Implemented that
  way — it is exactly what (L6d) needs (`A.delete(X_z)`). §6.2.
- **The [L3] skip was verified, not assumed:** a standalone prototype of the loop (naive inline
  primitives) passed 336 random trials before integration; it also caught an error in my own mental
  trace of P3 (the final `A.reverse()` flips the chain, so P3 returns the *other* endpoint).
- **The [L6c] "boundary" wording, in plain terms:** we run forcing on the whole graph but pretend
  every vertex outside the current region is already blue. Those outside vertices never force,
  because they only touch the region through the bag `X_t ∪ X_z` (which is blue) — so they have no
  white neighbor. That fact is guaranteed by contiguity (D2) for the algorithm's regions; it can
  fail for an arbitrary vertex subset, but the algorithm never uses one. ("Boundary condition"
  was just a name for this fact; the docs now say it plainly.)
- **Brute-force sanity:** `Z(Petersen) = 5` reproduced; `Z(K_n) = n−1`, `Z(K_{1,k}) = k−1`,
  `Z(P_n) = 1` all matched by the returned sets where the decomposition allowed it.
- The two subagents resolved minor contract edge cases (out-of-range indices → `ValueError`,
  atomic `extend`, `from_bags([])` → `ValueError`); all resolutions are documented in their test
  files and consistent with SPEC-v1 §5.2. One integrator fix afterwards: non-comparable external
  names now raise `ValueError` (was `TypeError`) in `Graph`.