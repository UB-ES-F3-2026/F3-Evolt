from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    xp: int = 0  # Les recàrregues no el modifiquen (US-09, criteri 6).

    def __post_init__(self) -> None:
        if self.xp < 0:
            raise ValueError("xp no pot ser negatiu")
