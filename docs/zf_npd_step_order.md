# `zf_npd` — Driver Step Order (authoritative record)

Status: design record for the L3 driver (Algorithm 4.2, Cameron–Janssen–Mathew–
Zhang, arXiv:2402.08866v1). Correctness is by the paper's proof (Thm 4.6–4.8);
the implementation performs every step faithfully — nothing added, removed, or
reordered. Per decision: no runtime correctness verification; the driver assumes
the contracts below.

---

## Files and roles (interface contract the driver imposes)

| File | Contract required by the driver |
|---|---|
| `zf_graph.py` | frozen; `n`; `adj` ascending per vertex (determinism); simple undirected |
| `nice_pd.py` | `k`, `width`; `mask_of(i) -> bytes` for all `0 ≤ i ≤ k+1`; `op(z) -> (v, is_insert)` for all `1 ≤ z ≤ k+1`; D1–D4 validated at construction |
| `zf_closure.py` | `__init__(adj)` binds read-only adjacency; `white(blue, host) -> bytearray` (deque, $O(n+m)$); `fas(blue, host) -> ArcSet` (min-heap canon, $O((n+m)\log n)$); read-only inputs; engine spec in §"Closure engine" |
| `zf_arcset.py` | `reverse()` mutator; `extend(other)`; `delete_heads(mask)`; `sources()`; `arcs()`; `__len__` |
| `zf_npd.py` | driver — this record |

Mask conventions: `bytes` for frozen bag masks (immutable, served by `NicePD`);
`bytearray` for driver-owned masks. One byte per vertex, value 0 or 1.

CPython caveat: `bytearray`/`bytes` do NOT support `|`, `&`, or `|=` between
masks (only `+` concatenation). All set operations go through small helpers:
- union into: `_mask_or(dst, src)` — `for i, b in enumerate(src): if b: dst[i] = 1`
- disjointness / intersection: element-wise scan (no built-in `&`)
- deletion: `mask[v] = 0`
Do not use `a | b` on masks in the implementation. `_mask_or` is a module-local
helper of `zf_npd.py` (driver-only); the closure reads masks but never unions.

---

## Host design: what `host` is

$G(t,z) = G[X_t^z]$ is **never materialized** as a graph object. It is represented
by the pair `(g.adj, host)`:

- `host` is a `bytearray` of length $n$; `host[u] == 1` iff $u \in X_t^z$. It is
  exactly the running union at all times.
- Monotonicity: $X_t^z$ is a union of bags, so an **insert adds the vertex** to
  `host`; a **delete changes nothing** (removing a vertex from a bag never removes
  it from the union). Only the current-bag mask `bag` shrinks on delete.
- Engine semantics: a vertex exists iff `host[v] == 1`; a blue vertex $u$'s white
  neighbors are its neighbors $w$ in `g.adj` with `host[w] == 1` and currently
  white; vertices outside `host` are invisible (induced-subgraph forcing).
- Invariant of every driver call: `blue ⊆ host` (blue $= X_t \cup X_z \subseteq X_t^z$).
- I/O: `blue` and `host` are read-only to the engine (the driver reuses `host`
  across steps within a segment); `white` returns a **fresh** mask; `fas` returns
  a fresh `ArcSet`. Engine holds only `adj` between calls. $O(n+m)$ per call.
- Edge: `host` all-zero (empty induced subgraph, e.g. segment $t = k+1$) →
  `white` returns all-zero mask, `fas` returns empty `ArcSet`.
- `fas` canon (paper): exactly one vertex forced per step; among eligible blue
  vertices (exactly one white neighbour in host), choose the smallest index.

## Closure engine — exact design (`white` / `fas`)

STATUS: implemented in `src/zf_npd/zf_closure.py` (class `zf_closure`);
`white`, `fas`, `white_and_fas` follow this section literally.

