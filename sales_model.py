from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class SaleLine:
    product_id: int
    quantity: int
    unit_price: float

@dataclass
class Sale:
    """Simple sales model stub."""
    id: int | None = None
    customer_id: int | None = None
    lines: List[SaleLine] = field(default_factory=list)
    total: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def compute_total(self) -> float:
        self.total = sum(l.quantity * l.unit_price for l in self.lines)
        return self.total
