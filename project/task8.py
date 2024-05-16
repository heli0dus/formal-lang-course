from pyformlang import *
from pyformlang.finite_automaton import *
import networkx as nx
from scipy.sparse import *
from typing import *
from itertools import product

from project.task2 import graph_to_nfa

def cfpq_with_tensor(
    rsm: rsa.RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:

    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes

    graph_mat, graph_mat_mapping, n_graph, graph_states = graph_to_mat(graph, start_nodes, final_nodes)

    rsm_mat, n_rsm = rsm_to_mat(rsm)
    rsm_states = set()
    rsm_starts = set()
    rsm_finals = set()

    for sym, box in rsm.boxes.items():
        rsm_states |= {(sym.value, state.value) for state in box.dfa.states}
        rsm_starts |= {(sym.value, state.value) for state in box.dfa.start_states}
        rsm_finals |= {(sym.value, state.value) for state in box.dfa.final_states}

    idx_to_state = {
        i: state for i, state in enumerate(product(graph_states, rsm_states))
    }

    nonzero = 0
    while True:
        n = n_rsm * n_graph
        symbols = rsm_mat.keys() & graph_mat.keys()
        if len(symbols) != 0:
            mat = {}
            for symbol in symbols:
                mat[symbol] = kron(graph_mat[symbol], rsm_mat[symbol])
            m = sum(mat.values())
        else:
            m = dok_matrix((n, n), dtype=bool)
        m += eye(n, dtype=bool)

        for _ in range(n):
            m += m @ m
        new_nonzero = m.count_nonzero()
        if new_nonzero <= nonzero:
            break
        else:
            nonzero = new_nonzero

        for from_idx, to_idx in zip(*m.nonzero()):
            from_state = idx_to_state[from_idx]
            to_state = idx_to_state[to_idx]
            from_rsm_state = from_state[1]
            to_rsm_state = to_state[1]
            if from_rsm_state in rsm_starts and to_rsm_state in rsm_finals:
                sym = from_rsm_state[0]
                from_graph_idx = graph_mat_mapping[from_state[0]]
                to_graph_idx = graph_mat_mapping[to_state[0]]
                graph_mat.setdefault(
                    sym, dok_matrix((n_graph, n_graph), dtype=bool)
                )[from_graph_idx, to_graph_idx] = True

    S = rsm.initial_label.value
    if S not in graph_mat:
        return set()

    res = set()
    for from_graph_state, to_graph_state in product(start_nodes, final_nodes):
        from_graph_idx = graph_mat_mapping[from_graph_state]
        to_graph_idx = graph_mat_mapping[to_graph_state]
        if graph_mat[S][from_graph_idx, to_graph_idx]:
            res.add((from_graph_state, to_graph_state))
    return res


def cfg_to_rsm(cfg: cfg.CFG) -> rsa.RecursiveAutomaton:
    return rsa.RecursiveAutomaton.from_text(cfg.to_text())


def ebnf_to_rsm(ebnf: str) -> rsa.RecursiveAutomaton:
    return rsa.RecursiveAutomaton.from_text(ebnf)


def rsm_to_mat(rsm: rsa.RecursiveAutomaton) -> Tuple[Dict[str, dok_matrix], int]:
    n = sum([len(box.dfa.states) for box in rsm.boxes.values()])

    rsm_states = set()

    for sym, box in rsm.boxes.items():
        rsm_states |= {(sym.value, state.value) for state in box.dfa.states}

    mat = {}
    mapping = {state: i for i, state in enumerate(rsm_states)}
    for sym, box in rsm.boxes.items():
        for from_state, transitions in box.dfa.to_dict().items():
            for symbol, to_state in transitions.items():
                from_idx = mapping[(sym.value, from_state.value)]
                to_idx = mapping[(sym.value, to_state.value)]
                mat.setdefault(
                    symbol.value, dok_matrix((n, n), dtype=bool)
                )[from_idx, to_idx] = True

    return (mat, n)

def graph_to_mat(graph: nx.DiGraph,
                 start_nodes: set[int],
                 final_nodes: set[int]) -> Tuple[Dict[str, dok_matrix], Dict[str, int], int, Set[int]]:
    nfa = graph_to_nfa(graph, start_nodes, final_nodes)

    states = {state.value for state in nfa.states}
    n = len(nfa.states)

    mapping = {state: i for i, state in enumerate(states)}
    mat = {}

    for from_state, transitions in nfa.to_dict().items():
        for symbol, to_states in transitions.items():
            if not isinstance(to_states, set):
                to_states = {to_states}
            for to_state in to_states:
                from_idx = mapping[from_state.value]
                to_idx = mapping[to_state.value]
                mat.setdefault(
                    symbol.value,
                    dok_matrix((n, n), dtype=bool),
                )[from_idx, to_idx] = True

    return (mat, mapping, n, states)