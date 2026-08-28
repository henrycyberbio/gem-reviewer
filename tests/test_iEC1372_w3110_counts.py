from pathlib import Path

from gem_reviewer.sbml import count_entities


GEM_PATH = Path("data/gem/iEC1372_W3110.xml")


def test_frozen_iEC1372_w3110_entity_counts_match_bigg_record() -> None:
    assert count_entities(GEM_PATH) == {
        "metabolites": 1918,
        "reactions": 2758,
        "genes": 1372,
    }