The induced subgraph $G(t,z)$ is the **view pair `(self.adj, host)`**; no Graph
object is ever constructed. The engine binds `adj` once in `__init__` (read-only,
stored between calls) and receives `host` per call. All per-call state is local:
`col` (engine-owned colour copy), `cnt` (white-neighbour counts), a queue.

Shared core (one pass; `white` and `fas` differ only in queue type and whether
arcs are recorded):

```python
# per call; self.adj = bound adjacency of G (read-only)
col = bytearray(blue)                       # engine-owned copy; input blue is read-only
cnt = [0] * n                               # cnt[u] = # white neighbours of u inside host
# init — one scan of the host's adjacency lists: O(n + m)
for v in range(n):
    if host[v]:
        for w in self.adj[v]:
            if host[w] and not col[w]:
                cnt[v] += 1
q = deque()  or  heap                       # white(): deque; fas(): min-heap keyed by id
for v in range(n):
    if host[v] and col[v] and cnt[v] == 1:
        push(q, v)
while q:
    u = pop(q)
    if not (host[u] and col[u]) or cnt[u] != 1:
        continue                    # stale: unique white neighbour already turned blue
    w = the unique w in self.adj[u] with host[w] and not col[w]  # exists iff cnt[u]==1
    col[w] = 1                      # u forces w
    record arc (u, w) if fas
    for x in self.adj[w]:           # w turned blue -> update its host neighbours
        if host[x]:
            cnt[x] -= 1
            if col[x] and cnt[x] == 1:
                push(q, x)
    if cnt[w] == 1:                 # newly blue w itself may be eligible
        push(q, w)
```

- `white`: run core with a deque; return a fresh mask `wmask` with
  `wmask[v] = 1` iff `host[v] and not col[v]`, built by an explicit loop
  (bytearrays have no `&`/`~` operators). Result independent of pop order
  (derived colouring is unique), so no tie-breaking needed.
- `fas`: run core with a min-heap keyed by vertex id (smallest eligible index
  pops first = paper canon); collect arcs, build a fresh `ArcSet` via
  `ArcSet.add` (P1 asserted per arc), return it. The driver merges with
  `ArcSet.extend`.
- Read-only contract: engine never mutates `blue` or `host`; per-call arrays are
  locals (the engine stores no colouring/arcs between calls).
- Load-bearing details:
  (i)  **stale-skip at pop** — a queued $u$ can lose its unique white neighbour
       before it pops, so eligibility must be re-checked at pop time;
  (ii) **check the newly forced vertex itself** — after `col[w] = 1`, if
       `cnt[w] == 1` then $w$ is eligible and is not reached by the neighbour
       loop, so it must be pushed explicitly;
  (iii) each vertex turns blue at most once, so the decrement loop scans each
        adjacency list at most once in total; each successful forcer scans its
        list at most once — `white` is $O(n+m)$ (matches paper Prop 4.11);
        `fas` with a heap is $O((n+m)\log n)$ (fine under the $O(nm)$ budget).
- `fas` return-type annotation: `ArcSet` (the old name `zf_arcs` must not be
  used). `__init__` accepts any sequence-of-sequences adjacency (Graph.adj is a
  tuple of tuples).

### Why the engine works (invariant + worked example)

Loop invariant: after every mutation,
$cnt[u] = |\{w \in adj[u] : host[w]=1 \wedge col[w]=0\}|$.
Init establishes it (one filtered scan); forcing $w$ (setting $col[w]=1$)
decrements $cnt[x]$ exactly for the host-neighbours $x$ of $w$, preserving it.
Eligibility is then literally the colour-change rule: blue $u$ with $cnt[u]==1$
has a unique white host-neighbour, found by one filtered scan of $adj[u]$.

Worked example — $G = P_6$ (path 0–1–2–3–4–5), $host=\{0,1,2,3,4\}$
(vertex 5 invisible), $blue=\{0\}$:

