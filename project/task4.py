import scipy.sparse as sparse
import numpy as np

from project.task3 import FiniteAutomaton


def reachability_with_constraints(fa: FiniteAutomaton,
                         constraints_fa: FiniteAutomaton) -> dict[int, set[int]]:
    fa_mat, fa_idx = fa.matrix, fa.state_to_idx
    constraint_mat, constraint_idx = constraints_fa.matrix, constraints_fa.state_to_idx
    commons = set(fa_mat.keys()).intersection(set(constraint_mat.keys()))
    transitions = {
        s: sparse.block_diag((fa_mat[s], constraint_mat[s]), format="dok")
        for s in commons
    }

    idx_to_state = {v: k for k, v in fa_idx.items()}
    starts_idx = [fa_idx[s] for s in fa.start_states]

    result = dict()
    for s in starts_idx:
        n_constr = len(constraints_fa.state_to_idx)
        n_graph = len(fa.state_to_idx)

        accessible = sparse.eye(n_constr, n_constr + n_graph, dtype=np.bool_, format="dok")
        for rs in constraints_fa.start_states:
            i = constraint_idx[rs]
            accessible[i, n_constr + fa_idx[s]] = True

        prev = 0
        front = accessible
        while accessible.count_nonzero() != prev:
            prev = accessible.count_nonzero()
            new_front = sparse.eye(n_constr, n_constr + n_graph, dtype=np.bool_, format="dok")
            for mat in transitions.values():
                next = front @ mat
                for i in range(n_constr):
                    for j in range(n_constr):
                        if next[i, j]:
                            new_front[j, n_constr:] += next[i, n_constr:]
            accessible += new_front
            front = new_front

        result_single = set()
        for fs in constraints_fa.final_states:
            fs_id = constraint_idx[fs]
            for i in range(n_graph):
                if accessible[fs_id, n_constr + i]:
                    result_single.add(idx_to_state[i])
        result[s] = result_single

    return {k: v.intersection(set(fa.final_states)).
            intersection(set(constraints_fa.final_states))
            for k, v in result.items()}
