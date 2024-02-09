import copy
import networkx as nx
from LinkedList import DLinkedList as DLL

N_W = 'white_neighbours'
# N_B = 'black_neighbours'
CF = 'can_force'
CNF = 'cannot_force'
Blue = True
White = False
colour = 'forced'

def set_black(u, G:nx.Graph, frontier, whites):
    G.nodes()[u][colour] = Blue
    whites.pop(u)

    for v in G.neighbors(u):
        G.nodes()[v][N_W].pop(u)
        if G.nodes()[v][colour] == Blue:
            if v in frontier[CF]: # i.e. these forcable are no longer forcable
                frontier[CF].pop(v)
            if u in G.nodes()[v][N_W]:
                G.nodes()[u][N_W].pop(v)
            if len(G.nodes()[v][N_W])==1:
                frontier[CNF].pop(v)
                frontier[CF][v] = 0

    if len(G.nodes()[u][N_W]) == 1:
        frontier[CF][u] = 0
    else:
        frontier[CNF][u] = 0

    return

def zero_force(u, G:nx.Graph, frontier, whites):
    frontier[CF].pop(u)
    if len(G.nodes()[u][N_W]) != 1:
        print('There is a bug')
        exit(0)
    # v = None
    for v in G.nodes()[u][N_W]:
        break
    set_black(v, G, frontier, whites)
    return v

# a networkX object
# a vertex set X
# return the set of white vertices W
# return the set of zero forcing chains.
def closure(G_0:nx.classes.graph.Graph, Z_0):
    G = copy.deepcopy(G_0)
    Z = copy.deepcopy(Z_0)
    nx.set_node_attributes(G, White, colour)
    max_node_index = max([_ for _ in G.nodes()])
    FAS = [None for _ in range(max_node_index + 1)]
    FAS_tail = [None for _ in range(max_node_index + 1)]
    # max_d = max([_[1] for _ in G.degree()])
    frontier = {CF:{}, CNF:{}}
    whites = {}

    for u in G.nodes():
        whites[u] = G.degree()[u]
        # G.nodes()[u][N_B] = {}
        G.nodes()[u][N_W] = {}
        for v in G.neighbors(u):
            G.nodes[u][N_W][v] = 0

    for z in Z:
        set_black(z, G, frontier, whites)
        FAS[int(z)] = DLL.LinkedList(z)
        FAS_tail[int(z)] = FAS[int(z)]

    while len(frontier[CF])>0:
        for u in frontier[CF]:
            prt = 'Frontier: ' + str(frontier) + '\t'
            v = zero_force(u, G, frontier, whites)
            prt += str(u) + ' forces ' + str(v)
            # print(prt)
            FAS_tail[u]:DLL.LinkedList
            FAS_tail[u].append(v)
            FAS_tail[v] = FAS_tail[u]
            FAS_tail[u] = None
            break

    Whites = [u for u in whites]
    return Whites, FAS


def draw_ZFS(G, S, pos = None):
    if pos is None:
        pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos, with_labels=G.nodes())
    nodes = nx.draw_networkx_nodes(G, pos, node_color='white')
    nodes.set_edgecolor('black')
    nx.draw_networkx_nodes(G, pos, nodelist=S, node_color='blue')


def draw_FAS(G, S, A, pos = None):
    if pos is None:
        pos = nx.kamada_kawai_layout(G)
    FAS = []
    for i, chain in enumerate(A):
        if chain is None:
            continue
        chain: DLL.LinkedList
        curr = chain.head
        while curr.next is not None:
            FAS.append((curr.get_self(), curr.next.get_self()))
            curr = curr.next

    # nx.draw(G, pos, with_labels=G.nodes())
    nx.draw(G, pos, with_labels=G.nodes())
    nodes = nx.draw_networkx_nodes(G, pos, node_color='white')
    nodes.set_edgecolor('black')
    drawH = nx.DiGraph()
    drawH.add_edges_from(G.edges())
    nx.draw_networkx_nodes(drawH, pos, nodelist=S, node_color='blue')
    nx.draw_networkx_edges(drawH, pos, edgelist=FAS, edge_color='w', arrows=False)
    nx.draw_networkx_edges(drawH, pos, edgelist=FAS, edge_color='r', arrows=True, arrowsize=20, width=1)

