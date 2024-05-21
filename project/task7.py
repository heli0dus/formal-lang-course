from pyformlang.cfg import *
import networkx as nx
from typing import Set
from project.task6 import cfg_to_weak_normal_form

import scipy.sparse as sparse
import copy


def cfpq_with_matrix(
    cfg: CFG,
    graph: nx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> set[tuple[int, int]]:

    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes

    gramm = cfg_to_weak_normal_form(cfg)
    n = graph.number_of_nodes()

    mat_init = {}
    terminals_to_vars = {}
    eps_rules = set()
    pair_rules = {}

    for p in gramm.productions:
        mat_init[p.head.to_text()] = sparse.dok_matrix((n, n), dtype=bool)
        if len(p.body) == 0:
            eps_rules.add(p.head.to_text())
        if len(p.body) == 1 and isinstance(p.body[0], Terminal):
            terminals_to_vars.setdefault(p.body[0].to_text(), set()).add(
                p.head.to_text()
            )
        if len(p.body) == 2:
            pair_rules.setdefault(p.head.to_text(), set()).add(
                (p.body[0].to_text(), p.body[1].to_text())
            )

    for u, v, label in graph.edges(data="label"):
        if label in terminals_to_vars:
            for term_var in terminals_to_vars[label]:
                mat_init[term_var][u, v] = True

    for sym in eps_rules:
        mat_init[sym].setdiag(True)

    mat = {
        p.head.to_text(): sparse.dok_matrix((n, n), dtype=bool)
        for p in gramm.productions
    }

    for i in range(graph.number_of_nodes() * len(mat_init)):
        for sym, prod in pair_rules.items():
            for lhs, rhs in prod:
                mat[sym] += mat_init[lhs] @ mat_init[rhs]
        for sym, m in mat.items():
            mat_init[sym] += m

    start = gramm.start_symbol.to_text()
    ns, ms = mat_init[start].nonzero()
    return {(n, m) for n, m in zip(ns, ms) if n in start_nodes and m in final_nodes}
