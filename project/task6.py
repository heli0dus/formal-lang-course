from pyformlang.cfg import CFG, Variable, Terminal, Epsilon
import pyformlang
import networkx as nx
from typing import Tuple


def cfg_to_weak_normal_form(cfg: pyformlang.cfg.CFG) -> pyformlang.cfg.CFG:
    gramm1 = cfg.eliminate_unit_productions().remove_useless_symbols()
    long_rules = gramm1._get_productions_with_only_single_terminals()
    new_rules = set(gramm1._decompose_productions(long_rules))
    return CFG(start_symbol=Variable("S"), productions=new_rules)


def gramm_from_file(filepath: str) -> CFG:
    with open(filepath) as f:
        return CFG.from_text("".join(l for l in f))


def cfpq_with_hellings(
    cfg: pyformlang.cfg.CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[Tuple[int, int]]:

    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes

    gramm = cfg_to_weak_normal_form(cfg)
    p1 = {}
    p2 = set()
    p3 = {}

    for p in gramm.productions:
        p_len = p.body
        if p_len == 1 and isinstance(p.body[0], Terminal):
            p1.setdefault(p.head, set()).add(p.body[0])
        elif p_len == 1 and isinstance(p.body[0], Epsilon):
            p2.add(p.body[0])
        elif p_len == 2:
            p3.setdefault(p.head, set).add((p.body[0], p.body[1]))

    result = {(n, v, v) for n in p2 for v in graph.nodes}
    increment = {}
    i = 0
    for v, u, tag in graph.edges.data("label"):
        for n in p1:
            if tag in p1[n]:
                increment[i] = (n, v, u)
                i += 1
    result.union(increment)

    queue_to_process = result.copy()

    while len(queue_to_process) > 0:
        n_i, vi, ui = queue_to_process.pop()

        step_increment = set()

        for n_j, vj, uj in result:
            if vi == ui:
                for n_k in p3:
                    if (n_j, n_i) in p3[n_k] and (n_k, vj, vi) not in result:
                        queue_to_process.add((n_k, vj, ui))
                        step_increment.add((n_k, vj, ui))

        for n_j, vj, uj in result:
            if ui == vi:
                for n_k in p3:
                    if (n_i, n_j) in p3[n_k] and (n_k, vi, ui) not in result:
                        queue_to_process.add((n_k, vi, uj))
                        step_increment.add((n_k, vi, uj))

        result.union(step_increment)

    return {
        (u, v)
        for (n_i, u, v) in result
        if u in start_nodes and v in final_nodes and Variable(n_i) == cfg.start_symbol
    }
