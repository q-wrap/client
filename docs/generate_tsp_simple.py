# simplified version of the TSP circuit generation code (src.evaluation.generation.tsp.TspCircuitGenerator)

import qiskit
from qiskit import qasm2
from qiskit.primitives import Sampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.applications import Tsp
from qiskit_optimization.converters import QuadraticProgramToQubo


def generate_tsp_circuit(n: int, seed: int) -> str:
    instance = Tsp.create_random_instance(n=n, seed=seed)

    qp = instance.to_quadratic_program()
    qubo = QuadraticProgramToQubo(penalty=None).convert(qp)
    operator, _ = qubo.to_ising()
    qaoa = QAOA(
        sampler=Sampler(),
        optimizer=COBYLA(maxiter=500),
        reps=3
    )
    optimal_params = qaoa.compute_minimum_eigenvalue(operator).optimal_point
    circuit = qaoa.ansatz.assign_parameters(optimal_params)

    return qiskit.qasm2.dumps(circuit)
