from dataclasses import dataclass, field


@dataclass
class TableConfig:
    columns: list[dict[str, str]] = field(default_factory=list)
    clean: bool = False
    drop: bool = False


@dataclass
class SanitizeConfig:
    tables: dict[str, TableConfig] = field(default_factory=dict)
