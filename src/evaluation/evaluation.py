from typing import Callable

from matplotlib import pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit_algorithms.optimizers import COBYLA, SPSA

from api_client import ApiClient
from generation import TspCircuitGenerator


def show_histogram(counts: dict[str, int], title: str = ""):
    plot_histogram(counts)
    if title:
        plt.title(title, fontsize=10)
    plt.show()


def filter_counts(filter_function: Callable[[str], bool], counts: dict[str, int]) -> dict[str, int]:
    return dict(filter(lambda item: filter_function(item[0]), counts.items()))


def evaluate_counts(counts: dict[str, int], solutions: set[str]) -> tuple[int, int, float]:
    correct_counts = 0

    for bitstring in solutions:
        if bitstring in counts.keys():
            correct_counts += counts[bitstring]

    all_counts = sum(counts.values())
    return correct_counts, all_counts, correct_counts / all_counts


def evaluate_tsp():
    tsp = TspCircuitGenerator(3)
    tsp_solution = tsp.solution_to_bitstrings(tsp.solve_by_brute_force())
    print(f"optimal solution: {tsp_solution}")

    evaluate_tsp_ideal(tsp, tsp_solution)
    evaluate_tsp_noisy(tsp, tsp_solution)


def evaluate_tsp_ideal(tsp: TspCircuitGenerator, tsp_solution: set[str]):
    optimizer = COBYLA
    optimizer_iterations = 500
    qaoa_iterations = 3
    qubo_penalty = None

    circuit = tsp.generate_openqasm(optimizer, optimizer_iterations, qaoa_iterations, qubo_penalty)
    info = f"opt={optimizer.__name__}, " \
           f"opt_iter={optimizer_iterations}, qaoa_iter={qaoa_iterations}, qubo_penalty={qubo_penalty}," \
           f"\nconstraints=None"

    evaluate_single_tsp(circuit, tsp, tsp_solution, "ibm", description=f"{info}\nIBM ideal")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "ionq", description=f"{info}\nIonQ ideal")


def evaluate_tsp_noisy(tsp: TspCircuitGenerator, tsp_solution: set[str]):
    optimizer = SPSA
    optimizer_iterations = 500
    qaoa_iterations = 2
    qubo_penalty = 150

    circuit = tsp.generate_openqasm(optimizer, optimizer_iterations, qaoa_iterations, qubo_penalty)
    info = f"opt={optimizer.__name__}, " \
           f"opt_iter={optimizer_iterations}, qaoa_iter={qaoa_iterations}, qubo_penalty={qubo_penalty}," \
           f"\nconstraints=None"

    evaluate_single_tsp(circuit, tsp, tsp_solution, "ibm", "montreal",
                        description=f"{info}\nIBM Montreal")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "ibm", "washington",
                        description=f"{info}\nIBM Washington")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "ionq", "aria-1",
                        description=f"{info}\nIonQ Aria 1")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "iqm", "apollo",
                        description=f"{info}\nIQM Apollo")


def evaluate_single_tsp(circuit: str, tsp: TspCircuitGenerator, tsp_solution: set[str],
                        vendor: str, noisy_backend: str | None = None, filtering=False,
                        description: str = ""):
    counts = ApiClient.simulate_circuit(circuit, vendor, noisy_backend=noisy_backend)["counts"]
    if filtering:
        counts = filter_counts(tsp.check_for_valid_tour, counts)
    show_histogram(counts, description)

    right_counts, all_counts, percentage = evaluate_counts(counts, tsp_solution)
    print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")


if __name__ == '__main__':
    evaluate_tsp()
