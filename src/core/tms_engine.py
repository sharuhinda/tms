"""
"""

from typing import Dict, List, Set

from core.justification import Justification


class TruthMaintenanceSystem:
    """
    Легковесный JTMS движок для отслеживания зависимостей и каскадного удаления фактов.
    """
    def __init__(self):
        self.justifications: Dict[str, List[Justification]] = {}  # consequence_id -> list of justifications
        self.premise_to_consequences: Dict[str, Set[str]] = {}     # premise_id -> set of consequence_ids

    def add_justification(self, consequence_id: str, premise_ids: Set[str], source: str = "direct_input"):
        just = Justification(consequence_id=consequence_id, premise_ids=premise_ids, source=source)
        if consequence_id not in self.justifications:
            self.justifications[consequence_id] = []
        self.justifications[consequence_id].append(just)

        for premise_id in premise_ids:
            if premise_id not in self.premise_to_consequences:
                self.premise_to_consequences[premise_id] = set()
            self.premise_to_consequences[premise_id].add(consequence_id)

    def is_well_justified(self, fact_id: str, active_fact_ids: Set[str]) -> bool:
        """
        Проверяет, имеет ли факт хотя бы одно активное обоснование.
        Утверждения, введенные пользователем напрямую (без предпосылок), всегда обоснованы.
        """
        if fact_id not in self.justifications or not self.justifications[fact_id]:
            return True  # Базовое допущение / прямой ввод

        for just in self.justifications[fact_id]:
            # Обоснование активно, если все его предпосылки активны
            if just.premise_ids.issubset(active_fact_ids):
                return True
        return False
