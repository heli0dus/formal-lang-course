from typing import Iterable, Union
from networkx import MultiDiGraph
from copy import deepcopy

# from networkx import NodeView
from pyformlang.finite_automaton import Symbol

from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import EpsilonNFA
import scipy.sparse as sparse
import numpy as np

import project.task2 as task2


def as_set(obj):
    if not isinstance(obj, set):
        return {obj}
    return obj


class FiniteAutomaton:
    def __init__(
        self, aut: Union[NondeterministicFiniteAutomaton, DeterministicFiniteAutomaton]
    ):
        self.start_states = aut.start_states
        self.final_states = aut.final_states
        states = aut.to_dict()
        len_states = len(aut.states)
        self.state_mat_mapping = {v: i for i, v in enumerate(aut.states)}
        self.matrix = dict()

        for label in aut.symbols:
            self.matrix[label] = sparse.dok_matrix((len_states, len_states), dtype=bool)
            for u, edges in states.items():
                if label in edges:
                    for v in as_set(edges[label]):
                        self.matrix[label][
                            self.state_mat_mapping[u], self.state_mat_mapping[v]
                        ] = True

    def accepts(self, word: Iterable[Symbol]) -> bool:
        return self.to_automaton().accepts("".join(word))

    def is_empty(self) -> bool:
        return len(self.matrix.values()) == 0

    def size(self) -> int:
        return len(self.state_mat_mapping)

    def transitive_closure(self) -> sparse.dok_matrix:
        if self.is_empty():
            return sparse.dok_matrix((0, 0), dtype=bool)
        
        adj = sum(self.matrix.values()) + sparse.eye(self.size(), self.size(), dtype=bool)

        for _ in range(adj.shape[0]):
            adj += adj @ adj
            
        return adj

    def to_automaton(self) -> NondeterministicFiniteAutomaton:
        ans = NondeterministicFiniteAutomaton()

        idx_to_state = {v: k for k, v in self.state_mat_mapping.items()}

        for label in self.matrix.keys():
            matrix_size = self.matrix[label].shape[0]
            for x in range(matrix_size):
                for y in range(matrix_size):
                    if self.matrix[label][x, y]:
                        ans.add_transition(
                            self.state_mat_mapping[State(x)],
                            label,
                            self.state_mat_mapping[State(y)],
                        )

        for s in self.start_states:
            ans.add_start_state(self.state_mat_mapping[State(s)])

        for s in self.final_states:
            ans.add_final_state(self.state_mat_mapping[State(s)])

        return ans


def intersect_automata(
    automaton1: FiniteAutomaton, automaton2: FiniteAutomaton
) -> FiniteAutomaton:
    a = deepcopy(automaton1)
    num_states = len(automaton2.state_mat_mapping)
    symbols = automaton1.matrix.keys() & automaton2.matrix.keys()
    # symbols = None
    # if take_from_mapping:
    #     symbols = automaton1.state_mat_mapping.keys() & automaton2.state_mat_mapping.keys()
    # else:
    #     symbols = automaton1.matrix.keys() & automaton2.matrix.keys()
    matrices = {
        label: sparse.kron(automaton1.matrix[label], automaton2.matrix[label], "csr")
        for label in symbols
    }
    start = set()
    final = set()
    mapping = dict()

    for u, i in automaton1.state_mat_mapping.items():
        for v, j in automaton2.state_mat_mapping.items():

            k = len(automaton2.state_mat_mapping) * i + j
            mapping[State(k)] = k

            assert isinstance(u, State)
            if u in automaton1.start_states and v in automaton2.start_states:
                start.add(State(k))

            if u in automaton1.final_states and v in automaton2.final_states:
                final.add(State(k))

    a.matrix = matrices
    a.state_mat_mapping = mapping
    a.start_states = start
    a.final_states = final
    return a


def paths_ends(
    graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int], regex: str
) -> list[tuple[any, any]]:  # почему-то у меня не получилось импортировать NodeView
    query = FiniteAutomaton(task2.regex_to_dfa(regex))
    aut_graph = FiniteAutomaton(task2.graph_to_nfa(graph, start_nodes, final_nodes))
    intersection = intersect_automata(aut_graph, query)
    closure = intersection.transitive_closure()

    size = query.size()
    result = []
    for u, v in zip(*closure.nonzero()):
        if u in intersection.start_states and v in intersection.final_states:
            result.append(
                (aut_graph.state_mat_mapping[u // size], aut_graph.state_mat_mapping[v // size])
            )

    return result
