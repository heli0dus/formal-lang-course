from pyformlang.rsa import *
import networkx as nx
from copy import deepcopy

from pyformlang.finite_automaton import State, Symbol
from pyformlang.cfg import CFG
from project.task8 import cfg_to_rsm
from dataclasses import dataclass
from typing import *


@dataclass
class GLLDescriptor:
    rsm_state: Tuple[Symbol, State]
    graph_node: int
    return_address: Tuple[Symbol, int]


def cfpq_with_gll(
    rsm: RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:

    if isinstance(rsm, CFG):
        rsm = cfg_to_rsm(rsm)

    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes

    initial_gss = {(rsm.initial_label, start_node) for start_node in start_nodes}

    visited_descriptors = {
        ((rsm.initial_label, rsm.boxes[rsm.initial_label].dfa.start_state), st[1], st)
        for st in initial_gss
    }
    to_visit = deepcopy(visited_descriptors)

    pop_history = {}
    res = set()
    gss = {st: set() for st in initial_gss}
    while len(to_visit) != 0:
        rsm_state, graph_node, gss_vertex = to_visit.pop()

        if rsm_state[1] in rsm.boxes[rsm_state[0]].dfa.final_states:
            if gss_vertex in initial_gss:
                if graph_node in final_nodes:
                    res.add((gss_vertex[1], graph_node))

            # назад по адресам возврата
            pop_history.setdefault(gss_vertex, set()).add(graph_node)
            for to_stack_state, to_rsm_state in gss.setdefault(gss_vertex, set()):
                new_descriptor = (to_rsm_state, graph_node, to_stack_state)
                if new_descriptor not in visited_descriptors:
                    to_visit.add(new_descriptor)
                    visited_descriptors.add(new_descriptor)

        to_nodes = {}
        for _, n, l in graph.edges(graph_node, data="label"):
            to_nodes.setdefault(l, set()).add(n)

        dfa_dict = rsm.boxes[Symbol(rsm_state[0])].dfa.to_dict()
        if rsm_state[1] not in dfa_dict:
            continue
        for symbol, to in dfa_dict[rsm_state[1]].items():
            if symbol in rsm.labels:  # если нетерминал и мы меняем коробку
                new_gss_vertex = (symbol.value, graph_node)  # новая нода gss
                if new_gss_vertex in pop_history:
                    # если мы уже ходили из этого обратного адреса -
                    # попробовать запустить эти обратыне адреса заново в новой вершине
                    for to_graph_node in pop_history[new_gss_vertex]:
                        new_descriptor = (
                            (rsm_state[0], to.value),
                            to_graph_node,
                            gss_vertex,
                        )
                        if new_descriptor not in visited_descriptors:
                            to_visit.add(new_descriptor)
                            visited_descriptors.add(new_descriptor)
                gss.setdefault(new_gss_vertex, set()).add(
                    (gss_vertex, (rsm_state[0], to.value))
                )  # добавляем адрес возврата
                box_start_state = rsm.boxes[symbol].dfa.start_state.value
                new_descriptor = (
                    (symbol.value, box_start_state),
                    graph_node,
                    new_gss_vertex,
                )

                if new_descriptor not in visited_descriptors:
                    to_visit.add(new_descriptor)
                    visited_descriptors.add(new_descriptor)
            else:  # если остаёмся в той же коробке
                if (
                    symbol.value not in to_nodes
                ):  # если по этому символу из этой вершины не можем пойти
                    continue
                for node in to_nodes[symbol.value]:
                    new_descriptor = ((rsm_state[0], to.value), node, gss_vertex)

                    if new_descriptor not in visited_descriptors:
                        to_visit.add(new_descriptor)
                        visited_descriptors.add(new_descriptor)
    return res
