# HANDOFF — zf-approx

**Where to take off:** read §1 (design principles) and §8 (the outside API — frozen by the
owner's answers and implemented in round 9). Remaining optional items are §4; the owner's
recorded answers are §6. Current status is §2, git is §3. The core deliverables are committed
at `76700f8`; the round-9 outside API is committed on top (local, not pushed — run `git log`).

---

## 1. Design principles (owner rulings — carry these forward)

- **Mathematical origin, not software engineering.** Implement the algorithm; no correctness
  proofs or complexity analysis in the deliverables (AGENTS.md rule 1).
- **One interface with the outside.** Internally, minimal `try`/`except` — only where necessary.
  The core trusts that the inputs are suitable; it does not check or clean them.
- **Core only:** the input/output objects and the main loop. No unasked extras (tests, README,
  etc.) without offering first.
- **Confirm scope before building.** When unsure of a requirement, ask the owner one concise
  question with a stated default (skipping must be safe).
- **Report style:** four buckets (owner knows / decided / to-decide / agent findings), reading
  guide at the top, plain self-contained items, no verification busywork. The owner is the
  paper's author — never ask him to confirm facts from his own paper; resolve and record them.

## 2. Current status (rounds 1–5 and 9, 2026-11-20/21)

**Done and verified:**
- Lean core `zf/` (core ~370 lines, 6 modules; round 9 adds the 98-line `api.py` layer),
  **zero** `try`/`except`/`raise`:
  - `graph.py` — `Graph`: static, 0-based, name bijection (`names` index→name, `index` name→index),
    edge list, `adj`; output views `to_names(vertices)` and `arcs_to_names(arcs)`.
  - `arcs.py` — `Arcs`: `out_arcs`/`in_arcs` (−1 = absent), dynamic `count`/`__len__`,
    `add`/`delete(heads)`/`reverse`/`extend`/`sources(vertices=None)`/`arcs()`.
  - `decomposition.py` — `NicePathDecomposition`: `ops=(v,±1)`, `bags`/`k`/`width`, `from_bags`;
    no validation.
  - `closure.py` — `closure(graph, blue) -> (white, arcs)`: Brimkov–Fast–Hicks count engine
    (complementary white counts), **min-index canon** (min-heap), stale-entry guard.
  - `algorithm.py` — `zero_forcing_set(graph, pd) -> ZFResult(zf_set, forts, arcs)`:
    Algorithm L1–L8 with the three tricks.
- **Tricks:** [L3] introduce steps and forgets of vertices in `X_t` skip closure; [L6b] `S`
  computed once at the end (`A.sources()`); [L6c] closure on the FULL graph with outside vertices
  blued (no induced subgraph ever built).
- **Canon:** smallest-eligible-index = paper tex:L621 = the parallel project's `zf_closure.py`;
  arc-for-arc parity verified (960/960 round 2; 480/480 round 3).
- `examples.py` — 8 explicit blocks (path a-b-c, P3, P4, C5 A/B, star, K4, C5 fort from `[0]`,
  sources-mask demo); all assertions pass (`python3 examples.py`).
- Round 9 (2026-11-21): **outside API implemented** — `zf/api.py` (translation layer: NetworkX
  graph + list of bags → nice-ification → unchanged core → names-based result); `zf/__init__.py`
  exports only `zero_forcing_set`. Frozen contract and conventions: §8. Verified by throwaway
  script (deleted after use): nice-input parity with the core, brute-force invariants on random
  graphs incl. disconnected/edgeless, width preservation, determinism.
- Docs: `SPEC-v1.md` (living spec, lean contract), `docs/definitions.md` (all math definitions,
  one per line), `docs/closure-review.md` (B-F-H comparison), `REPORT.md` (rounds 1–5, 9).
- Backup: `zf-round2-backup.zip` = round-2 defensive core + 112-test suite + examples + README,
  preserved verbatim.

**Key math facts (do not re-derive):**
- Indexing: `ops` length `2n`; `k = 2n−1` non-empty bags; 0-based op `z−1` produces `X_z`; signs
  exactly `{+1, −1}` (no `0` op). Audited correct in code and report.
- `sources(vertices)` = `sources ∩ mask`: needed because [L6c] blues outside vertices, which
  otherwise appear as spurious sources. The main algorithm computes `sources(A)` once at the end
  over all `V`, so it needs no mid-loop mask.
- Input suitability = D1–D4 + every vertex in some bag; the caller's responsibility (weaker than
  the paper's connectedness assumption, so edgeless/disconnected graphs work).
- Paper: arXiv:2402.08866v1. Algorithm box tex:L623–665; canon tex:L621; "S once at end" remark
  tex:L685; closure subroutine = Brimkov–Fast–Hicks, EJOR 273(3):889–903 (2019), Algorithm 1.
  Local tex: `resources/paper/arXiv-2402.08866v1/2024-02-13-Zero_Forcing_Approx_Alg.tex`.

## 3. Git state

- The core deliverables are in commit `76700f8` (12 files). This handoff is committed on top of
  it (the latest commit — run `git log` to see its hash). Everything is local; nothing is pushed.
- Files in the repository: the 12 deliverables, this handoff, and the baseline `.gitignore`,
  `AGENTS.md`, `HANDOFF.md`.
- Left as-is (not committed): your edit to `AGENTS.md`. Never added to the repository:
  `SPEC.md` (your v0), `resources/` (the papers), `spec2` (not created by me).
- No push and no remote change (AGENTS.md rule 7).

## 4. What I expect to do next round (I will confirm scope with you first)

**Round-9 status (2026-11-21):** item 1 done — scope confirmed by your answers (§6), API frozen
and implemented (§8). Items 2–4: defaults stand (you did not ask). Item 5 done this round.
Item 6 closed (numbering correct).

1. **One function for the outside.** Today the package exposes several names (`Graph`, `Arcs`,
   `NicePathDecomposition`, `closure`, `zero_forcing_set`, `ZFResult`). You asked for a single
   interface, so I would hide the helpers and leave just one function for you to call.
   *Done (round 9). The design is §8 (graph given as NetworkX; a translation layer in between).
   Your answer on the return shape and API points 2 and 3 is recorded in §6.*
2. **Where the decomposition comes from.** Today you supply a ready-made nice path decomposition
   (the list of add/remove steps). Building one from a graph is a separate algorithm (pathwidth).
   *Default: not part of this project unless you ask.*
3. **More worked examples.** Name the graphs you want and I will work them through.
   *Default: only when you ask.*
4. **Show the guarantee directly.** The result already satisfies: size of the zero forcing set
   ≤ (width + 1) × (number of forts). I can display this comparison more directly if it helps.
   *Default: only when you ask.*
5. **Keep the spec (`SPEC-v1.md`) and the report (`REPORT.md`) current** each round.
6. **The numbering question** in §5, if you still see a problem.

## 5. Open questions (answer in one line; if you skip, the default applies)

**All resolved (2026-11-21):** one function — yes, implemented (§8); left-out files — stay out
(default applied); numbering — correct (default applied, round-5 audit stands).

- **Just one function?** Should the package give you only one function to call from outside —
  you pass in a graph and its decomposition, and it returns the zero forcing set, the forts, and
  the arcs, all using your original vertex names — with every helper hidden inside?
  *Default: yes; that one function is `zero_forcing_set`.*
- **Add the left-out files to git?** Your v0 `SPEC.md`, the paper PDFs in `resources/`, and
  `spec2` are not in the repository right now. Should I add them?
  *Default: leave them out.*
- **Any numbering mistake left?** I checked the add/remove step numbering and the +1/−1 signs
  and found them correct. Do you still see a specific place where a number is off by one? If so,
  tell me the file and line.
  *Default: it is correct; nothing to change.*

## 6. Owner comment area (please fill in — feedback / where to take off)

**Owner answers given in chat 2026-11-21, recorded by the agent (round 9):**

> - Where should the next chat begin?
>   - (not answered; agent note: the outside API is now implemented — begin from §8.)
> - What should the one outside function take as input, and give back?
>   - Input: as §8 point 1 (NetworkX graph + list of bags). Give back: **a result object in the
>     original vertex names** (owner chose the recommended default: `zf_set`, `forts`, `arcs`
>     all in names).
> - Which graphs or examples do you want next?
>   - (not answered; default: only when asked.)
> - Is anything in the "key math facts" (§2) wrong?
>   - (not answered; no correction given — facts stand.)
> - What is in scope / out of scope for next round?
>   - (not answered directly; see API point 2 below — pathwidth construction stays out unless
>     asked.)
> - API points 2 and 3 (see §8 — point 1 is recorded):
>   - **Point 2 (owner, verbatim):** "Where the decomposition comes from. Today you supply a
>     ready-made nice path decomposition (the list of add/remove steps). Building one from a
>     graph is a separate algorithm (pathwidth). *Default: not part of this project unless you
>     ask.*" — This is §4 item 2; it was recorded there but never carried into §8. The default
>     stands: the caller supplies the bags; the layer makes them nice; building a decomposition
>     from a graph (pathwidth) is out of scope unless asked.
>   - **Point 3:** not stated. Proceeding without it; fold it in whenever given.
> - Anything else:
>   - **On trust vs checking (owner, verbatim):** "No, in fact, the translation (transition)
>     layer should involve a function that making a path decomposition into a nice p-d" —
>     read as: no suitability checking (trust, like the core); the layer must contain an
>     explicit function turning a path decomposition into a nice one. Implemented as
>     `_to_nice` in `zf/api.py` (round 9).

## 7. Pointers

- Spec: `SPEC-v1.md` · definitions: `docs/definitions.md` · review: `docs/closure-review.md` ·
  status: `REPORT.md`.
- Examples: `examples.py` (`python3 examples.py`).
- Prior work + tests: `zf-round2-backup.zip`.
- Paper: `resources/paper/arXiv-2402.08866v1/` · Brimkov PDFs: `resources/brimkov*.pdf`.

## 8. Outside API — frozen and implemented (round-8 design; round-9 implementation, 2026-11-21)

Owner's point 1 is below. Point 2 was identified by the owner on 2026-11-21 (§6): it is the
decomposition-provenance item of §4.2, and its default stands (pathwidth construction out of
scope unless asked). Point 3 was not stated; proceeding without it.

**The shape (I agree).** One function is the only thing the outside world calls. It takes two
things:
- a graph, given as a **NetworkX graph** (`networkx.Graph`: simple, undirected; its nodes are the
  vertex names), and
- a **list of bags** (each bag a set of vertex names) forming a path decomposition — it does
  **not** have to be "nice".

Between that function and the lean core sits a **translation layer** — the only place that
touches external formats. It turns the NetworkX graph into the internal `Graph` (0-based indices
plus the name bijection), and the list of bags into the internal `NicePathDecomposition`. The
core then runs unchanged on indices, and the layer translates the answer (zero forcing set,
forts, arcs) back into the original names. This gives exactly "one interface outside, lean
internal core": the core keeps trusting suitable inputs; all format handling lives in the layer.

**Fixed choice — NetworkX (one graph type, not two).** Of the two options offered (NetworkX or
an edge list), I fix **NetworkX** as the single outside graph type, because:
- its nodes already are the vertex names, and it includes isolated vertices (an edge list alone
  loses isolated vertices, which the bags must still cover);
- it is the standard graph object in the mathematics/algorithm community, so a public release
  interoperates naturally;
- the dependency is confined to the translation layer — the core stays standard-library only.

If a zero-dependency package is preferred, the fallback is one fixed edge-list format; say so and
I will switch. Otherwise NetworkX stands. The bags are fixed as a **list of sets of names**.

**What the translation layer must do (next-round implementation items):**
1. NetworkX graph → internal `Graph` (sort names to indices; edges; adjacency).
2. List of bags → internal nice decomposition. Since the bags need not be nice, this step must
   **make the decomposition nice**: pad empty end bags and replace any multi-vertex bag-to-bag
   change with a sequence of single-vertex add/remove steps, keeping the path-decomposition
   properties. (Standard "nice-ification"; the paper cites Bodlaender–Kloks, Lemma 13.1.3.)
3. Run the core; translate the result back to names.

**Decided (owner, 2026-11-21 — §6):** the layer does **not** check suitability; it trusts
suitable inputs, consistent with the core. It **must contain an explicit function that makes a
path decomposition nice** — implemented as `_to_nice` in `zf/api.py`.

**Owner API points 2 and 3:** point 2 = §4.2 (decomposition provenance; default stands: the
caller supplies bags, building one from a graph is out of scope unless asked). Point 3: not
stated; fold in when given.

**Implemented (round 9) — the frozen contract:**
- `zf.zero_forcing_set(graph, bags)` is the only export (`zf/__init__.py`). `graph` is a
  `networkx.Graph` (simple, undirected; nodes = vertex names); `bags` is a list of sets of
  names forming a path decomposition (D1/D2 + every vertex in some bag; not necessarily nice).
- Returns a frozen `ZFResult` (in `zf/api.py`) **in the original names**: `zf_set` (tuple of
  names, sorted), `forts` (tuple of frozensets of names, in discovery order), `arcs` (tuple of
  `(name, name)` pairs, sorted by tail).
- Nice-ification convention (`_to_nice`, forget-first — forced by width preservation): drop
  empty and consecutive-duplicate bags, pad empty ends implicitly; between consecutive bags
  forget `X_i \ X_{i+1}` in increasing index order, then introduce `X_{i+1} \ X_i` in increasing
  index order. Every input bag appears verbatim; width is preserved; each vertex is introduced
  once and forgotten once. For disconnected inputs, consecutive bags may have empty
  intersection; the width-preserving sequence then passes through an empty intermediate bag
  (D3 relaxed). The core replays ops without D3 checks and handles this correctly (verified).
- The layer never imports networkx: it reads `graph.nodes` / `graph.edges` (trusted, duck-typed),
  so `import zf` stays standard-library-only; networkx is needed only to construct inputs.
- The core (`zf/graph.py`, `arcs.py`, `decomposition.py`, `closure.py`, `algorithm.py`) is
  unchanged; helpers remain importable from their modules but are no longer package exports.
  `examples.py` now imports them from the submodules.