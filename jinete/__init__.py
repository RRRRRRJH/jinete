"""
High Performance solving suite for the Pickup and Delivery Problem and its related extensions.
"""

from ._version import (
    __version__,
    VERSION,
)

from .models import (
    Position,
    GeometricPosition,
    Surface,
    GeometricSurface,
    DistanceMetric,
    Service,
    Trip,
    Job,
    Vehicle,
    Fleet,
    Route,
    Planning,
    PlannedTrip,

    Stop,

    Result,

    OptimizationDirection,

    Objective,
    DialARideObjective,
    TaxiSharingObjective,
    HashCodeObjective,

    RouteCriterion,
    ShortestAveragePlannerTripDurationCriterion,
    EarliestLastDepartureTimeRouteCriterion,
    ShortestTimeRouteCriterion,
    LongestTimeRouteCriterion,
    LongestUtilTimeRouteCriterion,
    HashCodeRouteCriterion,

    MAX_INT,
    MIN_INT,
    MAX_FLOAT,
    MIN_FLOAT,
)

from .loaders import (
    LoaderException,
    LoaderFormatterException,
    Loader,
    FileLoader,
    LoaderFormatter,
    HashCodeLoaderFormatter,
    CordeauLaporteLoaderFormatter,
)

from .dispatchers import (
    Dispatcher,
    StaticDispatcher,
)

from .storers import (
    StorerFormatter,
    ColumnarStorerFormatter,
    HashCodeStorerFormatter,
    Storer,
    FileStorer,
    PromptStorer,
    GraphPlotStorer,
    StorerSet,
)

from .algorithms import (
    Algorithm,
    NaiveAlgorithm,
    InsertionAlgorithm,
    LocalSearchAlgorithm,
    GraspAlgorithm,
    SequentialAlgorithm,
    MilpAlgorithm,
    IterativeAlgorithm,
    InsertionIterator,
    StatelessInsertionIterator,
    BestStatelessInsertionIterator,
    RankingInsertionIterator,
    LocalSearchStrategy,
    OneShiftLocalSearchStrategy,
    TwoOPTLocalSearchStrategy,
    ReallocationLocalSearchStrategy,
    InsertionStrategy,
    SamplingInsertionStrategy,
    IntensiveInsertionStrategy,
    TailInsertionStrategy,
)

from .exceptions import (
    JineteException,
    NonFeasiblePlannedTripException,
    NonFeasibleRouteException,
    PreviousStopNotInRouteException,
)
from .solvers import (
    Solver,
)
