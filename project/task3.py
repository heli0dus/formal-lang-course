from typing import Iterable
from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex, Symbol

from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
import scipy.sparse as sparse


class FiniteAutomaton:
    def __init__(self,
                 aut:
                 NondeterministicFiniteAutomaton |
                 DeterministicFiniteAutomaton):
        self.start_staes = aut.start_states
        self.final_states = aut.final_states
        pass

    def accepts(self, word: Iterable[Symbol]) -> bool:
        pass

    def is_empty(self) -> bool:
        pass
