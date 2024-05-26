from project.gflpql.project.gflpqlLexer import gflpqlLexer
from project.gflpql.project.gflpqlParser import gflpqlParser
from project.gflpql.project.gflpqlVisitor import gflpqlVisitor
from project.gflpql.project.gflpqlListener import gflpqlListener

from antlr4 import *
from antlr4.InputStream import InputStream


class NodeCountListener(gflpqlListener):

    def __init__(self) -> None:
        super(gflpqlListener, self).__init__()
        self.count = 0

    def enterEveryRule(self, ctx):
        self.count += 1


class StringingListener(gflpqlListener):
    res = ""

    def __init__(self):
        super(gflpqlListener, self).__init__()

    def enterEveryRule(self, rule):
        res += rule.getText()


def prog_to_tree(program: str) -> tuple[ParserRuleContext, bool]:
    parser = gflpqlParser(CommonTokenStream(gflpqlLexer(InputStream(program))))
    prog = parser.prog()
    correct = parser.getNumberOfSyntaxErrors() == 0
    return (prog, correct)


def nodes_count(tree: ParserRuleContext) -> int:
    listener = NodeCountListener()
    tree.enterRule(listener)
    # ParseTreeWalker.walk(listener, tree)
    return listener.count


def tree_to_prog(tree: ParserRuleContext) -> str:
    listener = StringingListener()
    tree.enterRule(listener)
    # ParseTreeWalker.walk(listener, tree)
    return listener.res
