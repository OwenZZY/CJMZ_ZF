import networkx as nx
from LinkedList import ZeroForcing as ZF
from LinkedList import DLinkedList as DLL

def get_Gst(G, calX, t, s):
    X_t_s = []
    for j in range(t, s+1):
        X_t_s.extend(calX[j])
    X_t_s = list(set(X_t_s))
    return nx.induced_subgraph(G, X_t_s)

def get_union(calX, t, s):
    cup_t_s = []
    cup_t_s.extend(calX[t])
    cup_t_s.extend(calX[s])
    return list(set(cup_t_s))



def algorithm(G:nx.Graph, calX):
    n = G.number_of_nodes()
    FAS=[None for _ in range(n+1)]
    FAS_tail = [None for _ in range(n+1)]
    rev_FAS = [None for _ in range(n+1)]
    rev_FAS_tail = [None for _ in range(n+1)]

    k = len(calX)-2
    calF = []
    t = 0

    while True:
        s, W = t, [] #(L2)
        old_FAS_t_s_1 = []

        while s <= k:
            s += 1
            G_ts = get_Gst(G, calX, t, s)
            cup_ts = get_union(calX, t, s)
            # print(t, s, cup_ts)
            W, FAS_t_s = ZF.closure(G_ts, cup_ts)

            if len(W) != 0:
                break
            # print('len(W) == 0')
            old_FAS_t_s_1 = FAS_t_s

        ## print test
        # print('Found a fort ', W, ' and current FAS is ')
        # for i, chain in enumerate(FAS):
        #     if chain is not None:
        #         print('\t', i, ': ', chain)
        # print('Reversed FAS')
        # for i, chain in enumerate(rev_FAS):
        #     if chain is not None:
        #         print('\t', i, ': ', chain)
        # print('Will add:')
        # for i, chain in enumerate(old_FAS_t_s_1):
        #     if chain is not None:
        #         print('\t', i, ': ', chain)
        ## print test end
        FAS, FAS_tail, rev_FAS, rev_FAS_tail \
            = union_fas(calX[t], calX[s-1], calX[s],
                        (FAS, FAS_tail),
                        (rev_FAS, rev_FAS_tail),
                        old_FAS_t_s_1
                        )

        ## print test
        # print("FAS changed to: ")
        # for i, chain in enumerate(FAS):
        #     if chain is not None:
        #         print('\t', i, ': ', chain)
        # print('Reversed FAS')
        # for i, chain in enumerate(rev_FAS):
        #     if chain is not None:
        #         print('\t', i, ': ', chain)
        # print()
        ## print test

        # (L4)
        calF.append(W)
        # print(t, s)
        if s>= k:
            break
        t = s # back to (L2)

    S = []
    for i, chain in enumerate(FAS_tail):
        if chain is not None:
            S.append(i)
    return S, calF, rev_FAS

def union_fas(leftX, rightX, rightX_small, # i.e., X_t, X_s, and X_{s-1}
              A_pair,
              rev_A_pair,
              newA):
    A, A_tail = A_pair
    rev_A, rev_A_tail = rev_A_pair
    # print('Concatenating FASs - X_t:', leftX, ' X_s:', rightX,)
    Z = []
    Z.extend(leftX)
    Z.extend(rightX)
    Z = list(set(Z))

    newA_tail = [None for _ in newA]
    rev_newA = [None for _ in newA]
    rev_newA_tail = [None for _ in newA]
    for i in range(len(newA)):
        if newA[i] is None:
            continue
        chain:DLL.LinkedList = newA[i]
        newA_tail[chain.tail.get_self()] = chain
        rev_chain = chain.copy_a_reverse()
        rev_newA[chain.tail.get_self()] = rev_chain
        rev_newA_tail[i] = rev_chain

    for v in rightX_small:
        if A[v] is None:
            continue
        chain:DLL.LinkedList = A[v]
        new_head = chain.trim_head()
        A[v] = None
        A[new_head] = chain

        chain:DLL.LinkedList = rev_A_tail[v]
        new_tail = chain.trim_tail()
        rev_A_tail[v] = None
        rev_A_tail[new_tail] = chain

    for v in Z:
        if A[v] is None:
            rev_A[v] = newA[v]
            chain:DLL.LinkedList = newA[v]
            rev_A_tail[chain.tail.get_self()] = chain

            A_tail[v] = rev_newA_tail[v]
            chain:DLL.LinkedList = rev_newA_tail[v]
            A[chain.head.get_self()] = chain
            continue

        chain1:DLL.LinkedList = rev_A_tail[v]
        chain2:DLL.LinkedList = newA[v]
        end = chain1.concatenate(chain2)
        rev_A_tail[v] = None
        rev_A_tail[end] = chain1

        chain1:DLL.LinkedList = A[v]
        chain2:DLL.LinkedList = rev_newA_tail[v]
        head = chain1.concatenate_from_before(chain2)
        A[v] = None
        A[head] = chain1

    return rev_A, rev_A_tail, A, A_tail

