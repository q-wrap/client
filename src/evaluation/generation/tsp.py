import math
from itertools import permutations

import networkx
import numpy
import qiskit
from qiskit import qasm2
from qiskit.primitives import Sampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import Optimizer, SPSA
from qiskit_optimization.applications import Tsp
from qiskit_optimization.converters import QuadraticProgramToQubo

from .generator import CircuitGenerator


class TspCircuitGenerator(CircuitGenerator):
    def __init__(self, number_of_cities: int, seed: int = None):
        self.instance = Tsp.create_random_instance(number_of_cities, seed=seed)

    def generate_openqasm(self,
                          optimizer: type(Optimizer),
                          optimizer_iterations: int,
                          qaoa_iterations: int,
                          qubo_penalty: float | None = None,
                          optimizer_learning_rate: float | None = None,
                          optimizer_perturbation: float | None = None,
                          ) -> str:
        qp = self.instance.to_quadratic_program()
        qubo = QuadraticProgramToQubo(penalty=qubo_penalty).convert(qp)
        operator, _ = qubo.to_ising()
        if optimizer == SPSA:
            qaoa = QAOA(sampler=Sampler(), optimizer=optimizer(
                maxiter=optimizer_iterations,
                learning_rate=optimizer_learning_rate,
                perturbation=optimizer_perturbation,
            ), reps=qaoa_iterations)
        else:
            qaoa = QAOA(sampler=Sampler(), optimizer=optimizer(
                maxiter=optimizer_iterations,
            ), reps=qaoa_iterations)


        optimal_params = qaoa.compute_minimum_eigenvalue(operator).optimal_point
        circuit = qaoa.ansatz.assign_parameters(optimal_params)

        return qiskit.qasm2.dumps(circuit)

    def solve_by_brute_force(self) -> set[tuple[int, ...]]:
        distance_matrix = networkx.to_numpy_array(self.instance.graph)
        number_of_cities = distance_matrix.shape[0]
        all_routes = list(permutations(range(1, number_of_cities)))

        shortest_distance = None
        optimal_routes = set()

        for route in all_routes:
            distance = 0
            previous_city = 0

            for city in route:
                distance += distance_matrix[city, previous_city]
                previous_city = city

            distance += distance_matrix[previous_city, 0]
            full_route = (0,) + route

            if shortest_distance is None or distance < shortest_distance:
                shortest_distance = distance
                optimal_routes = {full_route}
            elif distance == shortest_distance:
                optimal_routes.add(full_route)

        return optimal_routes

    @classmethod
    def solution_to_bitstrings(cls, solution: set[tuple[int, ...]]) -> set[str]:
        return {cls.tour_to_matrix(tour) for tour in solution}

    @staticmethod
    def tour_to_matrix(tour: tuple[int, ...]) -> str:
        n = len(tour)
        matrix = numpy.zeros((n, n), dtype=int)

        for i in range(n):
            from_city = tour[i]
            to_city = tour[(i + 1) % n]
            matrix[from_city, to_city] = 1

        return "".join(str(city) for city in matrix.ravel())

    @staticmethod
    def matrix_to_tour(matrix_bitstring: str) -> tuple[int, ...]:
        n = math.sqrt(len(matrix_bitstring))
        if not n.is_integer():
            raise ValueError("Invalid matrix bitstring: Length must be a perfect square.")

        n = int(n)
        matrix = numpy.fromiter((int(b) for b in matrix_bitstring), dtype=int).reshape((n, n))
        if not (numpy.all(matrix.sum(axis=0) == 1) and numpy.all(matrix.sum(axis=1) == 1)):
            raise ValueError("Invalid matrix bitstring: Each city must be arrived and departed exactly once.")

        tour = [0]
        visited = {0}

        while len(tour) < n:
            next_city = next((j for j in range(n) if matrix[tour[-1], j] == 1 and j not in visited), None)

            if next_city is None:
                raise ValueError("Invalid matrix bitstring: No Hamiltonian cycle found.")

            tour.append(next_city)
            visited.add(next_city)

        return tuple(tour)

    @classmethod
    def check_for_valid_tour(cls, matrix_bitstring: str) -> bool:
        try:
            cls.matrix_to_tour(matrix_bitstring)
            return True
        except ValueError:
            return False
