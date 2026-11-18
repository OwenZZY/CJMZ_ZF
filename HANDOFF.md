# HANDOFF — zf-approx

**Current stage: 0 — close read of the paper.**
**Current step: 0.1 — definitions and notation ledger** (draft posted in chat on 2026-11-18; awaiting Owen's sign-off before anything is written to `docs/paper-notes.md`).
**Updated: 2026-11-18**

Paper: B. Cameron, J. Janssen, R. Mathew, Z. Zhang,
*An approximation algorithm for zero forcing*, [arXiv:2402.08866v1](https://arxiv.org/abs/2402.08866).
Source is kept read-only in `docs/arXiv-2402.08866v1/` (`.tex`, `.bbl`, `.bib`).

## Read order for a cold start

1. `HANDOFF.md` — this file.
2. `AGENTS.md` — working agreement and stage protocol.
3. `SPEC.md` — normative contract (appears in Stage 1).
4. `docs/paper-notes.md` — the paper as read; context only, never normative.

## Files and their job

| file | job | status |
|---|---|---|
| `HANDOFF.md` | state, decisions, next action — the checkpoint a fresh agent resumes from | live |
| `SPEC.md` | normative contract; self-contained and prompt-ready (see C2) | Stage 1 |
| `docs/paper-notes.md` | descriptive transcription: definitions, pseudocode, theorem ledger | Stage 0 |
| `AGENTS.md` | working agreement, stage protocol | live; patch pending (step 1.1) |
| `src/`, `tests/`, `README.md`, `LICENSE`, `pyproject.toml` | code, tests, user docs, license, packaging | Stages 2–5 |

## Stage ladder

| stage | deliverable | gate |
|---|---|---|
| 0 close read | `docs/paper-notes.md` | Owen signs off each of 0.1–0.4 |
| 1 spec | `SPEC.md` | every open `D#` closed; SPEC passes the C2 self-containment test |
| 2 oracle | exact `Z`/pathwidth reference + graph generators | oracle matches hand-computed values on a fixed benchmark |
| 3 implementation | `src/` | differential tests vs oracle + invariant tests green |
| 4 evidence | full test suite, experiments | certificates hold on all generated inputs; scaling reported |
| 5 release | packaging, README, LICENSE, CI | fresh clone, one command reproduces results |

Sub-steps: 0.1 definitions · 0.2 algorithm pseudocode · 0.3 theorem ledger
(load-bearing vs context) · 0.4 ambiguity list `A#`.
Stage 1 sub-steps: 1.1 process files · 1.2 data model + primitives · 1.3 main
algorithm + invariants · 1.4 certificates + acceptance tests · 1.5 complexity
+ API + environment.

## Closed decisions

- **C1** Repo documentation is GitHub-flavoured Markdown with `$...$` math; the
  `.tex` source is reference only. (2026-11-18)
- **C2** `SPEC.md` is a single self-contained file from which a strong model can
  implement without access to the paper: definitions restated, exact
  pseudocode, data structures, invariants, literal runnable acceptance tests,
  golden traces pinning tie-breaking, and a completion checklist. (2026-11-18)
- **C3** Profile `desktop` gained the official bundle
  `@deepseek-ai/dsh-experimental-session-search@0.2.2-rc.5` (tools to search and
  read earlier sessions in this workspace), requested by Owen for cross-session
  recall. Installed; **DSH restart required to activate**. No other profile
  changes. (2026-11-18)
- **C4** The workspace is a local git repository on `main` (remote per C5). One
  accepted step = one commit whose message summarises the HANDOFF delta, and the
  HANDOFF is updated in that same commit. The arXiv source is gitignored (local
  reference only). (2026-11-18)
- **C5** This project's remote is the existing public repo
  `https://github.com/OwenZZY/CJMZ_ZF` — the repository the paper cites as its
  Python implementation. Its current content is replaced wholesale by this
  project at the v0.1.0 release; nothing is pushed before then. The legacy tip
  `93fbfdbe01f015723694eb059bd76fe11e7709a7` (`main`, 2026-11-18) is preserved
  under a `legacy` tag before the first push. Remote is configured locally as
  `origin`; no fetch or push has been performed. (2026-11-18)

## Open decisions

- **D1** Canonical `fas(S, G)` tie-breaking rule — determines determinism and
  whether the paper's $O(nm)$ claim survives implementation. (Stage 1.2)
- **D2** Input scope: path decomposition given vs. also computed; which graph
  classes are supported. (Stage 1.2)
- **D3** Python floor and runtime dependency policy (stdlib-only core vs.
  `networkx`). (Stage 1.5)
- **D5** Dev environment and packaging: `pyproject.toml`, `src/` layout,
  `.venv/` gitignored and never committed, `.gitignore` contents. (Stage 1.5 / 3)

## Release plan for v0.1.0 (agreed; do not execute early)

Nothing is pushed before v0.1.0. Then, in this order:

1. `git fetch origin`
2. `git tag legacy 93fbfdb && git push origin legacy` — preserve the old
   implementation; if this fails, stop and do not continue.
3. `git push --force origin main` — repo content becomes this project.
4. On GitHub: confirm `main` is default; then README, release notes, citation.

Push authentication is not configured in this session (`gh` CLI absent); Owen
may need to supply credentials, or we switch `origin` to SSH before release.

## Deferred to Stage 5

LICENSE (type and copyright line); package/registry name; CI provider and
badges; docs site; README wording; versioning scheme; Zenodo DOI / arXiv link
in README.

## Open questions for Owen

- **Q2** (D2) May v1 require a path decomposition as input, i.e. ship no
  pathwidth solver?
- **Q3** (0.3) Beyond the three output guarantees (ZF set, fort packing,
  ratio), which paper results should the release demonstrate empirically?
- **Q4** (C5) Must the new implementation reproduce the *legacy* CJMZ_ZF
  outputs exactly, or only the paper's guarantees? Black-box comparison against
  the `legacy` tag is possible at Stage 4 if wanted.

## Guards

Why earlier attempts went wrong, and what we do instead:

- "It runs" is not correctness → every output carries checkable certificates;
  small cases are checked against an exact oracle.
- Tie-breaking drift → the canonical forcing rule is fixed once in `SPEC.md` and
  pinned by golden traces.
- Spec as prose summary → `SPEC.md` must be implementable without the paper (C2).
- Contamination → do not read the legacy CJMZ_ZF source during implementation;
  it stays available in the `legacy` tag for black-box output comparison only
  (Q4), not as a design reference.
- Scope creep → pathwidth computation, treewidth and PSD variants are out of
  scope unless a `D#` says otherwise.

## Next action

Draft step 0.1 (definitions and notation ledger) in chat for review; on approval
write it to `docs/paper-notes.md`.

## Changelog

- 2026-11-18 created. Workspace inspected; paper read end-to-end; Stage 0
  started. No other artifacts written yet.
- 2026-11-18 installed official session-search bundle (restart pending);
  step 0.1 definitions ledger drafted in chat for review. `HANDOFF.md` updated
  in the same turn per protocol.
- 2026-11-18 initialised the local git repository (no remote); first commit
  holds `AGENTS.md`, `HANDOFF.md` and `.gitignore`. Step 0.1 still awaiting
  sign-off.
- 2026-11-18 repo decision: reuse `OwenZZY/CJMZ_ZF` (the repo the paper cites)
  as the artifact's home, replaced at v0.1.0, old tip preserved as `legacy`.
  `origin` configured; nothing fetched or pushed. D4 and D6 closed, C5 added.
