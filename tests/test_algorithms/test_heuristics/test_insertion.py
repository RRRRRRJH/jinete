import unittest

import jinete as jit

from tests.utils import (
    generate_vehicles,
    generate_trips,
)


class TestInsertionAlgorithm(unittest.TestCase):

    def test_creation(self):
        job = jit.Job(generate_trips(10), objective_cls=jit.DialARideObjective)
        fleet = jit.Fleet(generate_vehicles(10))
        algorithm = jit.InsertionAlgorithm(
            crosser_cls=jit.Crosser,
            job=job,
            fleet=fleet,
        )
        self.assertEqual(algorithm.crosser_cls, jit.Crosser)
        self.assertEqual(algorithm.job, job)
        self.assertEqual(algorithm.fleet, fleet)


if __name__ == '__main__':
    unittest.main()