| pop $u$ | force | arc | $cnt$ after (positions 0..4) | queued by |
|---|---|---|---|---|
| — | — | — | $(1,1,2,2,1)$ | seed: only 0 |
| 0 | $0\to1$ | yes | $(0,1,1,2,1)$ | self-check: 1 |
| 1 | $1\to2$ | yes | $(0,0,1,1,1)$ | self-check: 2 |
| 2 | $2\to3$ | yes | $(0,0,0,1,0)$ | self-check: 3 |
| 3 | $3\to4$ | yes | $(0,0,0,0,0)$ | — |

Queue empty → all host vertices blue → `white` returns empty; `fas` arcs
$0\to1,\,1\to2,\,2\to3,\,3\to4$. Vertex 5 is never touched. No subgraph object
is ever built.

Stale example — same $G$, $host=\{0,1,2\}$, $blue=\{0,2\}$: init
$cnt=(1,0,1)$, both 0 and 2 seeded. 0 pops, forces 1; the decrement loop over
$adj[1]\cap host=\{0,2\}$ gives $cnt=(0,0,0)$. When 2 pops it fails the re-check
$cnt[2]\neq 1$ and is skipped — no double force. (If 2 popped first, 0 would be
the stale one; the final colouring is identical either way.)

Queue accounting: each vertex is pushed at most twice (seed / self-check when it
turns blue / decrement-push when its $cnt$ reaches 1) → $O(n)$ pops. Each
adjacency list is scanned $O(1)$ times overall (init / when the vertex turns
blue / when it successfully forces). Total $O(n+m)$ for `white` (paper
Prop 4.11); `fas` with a heap is $O((n+m)\log n)$.

## `NicePD.ops` contract

`ops` records the D4 transitions, indexed by the bag being entered:
`op(z) -> (v, is_insert)` for $z \in [1, k+1]$ = transition $X_{z-1} \to X_z$.
`is_insert=True` means $X_z = X_{z-1}\cup\{v\}$; `False` means
$X_z = X_{z-1}\setminus\{v\}$. `op(k+1)` is necessarily a delete (into the empty
sentinel). Internally a 0-based tuple (`ops[z-1]`) is fine; the driver only calls
`op(z)`.

Fix note for the coding chat: the current `NicePD.__init__` overwrites `self.ops`
with a joined string (`evs`) while `__repr__` iterates it. Keep the `_derive`
tuple as `self.ops`; format `evs` only inside `__repr__`.

---

## Paper mapping (Algorithm 4.2)

```
(L1)  t ← 0;  A ← empty ArcSet;  F ← empty list
(L2)  segment setup: host ← X_t;  bag ← X_t;  W ← empty;  z ← t
(L3)  while W is empty and z ≤ k:
(L3a)    z ← z + 1
(L3b)    W ← White(X_t ∪ X_z, G(t,z))     # only at delete transitions (see §4)
(L4)  A.reverse()
(L6)  if W ≠ ∅:
(L6a)     F.append(W)
(L6c)     A.extend( FAS(X_t ∪ X_{z−1}, G(t,z)) )   # NOT X_z — see T5
(L6d)     A.delete_heads( X_z )            # exactly heads in X_z; no-op if z = k+1
(L6e)     t ← z;  go to (L2)
(L7)  else (W = ∅ and z = k+1):
(L7a)     A.extend( FAS(X_t, G(t,k+1)) )
(L8)  return ( A.sources(), F )            # the single (L5), at the very end
```

---

## Authoritative driver (Python form)

