# Closure review — reference `zf_npd/zf_closure.py` vs `zf/closure.py`

Round 2 (2026-11-20). Compares the closure primitive of the parallel project
(`/Users/OwenZhang/CherryStudioWare/CJMZ_ZF/src/zf_npd/zf_closure.py`, read-only,
reviewed as provided) with this repo's [zf/closure.py](../zf/closure.py), against the
published pseudocode it descends from.

## The published pseudocode

Brimkov–Fast–Hicks, *Computational approaches for zero forcing and related problems*,
European J. Oper. Res. 273(3):889–903, 2019 — the work our paper cites for the closure
subroutine (tex:L813–816, bib key `BrimkovFastHicks2019`). Local copy:
`resources/brimkov2018computational.pdf`, **Algorithm 1** ("Finding the closure of a set
in O(n+m) time"), transcribed:

```
Data: G = (V,E), Z ⊆ V.  Result: cl(Z).
1  colored ← zeros(n);  count ← zeros(n)
2  for v ∈ Z: colored(v) ← 1
3  for v ∈ Z:
4      count(v) ← Σ_{y∈N(v)} colored(y)
5      if count(v) = d(v) − 1: push(v)
6  while Stack not empty:
7      pop(u)
8      v ← the y ∈ N(u) with colored(y) = 0
9      colored(v) ← 1
10     for w ∈ N(v):
11         if colored(w) = 1:
12             count(w) ← count(w) + 1
13             if count(w) = d(w) − 1: push(w)
14     count(v) ← Σ_{y∈N(v)} colored(y)
15     if count(v) = d(v) − 1: push(v)
16 return {v : colored(v) = 1}
```

The other three Brimkov PDFs in `resources/` contain no closure engine (2017: complexity;
2021: greedy minimal-violated-set algorithm; 2022: claw-free approximation).

## Three-way comparison

| aspect | B-F-H Algorithm 1 (printed) | reference `zf_closure.py` | this repo `zf/closure.py` |
|---|---|---|---|
| count scheme | `count` = #colored neighbors; eligible iff `count = d−1` | identical, verbatim (lines 71–74, 84–91) | complementary: `white_count` = #white neighbors; eligible iff `= 1` (equivalent) |
| updates on force | increment blue neighbors of `v`, push at `d−1`; recompute `count(v)`, push if eligible | identical | identical (decrement form) |
| container / order | **Stack** (LIFO; order unspecified) | **min-heap keyed by vertex id** = smallest eligible forcer | **min-heap keyed by vertex id** (aligned 2026-11-21; FIFO at review time) |
| canon source | none stated | our paper's example canon, tex:L621 ("eligible blue vertex of the lowest index") | same canon, tex:L621 (owner-approved alignment; SPEC-v1 §5.2, §6.7) |
| stale-entry guard | **absent** (line 8 presupposes a white neighbor) | present (`w is None → continue`) | present (`white_count[u] != 1 → skip`) |
| host / subgraph | none (full graph) | materializes `G[host]` (`induced_subgraph`; outside vertices isolated and blue) | no induced subgraph: full `G`, outside vertices blue — the [L6c] trick required by SPEC v0 |
| outputs | `cl(Z)` only | `(W bytearray mask, ArcSet)`; early exit when no white | `(sorted white list, arc pair list)` |
| per-call cost | O(n+m) (Prop. 1) | O((n+m) log n) (its docstring; heap) | O((n+m) log n) (heap, as the reference) |

## Findings

(Observations 2–4 record the pre-alignment state; the canon was aligned on 2026-11-21 — see
Decision below.)

1. **Same engine, same closure.** All three maintain the B-F-H count invariant and produce
   the same derived coloring. Verified: white sets agreed in **540/540** random full-graph
   trials and **420/420** region trials (region = random `R`, blue = outside ∪ boundary ∪ random
   inside, i.e. exactly the main algorithm's [L6c] call shape).
2. **The only behavioral difference is the forcing-order canon.** With my engine switched to
   the min-heap canon, arcs matched the reference **arc-for-arc in 960/960 trials** (540 full +
   420 region). As shipped (FIFO), arcs matched in 488/540 and 411/420. The literal B-F-H
   stack matched the reference in 396/540 — the printed LIFO order is a *third* canon.
3. **Canonical-order divergence is real but benign for correctness.** Example: P4 (0-1-2-3)
   from {0,3}: FIFO arcs `[(0,1),(3,2)]` (two chains); reference/min-index `[(0,1),(1,2)]`
   (one chain, 3 idle); B-F-H stack `[(3,2),(2,1)]`. White = ∅ in all three.
4. **Main-algorithm consequence.** Over 240 random graph+decomposition trials, FIFO vs
   min-index canon: fort packing `F` identical in **240/240** (white sets are unique),
   arcs differ in 70, returned zero forcing set `S` differs in **68 (28%)** — e.g.
   n=4, edges [(0,1),(0,2),(0,3),(1,2),(2,3)], order [2,3,0,1]: `S=(0,3)` (FIFO) vs
   `S=(2,3)` (min-index), same fort {0,2,3}. Both outputs satisfy every paper guarantee;
   only cross-project output identity is affected.
5. **Both implementations repair a gap in the printed pseudocode.** B-F-H line 8 assumes the
   popped vertex still has a white neighbor; it can be stale. P4 from {0,3}: after 3 forces 2
   and 2 forces 1, the seeded vertex 0 pops with no white neighbor (line 8 undefined). The
   reference's `w is None` guard and my `white_count != 1` guard both fix this; the O(n+m)
   bound is unaffected. So the reference is "B-F-H engine + our paper's canon + guard", not a
   literal transcription of the printed Stack algorithm.
6. **Host handling differs by design.** The reference materializes `G[host]` (literal
   `white(S, G(t,z))` semantics, valid for arbitrary hosts). This repo implements SPEC v0's
   [L6c] trick: closure on the full graph with outside blue, no induced subgraph. The two are
   equivalent whenever every inside-neighbor of an outside vertex is initially blue — which
   contiguity (D2) guarantees for the algorithm's regions `X_t^z` with blue ⊇ `X_t ∪ X_z`
   (SPEC-v1 §5.4). In plain words, the "boundary condition" just means: *an outside vertex only
   touches the region through the bag `X_t ∪ X_z`, which is blue, so it has no white neighbor and
   can never force.* For arbitrary host/blue they differ: the full-graph version lets an outside
   vertex force its unique white neighbor; the induced version cannot. The main algorithm
   never makes such calls. (Illustrated in `examples.py`; earlier test pins are in the project
   archive.)
7. **Interface differences are cosmetic:** bytearray masks + `ArcSet` + early exit vs iterable
   blue + pair list; `shift_by` is an arc name-space offset in the reference, irrelevant to the
   engine. No semantic impact.

## Verdict

The reference matches this repo's closure in mathematics, engine, and white-set output
(100% agreement, 960 trials). It differs in (a) forcing-order canon — min-index heap (our
paper's example canon) vs FIFO — which can change the arcs and hence the final `S` (never `F`),
and (b) host handling — materialized induced subgraph vs the [L6c] full-graph trick this
project's SPEC explicitly requires. Aligning the canon makes the two implementations
arc-for-arc identical (verified with a heap variant of this repo's engine).

## Decision (resolved 2026-11-21)

Owner approved alignment: this repo's `closure` now uses the smallest-eligible-index canon
(min-heap), matching the reference and tex:L621. Implemented in [zf/closure.py](../zf/closure.py);
SPEC-v1 §5.2 and §6.7 updated; one pinned-arc test updated and a canon-regression test added
(P4 from {0,3} → `[(0,1),(1,2)]`). Post-alignment verification: **112/112 unit tests pass**
(all algorithm invariants re-checked against brute force under the new canon); parity re-run:
shipped closure == reference **arc-for-arc in 960/960 trials** (540 full-graph + 420 region),
zero divergences; full-algorithm outputs identical to the verified heap variant in 240/240
trials; demo unchanged and correct. Trade-off accepted: heap log-factor per closure call.

Reproduction harness: `scratch/closure_compare.py` (temporary, deleted after verification;
methodology: load the reference via exec with shims for its documented interface, write nothing
to the other project).