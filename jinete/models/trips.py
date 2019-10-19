from __future__ import annotations

import logging
from typing import (
    TYPE_CHECKING,
    Optional,
)
from .constants import (
    MAX_FLOAT,
)

if TYPE_CHECKING:
    from typing import (
        Dict,
        Any,
    )
    from .positions import (
        Position,
    )

logger = logging.getLogger(__name__)


class Trip(object):
    __slots__ = (
        'identifier',
        'origin_position',
        'origin_earliest',
        'origin_latest',
        'origin_duration',
        'destination_position',
        'destination_earliest',
        'destination_latest',
        'destination_duration',
        'on_time_bonus',
        'capacity',
    )
    identifier: str
    origin_position: Position
    destination_position: Position
    origin_earliest: float
    timeout: Optional[float]
    on_time_bonus: float
    origin_duration: float
    capacity: float

    def __init__(self, identifier: str, origin_position: Position, destination_position: Position,
                 origin_earliest: float = 0.0, origin_latest: float = MAX_FLOAT, on_time_bonus: float = 0.0,
                 origin_duration: float = 0.0, capacity: float = 1, destination_earliest: float = 0.0,
                 destination_latest: float = MAX_FLOAT, destination_duration: float = 0.0):
        self.identifier = identifier
        self.origin_position = origin_position
        self.origin_earliest = origin_earliest
        self.origin_latest = origin_latest
        self.origin_duration = origin_duration

        self.destination_position = destination_position
        self.destination_earliest = destination_earliest
        self.destination_latest = destination_latest
        self.destination_duration = destination_duration

        self.on_time_bonus = on_time_bonus
        self.capacity = capacity

    @property
    def empty(self) -> bool:
        return self.capacity == 0

    @property
    def distance(self) -> float:
        return self.origin_position.distance_to(self.destination_position)

    def duration(self, now: float):
        return self.origin_position.time_to(self.destination_position, now)

    def __deepcopy__(self, memo: Dict[int, Any]) -> Trip:
        return self
