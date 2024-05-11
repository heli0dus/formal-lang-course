import project.task4 as task4
import project.task2 as task2
import project.task3 as task3
import project.task6 as task6
from pyformlang import cfg
import networkx as nx
from pyformlang.regular_expression import Regex


def test_cfpq():
    gramm = cfg.CFG.from_text("S -> $ | a S")
    regex_str = "a b c*"
    a = Regex("a b c*")
    # b = Regex("(abc)*")
    # assert Regex("abc*") == Regex("(abc)*")
    gr = nx.MultiDiGraph()
    gr.add_edges_from(
        [
            (0, 1, "l"),
            (1, 2, "l"),
            (2, 0, "b"),
            (2, 1, "b"),
            (2, 5, "l"),
            (2, 8, "l"),
            (3, 1, "l"),
            (3, 0, "e"),
            (4, 2, "e"),
            (6, 0, "b"),
            (7, 5, "b"),
        ]
    )
    # gr.add_edge(0, 1, label='a')
    # gr.add_edge(1, 2, label='b')
    # gr.add_edge(2, 0, label='a')
    # start_nodes = {0, 1, 2}
    # final_nodes = {0, 1}
    start_nodes = {0, 2, 6}
    final_nodes = {1, 2, 4}

    print()

    print(gramm.to_text())
    print(task6.cfg_to_weak_normal_form(gramm).to_text())
    print()
    print(
        task4.reachability_with_constraints(
            task3.FiniteAutomaton(task2.graph_to_nfa(gr, start_nodes, final_nodes)),
            task3.FiniteAutomaton(task2.regex_to_dfa(regex_str)),
        )
    )
    print(task6.cfpq_with_hellings(gramm, gr, start_nodes, final_nodes))
    print(task3.paths_ends(gr, start_nodes, final_nodes, regex_str))

    assert True
