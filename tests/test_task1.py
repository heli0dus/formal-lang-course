import project.task1 as task1
from os import path
import filecmp
import tempfile


wd = path.dirname(path.realpath(__file__))


def test_get_graph_params():
    with open(f"{wd}/data/task1/edges", "r") as f:
        edges_data = f.readline().strip()

    graph_data = task1.get_graph_params("generations")

    nodes = 129
    edges = 273

    assert nodes == graph_data.nodes
    assert edges == graph_data.edges
    assert edges_data == str(graph_data.labels).strip()


def test_two_cycle_graph_dotfile():
    with tempfile.NamedTemporaryFile() as tmp:
        path = tmp.name
    n = 200
    m = 201
    task1.two_cycle_graph_dotfile(tmp.name, n, m, ["a", "b"])
    assert filecmp.cmp(f"{wd}/data/task1/twocycles.dot", path)
