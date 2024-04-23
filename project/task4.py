import scipy.sparse as sparse
import numpy as np
from copy import deepcopy
from pyformlang.finite_automaton import State

from project.task3 import FiniteAutomaton, intersect_automata


def fixed_matrix(m):
    result = sparse.dok_matrix(m.shape, dtype=bool)
    for i in range(m.shape[0]):
        for j in range(m.shape[0]):
            if m[j, i]:
                result[i] += m[j]
    return result


def reachability_with_constraints(
    fa: FiniteAutomaton, constraints_fa: FiniteAutomaton
) -> dict[int, set[int]]:

    m = constraints_fa.size()
    n = fa.size()

    constr_start_inds = [
        constraints_fa.state_to_idx[State(i)] for i in constraints_fa.start_states
    ]

    symbols = fa.matrix.keys() & constraints_fa.matrix.keys()
    result = {s: set() for s in fa.start_states}
    transitions = {
        label: sparse.block_diag((constraints_fa.matrix[label], fa.matrix[label]))
        for label in symbols
    }

    for v in [fa.state_to_idx[State(k)] for k in fa.start_states]:
        front = sparse.dok_matrix((m, m + n), dtype=bool)
        for i in constr_start_inds:
            front[i, i] = True
        for i in range(m):
            front[i, v + m] = True

        for _ in range(m * n):
            new_front = sparse.dok_matrix((m, m + n), dtype=bool)
            for sym in symbols:
                new_front += fixed_matrix(front @ transitions[sym])
            front = new_front

            for i in [
                constraints_fa.state_to_idx[State(k)]
                for k in constraints_fa.final_states
            ]:
                for j in [fa.state_to_idx[State(k)] for k in fa.final_states]:
                    if front[i, j + m]:
                        result[v].add(j)
    return result
