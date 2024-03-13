from typing import Iterable, Union
from networkx import MultiDiGraph

# from networkx import NodeView
from pyformlang.finite_automaton import Symbol

from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import EpsilonNFA
import scipy.sparse as sparse

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
        self.state_to_idx = {v: i for i, v in enumerate(aut.states)}
        self.matrix = dict()

        for label in aut.symbols:
            self.matrix[label] = sparse.dok_matrix((len_states, len_states), dtype=bool)
            for u, edges in states.items():
                if label in edges:
                    for v in as_set(edges[label]):
                        self.matrix[label][
                            self.state_to_idx[u], self.state_to_idx[v]
                        ] = True

    def accepts(self, word: Iterable[Symbol]) -> bool:
        return self.to_automaton().accepts("".join(word))
        pass

    def is_empty(self) -> bool:
        return len(self.matrix) == 0 or len(list(self.matrix.values())[0]) == 0

    def transitive_closure(self):
        if len(self.matrix.values()) == 0:
            return sparse.dok_matrix((0, 0), dtype=bool)
        adj = sum(self.matrix.values())
        for _ in range(adj.shape[0]):
            adj += adj @ adj
        return adj

    def to_automaton(self) -> NondeterministicFiniteAutomaton:
        ans = NondeterministicFiniteAutomaton()

        for label in self.matrix.keys():
            matrix_size = self.matrix[label].shape[0]
            for x in range(matrix_size):
                for y in range(matrix_size):
                    if self.matrix[label][x, y]:
                        ans.add_transition(
                            self.state_to_idx[State(x)],
                            label,
                            self.state_to_idx[State(y)],
                        )

        for s in self.start_staes:
            ans.add_start_state(self.state_to_idx[State(s)])

        for s in self.final_states:
            ans.add_final_state(self.state_to_idx[State(s)])

        return ans


def intersect_automata(
    automaton1: FiniteAutomaton, automaton2: FiniteAutomaton
) -> FiniteAutomaton:
    num_states = len(automaton2.state_to_idx)
    symbols = set(automaton1.matrix.keys()).intersection(automaton2.matrix.keys())
    matrices = {
        label: sparse.kron(automaton1.matrix[label], automaton2.matrix[label])
        for label in symbols
    }

    res = EpsilonNFA()
    pass

    for symb, mat in matrices.items():
        from_idx, to_idx = mat.nonzero()
        for fro, to in zip(from_idx, to_idx):
            res.add_transition(fro, symb, to)

    for s1 in automaton1.start_states:
        for s2 in automaton2.start_states:
            res.add_start_state(
                automaton1.state_to_idx[s1] * num_states + automaton2.state_to_idx[s2]
            )

    for s1 in automaton1.final_states:
        for s2 in automaton2.final_states:
            res.add_final_state(
                automaton1.state_to_idx[s1] * num_states + automaton2.state_to_idx[s2]
            )

    return res


def paths_ends(
    graph: MultiDiGraph, start_nodes: set[int], final_nodes: set[int], regex: str
) -> list[tuple[any, any]]:  # почему-то у меня не получилось импортировать NodeView
    query = task2.regex_to_dfa(regex)
    aut = task2.graph_to_nfa(graph, start_nodes, final_nodes)

    both = FiniteAutomaton(intersect_automata(query, aut))
    flat = None
    for mat in both.matrix.values():
        if flat is None:
            flat = mat
            continue
        flat |= mat
    if flat is None:
        return []

    prev = 0
    while flat.count_nonzero() != prev:
        prev = flat.count_nonzero()
        flat += flat @ flat

    rev_idx = {i: k for k, i in both.state_to_idx.items()}
    names = list(aut.states)
    n_states = len(names)
    result = set()

    from_idx, to_idx = flat.nonzero()
    for fro, to in zip(from_idx, to_idx):
        fro_id = rev_idx[fro]
        to_id = rev_idx[to]
        if fro_id in both.start_states and to_id in both.final_states:
            result.add((names[fro_id.value % n_states], names[to_id.value % n_states]))

    return list(result)