```python
def zf_npd(g, npd):
    # -> (S: bytearray, F: list[bytearray]); |S| <= (npd.width + 1) |F|
    closure = zf_closure(g.adj)          # bound once; stateless per call
    A = ArcSet(g.n)                      # L1: empty FAS
    F = []                               # L1: fort packing
    t = 0                                # L1

    while True:                          # ---- segment (L2) ----
        Xt   = npd.mask_of(t)            # bytes, fixed per segment
        host = bytearray(Xt)             # running union X_t^z (grows only)
        bag  = bytearray(Xt)             # running current bag X_z
        W    = bytearray(g.n)            # empty mask
        z    = t

        while not any(W) and z <= npd.k:                 # L3
            z += 1
            v, is_ins = npd.op(z)        # transition X_{z-1} -> X_z
            if is_ins:
                host[v] = 1              # union grows (mandatory, T4)
                bag[v]  = 1
                continue                 # White() is provably empty here
            bag[v] = 0                   # X_z = X_{z-1} \ {v}; host unchanged
            blue = bytearray(Xt)         # L3b: blue = X_t ∪ X_z (recompute, T3)
            _mask_or(blue, bag)
            W = closure.white(blue, host)

        A.reverse()                      # L4
        if any(W):                       # L6 (W ≠ ∅)
            F.append(W)                  # L6a
            blue[v] = 1                  # L6c: X_t ∪ X_{z-1} = blue ∪ {v}
            A.extend(closure.fas(blue, host))
            A.delete_heads(bag)          # L6d: exactly the heads in X_z (= bag)
            t = z                        # L6e
            continue                     # -> (L2)
        # L7: W = ∅ and z = k+1; bag = X_{k+1} = ∅
        A.extend(closure.fas(bytearray(Xt), host))       # L7a
        return A.sources(), F            # the single (L5), then (L8)
```

---

## Load-bearing details (traps for the implementer)

- **T1 — the scan must evaluate $z = k+1$.** The `while` condition is checked
  before the body, so the final evaluation of a surviving segment is at
  $z = k+1$ with $X_{k+1} = \emptyset$: `white(X_t, G(t,k+1))`. A
  `for z in range(t+1, k+1)` loop would stop at $k$ and break the (L7a)
  guarantee. Use the exact `while` above.
- **T2 — exact deletion in (L6d).** Deleting less leaves an $X_z$ vertex with an
  in-arc (breaks "all of $X_z$ are sources" for the next segment); deleting more
  changes $\text{Sources}(A)$ and the size analysis. Faithful execution only.
- **T3 — `blue` is recomputed per evaluation, never maintained incrementally.**
  On a delete, `blue[v] = 0` would be wrong when $v \in X_t$. Example:
  bags $[\emptyset, \{0,1\}, \{1\}, \dots]$, segment $t=1$, $z=2$ deletes $0$,
  but blue $= X_1 \cup X_2 = \{0,1\}$ still contains $0$. Recompute
  `blue = bytearray(Xt); _mask_or(blue, bag)` at each evaluated step.
- **T4 — `host` is monotone; only the bag shrinks.** On insert: `host[v]=1`
  AND `bag[v]=1`. On delete: `bag[v]=0`, `host` unchanged. Never remove a
  vertex from `host` inside a segment — $X_t^z$ is a union of bags.
- **T5 — (L6c) uses $X_{z-1}$, never $X_z$.** $X_t \cup X_z$ is the set whose
  White is $W \neq \emptyset$ (the failing set). The loop can only exit with
  $W \neq \emptyset$ at a delete step, so $X_{z-1} = X_z \cup \{v\}$; in code:
  take the just-computed `blue` and set `blue[v] = 1`.
- **Skip-on-insert is a proven shortcut, not an algorithm change.** At an insert
  step, blue grows by the new vertex $v$ and host grows by $v$; every neighbor of
  $v$ in $X_t^z$ lies in $X_z \subseteq$ blue (D1 + D2), so $v$ has no white
  neighbors, and adding a blue vertex never changes any forcer's white-neighbor
  count. Hence $\text{White}(X_t \cup X_z, G(t,z)) = \emptyset$ unconditionally;
  skipping the call evaluates a provably empty value. (Constant-factor saving
  only; ≤ $k{+}1$ calls either way.)
- $S$ is never materialized during the loop; the single `sources()` call at the
  end is the final (L5) of the paper.

## Complexity

Each `white`/`fas` call is $O(n+m)$; the scan advances $z$ monotonically, so the
total number of calls over all segments is at most $k+1 \le 4n+1$. Total
$O(n(n+m)) = O(nm)$ for connected graphs — matches Prop 4.12 of the paper.
