from pyformlang.cfg import CFG


def to_wnf(gramm: CFG) -> CFG:
    gramm1 = gramm.eliminate_unit_productions().remove_useless_symbols()
    long_rules = gramm1._get_productions_with_only_single_terminals()
    new_rules = set(gramm1._decompose_productions(long_rules))
    return CFG(start_symbol=gramm1.start_symbol, production=new_rules)


def gramm_from_file(filepath: str) -> CFG:
    with open(filepath) as f:
        return CFG.from_text("".join(l for l in f))
