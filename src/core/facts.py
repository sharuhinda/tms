"""
Contains Fact class description
"""


from uuid import uuid4
import datetime as dt

from typing import Optional
from pydantic import BaseModel, Field


class Fact(BaseModel):
    """
    Main class to store knowledge facts in `subject` - `relation` - `value` format

    [TODO]
    - decide if this class should contain field stating it's a part of ontology or knowledge graph
    """
    id: str = Field(default_factory=lambda: uuid4().hex, description="Fact ID")
    subject: str = ""
    relation: str = ""
    value: str = ""
    confidence: float = Field(default=0., ge=0., le=1.)  # Вероятностная оценка (0.0 - 1.0) для будущих Байесовских методов/PSL
    is_active: bool = True   # Мягкое удаление (soft delete) для поддержки ревизии убеждений
    created_at: dt.datetime = Field(default_factory=dt.datetime.now)
    valid_from: dt.datetime = Field(default_factory=dt.datetime.now)
    valid_until: Optional[dt.datetime] = None  # Для ограничения времени действия фактов (например, при устаревании информации)

    # Резервные поля для будущих расширений (RST и Дискурсивный анализ)
    discourse_role: str = "nucleus"  # 'nucleus' или 'satellite' для RST
    discourse_weight: float = 1.0     # Вес риторической важности

    def __repr__(self):
        status = "ACT" if self.is_active else "DEL"
        return f"Fact[{self.id[:6]}][{status}] ({self.subject} --{self.relation}--> {self.value}) [conf={self.confidence:.2f}, rst={self.discourse_role}]"
