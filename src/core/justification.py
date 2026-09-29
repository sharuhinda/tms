"""
"""

from uuid import uuid4
import datetime as dt

from typing import Set
from pydantic import BaseModel, Field


class Justification(BaseModel):
    """
    Обоснование для JTMS (Justification-based Truth Maintenance System).
    Связывает следствие (consequence) с набором предпосылок (premises).
    """
    id: str = Field(default_factory=lambda: uuid4().hex, description="Justification ID")
    consequence_id: str = ""
    premise_ids: Set[str] = Field(default_factory=set)
    source: str = "direct_input"  # откуда пришел факт (например, "user_utterance", "rule_inference")
