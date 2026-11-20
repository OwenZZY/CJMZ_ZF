"""Zero forcing to fixation on the full graph (SPEC-v1.md §5.2).

Engine: the count scheme of Brimkov-Fast-Hicks (EJOR 273(3):889-903, 2019,
Algorithm 1), in complementary form — white-neighbor counts. Canon: one
force per step by the eligible blue vertex of smallest index (min-heap),
the example canon of arXiv:2402.08866v1, tex:L621. Internal core: inputs
are assumed suitable; nothing is validated.
"""

from heapq import heappop, heappush


def closure(graph, blue):
    """Run zero forcing to fixation from an initial blue set.

    graph: object with n (int) and adj (neighbor index sequences).
    blue: iterable of initial blue vertex indices.

    Returns (white, arcs): white = sorted indices still white at fixation;
    arcs = (u, v) forcing pairs in the order forced. Deterministic: the
    eligible blue vertex of smallest index forces at each step.
    """
    n = graph.n
    adj = graph.adj
    is_blue = bytearray(n)
    for v in blue:
        is_blue[v] = 1

    white_count = [0] * n
    heap = []
    for u in range(n):
        if not is_blue[u]:
            continue
        count = 0
        for w in adj[u]:
            if not is_blue[w]:
                count += 1
        white_count[u] = count
        if count == 1:
            heappush(heap, u)

    arcs = []
    while heap:
        u = heappop(heap)
        if not is_blue[u] or white_count[u] != 1:
            continue  # stale entry: unique white neighbor already forced
        v = -1
        for w in adj[u]:
            if not is_blue[w]:
                v = w
                break
        arcs.append((u, v))
        is_blue[v] = 1
        for w in adj[v]:
            if is_blue[w]:
                white_count[w] -= 1
                if white_count[w] == 1:
                    heappush(heap, w)
        count = 0
        for w in adj[v]:
            if not is_blue[w]:
                count += 1
        white_count[v] = count
        if count == 1:
            heappush(heap, v)

    white = [i for i in range(n) if not is_blue[i]]
    return white, arcs