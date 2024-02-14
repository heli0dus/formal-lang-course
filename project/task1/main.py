import cfpq_data as cfpq

from networkx.classes.reportviews import OutMultiEdgeView
from networkx.drawing.nx_pydot import write_dot

from dataclasses import dataclass


@dataclass
class GraphData:
    nodes: int
    edges: int
    labels: OutMultiEdgeView


def get_graph_params(name):
    path = cfpq.download(name)
    graph = cfpq.graph_from_csv(path)
    return GraphData(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        graph.edges(data='label')
    )


def two_cycle_graph_dotfile(path, n, m, labels):
    graph = cfpq.labeled_two_cycles_graph(n, m, labels=labels)
    write_dot(graph, path)
