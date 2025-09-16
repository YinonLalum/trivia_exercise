from dataclasses import dataclass
from hashlib import md5


@dataclass
class Player:
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Player name must be a non-empty string")

    def __hash__(self) -> int:
        return int(md5(self.name.encode('utf-8')).hexdigest(), 16)
