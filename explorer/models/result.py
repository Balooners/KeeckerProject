from dataclasses import dataclass

@dataclass
class Result:
    port: int
    protocol: str
    status: str
    details: dict