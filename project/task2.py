from typing import Set
from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex

from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    return Regex(regex).to_epsilon_nfa().minimize()


def graph_to_nfa(
  graph: MultiDiGraph, start_states: Set[int], final_states: Set[int]
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton()

    if len(start_states) == 0:
        for node in graph.nodes():
            nfa.add_start_state(node)
    for node in start_states:
        nfa.add_start_state(node)

    if len(final_states) == 0:
        for node in graph.nodes():
            nfa.add_final_state(node)
    for node in final_states:
        nfa.add_final_state(node)

    for u, v, label in graph.edges(data='label'):
        nfa.add_transition(u, label, v)

    return nfa
    pass
