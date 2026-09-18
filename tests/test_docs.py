"""Coherence entre ce que la documentation annonce et ce que le depot fait.

Un nombre ecrit dans un document ne se maintient pas tout seul. Celui des cas de mutation
a derive deux fois -- 28 annonces pour 33 puis 34 reels -- et l'enumeration des familles
avait rate ROUT et REG en entier, alors meme que CONTRIBUTING.md demande au point 4 de
verifier que le total monte. Ces tests virent au rouge au lieu de laisser le paragraphe
vieillir en silence.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "tests" / "mutation_check.sh"
CONTRIBUTING = RACINE / "CONTRIBUTING.md"


def _cas() -> list[str]:
    """Les identifiants de cas reellement executes par le script, dans l'ordre."""
    return re.findall(r'run_case "([A-Z]+)([0-9]+)"', SCRIPT.read_text(encoding="utf-8"))


class TestCasDeMutationAnnoncesParContributing(unittest.TestCase):
    def test_le_total_annonce_est_celui_du_script(self):
        annonce = re.search(r"(\d+)\s+cases\s+in\s+total", CONTRIBUTING.read_text(encoding="utf-8"))
        self.assertIsNotNone(annonce, "CONTRIBUTING.md n'annonce plus aucun total de cas")
        self.assertEqual(
            int(annonce.group(1)), len(_cas()),
            "le total annonce par CONTRIBUTING.md a derive du nombre de run_case du script",
        )

    def test_chaque_famille_est_citee_jusqu_a_son_dernier_cas(self):
        # Citer CARTE1..CARTE5 quand CARTE6 existe est le defaut exact qui a motive ce
        # test : le total pouvait etre juste et l'enumeration fausse.
        texte = CONTRIBUTING.read_text(encoding="utf-8")
        derniers: dict[str, int] = {}
        for prefixe, numero in _cas():
            derniers[prefixe] = max(derniers.get(prefixe, 0), int(numero))
        for prefixe, numero in sorted(derniers.items()):
            # assertTrue et non assertIn : l'echec doit nommer le cas manquant, pas
            # deverser CONTRIBUTING.md en entier dans la sortie de test.
            self.assertTrue(
                f"{prefixe}{numero}" in texte,
                f"{prefixe}{numero} tourne dans mutation_check.sh mais CONTRIBUTING.md "
                "ne cite pas sa famille jusqu'a lui",
            )


if __name__ == "__main__":
    unittest.main()
