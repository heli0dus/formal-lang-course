from pyformlang.cfg import CFG
import pyformlang
import networkx as nx
from typing import Tuple

def cfg_to_weak_normal_form(cfg: pyformlang.cfg.CFG) -> pyformlang.cfg.CFG:
    gramm1 = cfg.eliminate_unit_productions().remove_useless_symbols()
    long_rules = gramm1._get_productions_with_only_single_terminals()
    new_rules = set(gramm1._decompose_productions(long_rules))
    return CFG(start_symbol=gramm1.start_symbol, production=new_rules)


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