from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import (
    uuid4,
)

if TYPE_CHECKING:
    from typing import (
        Set,
    )
    from .routes import (
        Route,
    )
    from uuid import (
        UUID,
    )

logger = logging.getLogger(__name__)


class Planning(object):
    routes: Set[Route]
    computation_time: float
    uuid: UUID

    def __init__(self, routes: Set[Route], uuid: UUID = None):
        if uuid is None:
            uuid = uuid4()

        self.routes = routes
        self.uuid = uuid

    @property
    def loaded_routes(self):
        return set(route for route in self.routes if route.loaded)

    @property
    def cost(self) -> float:
        cost = 0.0
        for route in self.routes:
            cost += route.cost
        return cost

    @property
    def scoring(self) -> float:
        scoring = 0.0
        for route in self.routes:
            scoring += route.scoring
        return scoring

    def __lt__(self, other: 'Planning') -> bool:
        return self.cost < other.cost
