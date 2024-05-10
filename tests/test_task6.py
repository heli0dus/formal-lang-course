import project.task4 as task4
import project.task2 as task2
import project.task3 as task3
import project.task6 as task6
from pyformlang import cfg
import networkx as nx

def test_cfpq():
    gramm = cfg.CFG.from_text("S -> $ | a S")
    regex_str = "a*"

    gr = nx.MultiDiGraph()
    gr.add_edge(0, 1, label='a')
    gr.add_edge(1, 2, label='b')
    gr.add_edge(2, 0, label='a')
    start_nodes = {0, 1, 2}
    final_nodes = {0, 1}

    print(gramm)
    print(task6.cfg_to_weak_normal_form(gramm))
    print()
    print(task4.reachability_with_constraints(
                task3.FiniteAutomaton(task2.graph_to_nfa(gr, start_nodes, final_nodes)),
                task3.FiniteAutomaton(task2.regex_to_dfa(regex_str)),
            ))
    print(task6.cfpq_with_hellings(gramm, gr, start_nodes, final_nodes))

    assert True