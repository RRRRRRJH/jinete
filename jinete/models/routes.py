from __future__ import annotations

import logging
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
)
from uuid import (
    uuid4,
)

from ..exceptions import (
    PreviousStopNotInRouteException,
)
from .abc import (
    Model,
)
from .planned_trips import (
    PlannedTrip,
)
from .stops import (
    Stop,
)

if TYPE_CHECKING:
    from typing import (
        List,
        Iterator,
        Any,
        Dict,
        Optional,
        Iterable,
        Generator,
        Tuple,
    )
    from uuid import (
        UUID,
    )
    from .vehicles import (
        Vehicle,
    )
    from .trips import (
        Trip,
    )
    from .positions import (
        Position,
    )

logger = logging.getLogger(__name__)


class Route(Model):
    vehicle: Vehicle
    uuid: UUID
    stops: List[Stop]

    def __init__(self, vehicle: Vehicle, stops: List[Stop] = None, uuid: UUID = None):

        if uuid is None:
            uuid = uuid4()
        self.uuid = uuid

        self.vehicle = vehicle

        if stops is None:
            first = Stop(self, self.vehicle.origin_position, None)
            last = Stop(self, self.vehicle.destination_position, first)
            first.following = last
            self.stops = [
                first, last,
            ]
        else:
            self.stops = list(stops)

    def __deepcopy__(self, memo: Dict[int, Any]) -> Route:
        vehicle = deepcopy(self.vehicle, memo)

        route = Route(vehicle)
        memo[id(self)] = route

        route.stops = deepcopy(self.stops, memo)

        return route

    @property
    def planned_trips(self) -> Iterator[PlannedTrip]:
        yield from self.deliveries

    @property
    def pickups(self) -> Iterator[PlannedTrip]:
        for stop in self.stops:
            yield from stop.pickups

    @property
    def deliveries(self) -> Iterator[PlannedTrip]:
        for stop in self.stops:
            yield from stop.deliveries

    @property
    def feasible(self) -> bool:
        for stop in self.stops:
            stop.flush()

        if any(self.planned_trips):
            if not self.first_stop.position == self.vehicle.origin_position:
                return False
            if not self.vehicle.origin_earliest <= self.first_stop.arrival_time:
                return False
            if not self.last_position == self.vehicle.destination_position:
                return False
            if not self.last_departure_time <= self.vehicle.origin_latest:
                return False

        # if __debug__:
        #     for stop in self.stops:
        #         assert stop.route == self
        #
        #     for one, two in zip(self.stops[:-2], self.stops[1:-1]):
        #         assert one.following == two
        #         assert two.previous == one
        #         assert one.position != two.position

        for planned_trip in self.planned_trips:
            if not planned_trip.feasible:
                return False
        return True

    @property
    def loaded(self):
        return any(self.planned_trips)

    @property
    def trips(self) -> Iterator[Trip]:
        yield from (planned_trip.trip for planned_trip in self.planned_trips)

    @property
    def loaded_planned_trips(self) -> Iterator[PlannedTrip]:
        yield from (planned_trip for planned_trip in self.planned_trips if not planned_trip.empty)

    @property
    def loaded_trips(self) -> Iterator[Trip]:
        yield from (planned_trip.trip for planned_trip in self.loaded_planned_trips)

    @property
    def loaded_trips_count(self) -> int:
        return sum(1 for _ in self.loaded_trips)

    @property
    def first_stop(self) -> Stop:
        stop = self.stops[0]
        assert stop.previous is None
        return stop

    @property
    def first_arrival_time(self) -> float:
        return self.first_stop.arrival_time

    @property
    def first_departure_time(self) -> float:
        return self.first_stop.departure_time

    @property
    def last_stop(self) -> Stop:
        stop = self.stops[-1]
        return stop

    @property
    def last_arrival_time(self) -> float:
        return self.last_stop.arrival_time

    @property
    def last_departure_time(self) -> float:
        return self.last_stop.departure_time

    @property
    def last_position(self) -> Position:
        return self.last_stop.position

    @property
    def current_stop(self) -> Stop:
        stop = self.stops[-2]
        return stop

    @property
    def current_arrival_time(self) -> float:
        return self.current_stop.arrival_time

    @property
    def current_departure_time(self) -> float:
        return self.current_stop.departure_time

    @property
    def current_position(self) -> Position:
        return self.current_stop.position

    @property
    def duration(self) -> float:
        return self.last_departure_time - self.first_arrival_time

    @property
    def vehicle_identifier(self) -> Optional[str]:
        if self.vehicle is None:
            return None
        return self.vehicle.identifier

    def __iter__(self) -> Generator[Tuple[str, Any], None, None]:
        yield from (
            ('uuid', self.uuid),
            ('vehicle_identifier', self.vehicle_identifier),
            ('trip_identifiers', tuple(trip.identifier for trip in self.trips))
        )

    def conjecture_trip(self, trip: Trip, previous: Stop = None, following: Stop = None) -> Route:
        assert following is None or (previous is not None and following is not None)

        if previous is None:
            previous = self.current_stop
        if following is None:
            following = self.last_stop
        assert previous != following
        assert previous in following.all_previous
        assert following in previous.all_following
        assert previous.departure_time <= following.arrival_time

        previous_idx = self.stops.index(previous)
        following_idx = self.stops.index(following)

        route = deepcopy(self)

        previous_pickup = route.stops[previous_idx]
        pickup = Stop(route, trip.origin_position, previous_pickup)
        if previous_idx + 1 == following_idx:
            previous_delivery = pickup
        else:
            previous_delivery = route.stops[following_idx - 1]
        delivery = Stop(route, trip.destination_position, previous_delivery)
        planned_trip = PlannedTrip(route=route, trip=trip, pickup=pickup, delivery=delivery)
        route.append_planned_trip(planned_trip)
        return route

    def intensive_conjecture_trip(self, trip: Trip) -> List[Route]:
        routes = list()
        for i, previous in enumerate(self.stops[:-1]):
            for following in self.stops[i + 1:]:
                route = self.conjecture_trip(trip, previous, following)
                routes.append(route)
        return routes

    def sampling_conjecture_trip(self, trip: Trip, count: int) -> List[Route]:
        from random import randint

        indices = set()
        for _ in range(count):
            sampled_i = randint(0, len(self.stops) - 2)
            sampled_j = randint(sampled_i + 1, len(self.stops) - 1)
            pair = (sampled_i, sampled_j)
            indices.add(pair)

        planned_trips = list()
        for i, j in indices:
            if j is None:
                planned_trip = self.conjecture_trip(trip, self.stops[i])
            else:
                planned_trip = self.conjecture_trip(trip, self.stops[i], self.stops[j])
            planned_trips.append(planned_trip)

        return planned_trips

    def conjecture_trip_in_batch(self, iterable: Iterable[Trip]) -> List[Route]:
        # return sum((self.sampling_conjecture_trip(trip, 100) for trip in iterable), [])
        return sum((self.intensive_conjecture_trip(trip) for trip in iterable), [])
        # return [self.conjecture_trip(trip) for trip in iterable]

    def insert_stop(self, stop: Stop) -> Stop:
        for idx in range(len(self.stops)):
            if self.stops[idx] != stop.previous:
                continue
            return self.insert_stop_at(idx + 1, stop)
        raise PreviousStopNotInRouteException(stop)

    def insert_stop_at(self, idx: int, stop: Stop) -> Stop:
        previous_stop = self.stops[idx - 1]

        if previous_stop == stop:
            return stop

        assert set(stop.pickups).isdisjoint(stop.deliveries)

        stop.previous = previous_stop
        if previous_stop == stop:
            previous_stop.merge(stop)
            return previous_stop

        following_stop = previous_stop.following
        if following_stop is not None:
            following_stop.previous = stop
            stop.following = following_stop
        previous_stop.following = stop

        self.stops.insert(idx, stop)

        self.first_stop.flush_all_following()
        return stop

    def append_planned_trip(self, planned_trip: PlannedTrip):
        assert planned_trip.delivery is not None
        assert planned_trip.pickup is not None

        self.insert_stop(planned_trip.pickup)
        self.insert_stop(planned_trip.delivery)

        assert all(self.stops[i] == self.stops[i + 1].previous for i in range(len(self.stops) - 1))
        assert all(self.stops[i].following == self.stops[i + 1] for i in range(len(self.stops) - 1))
        logger.info(f'Append trip "{planned_trip.trip_identifier}" identifier to route "{self.uuid}".')
