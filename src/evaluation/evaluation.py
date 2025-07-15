from typing import Callable

from matplotlib import pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit_algorithms.optimizers import COBYLA, SPSA

from api_client import ApiClient
from generation import TspCircuitGenerator


def show_histogram(counts: dict[str, int], title: str = ""):
    plot_histogram(counts)
    plt.gca().set_ylabel("")
    plt.subplots_adjust(top=0.93, right=0.98, left=0.07, bottom=0.12)
    if title:
        plt.title(title, fontsize=12)
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
    seed = 123
    tsp = TspCircuitGenerator(2, seed)
    tsp_solution = tsp.solution_to_bitstrings(tsp.solve_by_brute_force())
    print(f"optimal solution: {tsp_solution}")

    evaluate_tsp_ideal(tsp, tsp_solution, seed)
    evaluate_tsp_noisy(tsp, tsp_solution, seed)


def evaluate_tsp_ideal(tsp: TspCircuitGenerator, tsp_solution: set[str], seed: int):
    optimizer = COBYLA
    optimizer_iterations = 500
    qaoa_iterations = 3
    qubo_penalty = None

    circuit = tsp.generate_openqasm(optimizer, optimizer_iterations, qaoa_iterations, qubo_penalty)
    info = f"seed={seed}, opt={optimizer.__name__}, " \
           f"opt_iter={optimizer_iterations}, qaoa_iter={qaoa_iterations}, qubo_penalty={qubo_penalty}"

    print(f"ideal simulation (IBM), {info}")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "ibm", title=f"ideal simulation (IBM), seed={seed}")
    print(f"ideal simulation (IonQ), {info}")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "ionq", title=f"ideal simulation (IonQ), seed={seed}")


def evaluate_tsp_noisy(tsp: TspCircuitGenerator, tsp_solution: set[str], seed: int):
    # another optimizer, better for noisy simulations, not used
    optimizer = SPSA
    optimizer_iterations = 500
    qaoa_iterations = 2
    qubo_penalty = 250
    optimizer_learning_rate = 0.3
    optimizer_perturbation = 0.05

    # same optimizer as for ideal simulation, used for comparability
    optimizer = COBYLA
    optimizer_iterations = 500
    qaoa_iterations = 3
    qubo_penalty = None
    optimizer_learning_rate = None
    optimizer_perturbation = None

    circuit = tsp.generate_openqasm(optimizer, optimizer_iterations, qaoa_iterations, qubo_penalty,
                                    optimizer_learning_rate, optimizer_perturbation)
    info = f"seed={seed}, opt={optimizer.__name__}, " \
           f"opt_iter={optimizer_iterations}, qaoa_iter={qaoa_iterations}, qubo_penalty={qubo_penalty}"
    if optimizer == SPSA:
        info += f", learning_rate={optimizer_learning_rate}, perturbation={optimizer_perturbation}"

    print(f"IBM Montreal, {info}")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "ibm", "montreal",
                        title=f"IBM Montreal, seed={seed}")
    print(f"IBM Washington, {info}")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "ibm", "washington",
                        title=f"IBM Washington, seed={seed}")
    print(f"IonQ Aria 1, {info}")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "ionq", "aria-1",
                        title=f"IonQ Aria 1, seed={seed}")
    print(f"IQM Apollo, {info}")
    evaluate_single_tsp(circuit, tsp, tsp_solution, "iqm", "apollo",
                        title=f"IQM Apollo, seed={seed}")


def evaluate_single_tsp(circuit: str, tsp: TspCircuitGenerator, tsp_solution: set[str],
                        vendor: str, noisy_backend: str | None = None, filtering=False,
                        title: str = ""):
    counts = ApiClient.simulate_circuit(circuit, vendor, noisy_backend=noisy_backend)["counts"]
    if filtering:
        counts = filter_counts(tsp.check_for_valid_tour, counts)
    show_histogram(counts, title)

    right_counts, all_counts, percentage = evaluate_counts(counts, tsp_solution)
    print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")


if __name__ == '__main__':
    evaluate_tsp()
