from dataclasses import dataclass, field
from typing import Any


@dataclass
class TableConfig:
    columns: dict[str, str | dict[str, Any]] = field(default_factory=dict)
    clean: bool = False
    drop: bool = False


@dataclass
class SanitizeConfig:
    tables: dict[str, TableConfig] = field(default_factory=dict)
