"""
"""


from typing import Dict, Set, List, Optional, Tuple

from core.facts import Fact
from core.tms_engine import TruthMaintenanceSystem


class KnowledgeBase:
    """
    Минимальный граф знаний с поддержкой ограничений целостности (онтологии) и JTMS.
    """
    def __init__(self):
        self.facts: Dict[str, Fact] = {}
        self.tms = TruthMaintenanceSystem()

        # Минимальная онтология (TBox): задаем однозначные (функциональные) отношения.
        # Например, человек может работать только в одной компании или жить в одном городе одновременно.
        self.functional_relations: Set[str] = {"works_at", "lives_in", "has_gout_diagnosis"}

    def add_fact(self, subject: str, relation: str, value: str,
                 confidence: float = 1.0,
                 premises: Optional[Set[str]] = None,
                 source: str = "direct_input",
                 discourse_role: str = "nucleus",
                 discourse_weight: float = 1.0) -> Fact:

        # Создаем новый факт
        fact = Fact(
            subject=subject.strip(),
            relation=relation.strip(),
            value=value.strip(),
            confidence=confidence,
            discourse_role=discourse_role,
            discourse_weight=discourse_weight
        )
        self.facts[fact.id] = fact

        # Если есть предпосылки, регистрируем их в JTMS
        if premises:
            self.tms.add_justification(fact.id, premises, source=source)

        return fact

    def get_active_facts(self) -> List[Fact]:
        return [f for f in self.facts.values() if f.is_active]

    def get_active_ids(self) -> Set[str]:
        return {f.id for f in self.facts.values() if f.is_active}

    def detect_conflicts(self, candidate: Fact) -> List[Fact]:
        """
        Ищет конфликты в базе знаний на основе правил онтологии (однозначных отношений).
        """
        if candidate.relation not in self.functional_relations:
            return []
            
        conflicts = []
        for fact in self.get_active_facts():
            if (fact.subject == candidate.subject and 
                fact.relation == candidate.relation and 
                fact.value.lower() != candidate.value.lower()):
                conflicts.append(fact)
        return conflicts

    def resolve_conflicts(self, new_fact: Fact, conflicts: List[Fact]) -> Tuple[List[str], List[str]]:
        """
        Разрешает конфликты на основе уверенности (Confidence) или политики Latest-Value-Wins.
        Производит каскадный пересмотр убеждений (Belief Revision).
        """
        retracted = []
        kept = []
        
        for old_fact in conflicts:
            # Стратегия разрешения конфликтов: сравниваем уверенность (Confidence-based arbitration)
            if new_fact.confidence >= old_fact.confidence:
                self.retract_fact_cascade(old_fact.id)
                retracted.append(old_fact.id)
            else:
                # Если новый факт менее достоверен, мы деактивируем новый факт
                self.retract_fact_cascade(new_fact.id)
                retracted.append(new_fact.id)
                
        return retracted, kept

    def retract_fact_cascade(self, fact_id: str):
        """
        Каскадно отзывает (деактивирует) факт и все логические следствия, которые на него опирались.
        """
        if fact_id not in self.facts or not self.facts[fact_id].is_active:
            return
            
        # Мягкое удаление текущего факта
        self.facts[fact_id].is_active = False
        
        # Находим все факты, которые использовали этот факт как предпосылку
        dependent_consequences = self.tms.premise_to_consequences.get(fact_id, set())
        active_ids = self.get_active_ids()
        
        for consequence_id in dependent_consequences:
            if consequence_id in self.facts and self.facts[consequence_id].is_active:
                # Проверяем, осталось ли у следствия хоть одно другое активное обоснование
                if not self.tms.is_well_justified(consequence_id, active_ids):
                    # Если нет - каскадно отзываем его
                    self.retract_fact_cascade(consequence_id)

    def print_state(self, title: str = "Текущее состояние базы знаний"):
        print(f"\n--- {title} ---")
        active = [f for f in self.facts.values() if f.is_active]
        inactive = [f for f in self.facts.values() if not f.is_active]
        
        print("Активные факты:")
        for f in active:
            print(f"  {f}")
            # Выводим зависимости, если они есть
            if f.id in self.tms.justifications:
                for just in self.tms.justifications[f.id]:
                    premises_str = ", ".join([self.facts[p].value[:15] + "..." for p in just.premise_ids if p in self.facts])
                    print(f"    [Обоснование: {just.source} на основе [{premises_str}]]")
                    
        if inactive:
            print("Отозванные (неактивные) факты:")
            for f in inactive:
                print(f"  {f}")
        print("-" * (len(title) + 8))
