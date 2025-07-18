from typing import Callable

from matplotlib import pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit_algorithms.optimizers import COBYLA, SPSA

from api_client import ApiClient
from generation import TspCircuitGenerator


def show_histogram(counts: dict[str, int], title: str = "", highlight_x: set[str] | None = None):
    plot_histogram(counts)

    axis = plt.gca()
    axis.set_ylabel("")

    if highlight_x is not None:
        highlight_x_not = {"".join("1" if bit == "0" else "0" for bit in bitstring) for bitstring in highlight_x}

        for bar, x in zip(axis.patches, counts.keys()):
            if x in highlight_x:
                bar.set_facecolor("green")
            elif x in highlight_x_not:
                bar.set_facecolor("darkred")

    if title:
        plt.subplots_adjust(top=0.93, right=0.98, left=0.07, bottom=0.12)
        plt.title(title, fontsize=12)
    else:
        plt.subplots_adjust(top=0.98, right=0.98, left=0.07, bottom=0.12)

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


def evaluate_tsp(number_of_cities: int, seed: int | None = None, devices: list[str] | None = None):
    tsp = TspCircuitGenerator(number_of_cities, seed)
    tsp_solution = tsp.solution_to_bitstrings(tsp.solve_by_brute_force())
    print(f"optimal solution: {tsp_solution}")

    evaluate_tsp_ideal(tsp, tsp_solution, seed, devices)
    evaluate_tsp_noisy(tsp, tsp_solution, seed, devices)


def evaluate_tsp_ideal(tsp: TspCircuitGenerator, tsp_solution: set[str], seed: int, devices: list[str] | None = None):
    if devices is not None and not set(devices).intersection(["ideal_ibm", "ideal_ionq"]):
        print("skipping ideal simulation")
        return

    optimizer = COBYLA
    optimizer_iterations = 500
    qaoa_iterations = 3
    qubo_penalty = None

    circuit = tsp.generate_openqasm(optimizer, optimizer_iterations, qaoa_iterations, qubo_penalty)
    info = f"seed={seed}, opt={optimizer.__name__}, " \
           f"opt_iter={optimizer_iterations}, qaoa_iter={qaoa_iterations}, qubo_penalty={qubo_penalty}"

    if devices is None or "ideal_ibm" in devices:
        print(f"ideal simulation (IBM), {info}")
        evaluate_single_tsp(circuit, tsp, tsp_solution, "ibm", title=f"ideal simulation (IBM), seed={seed}")
    if devices is None or "ideal_ionq" in devices:
        print(f"ideal simulation (IonQ), {info}")
        evaluate_single_tsp(circuit, tsp, tsp_solution, "ionq", title=f"ideal simulation (IonQ), seed={seed}")


def evaluate_tsp_noisy(tsp: TspCircuitGenerator, tsp_solution: set[str], seed: int, devices: list[str] | None = None):
    if devices is not None and not set(devices).intersection(
            ["ibm_montreal", "ibm_washington", "ionq_aria1", "ionq_harmony", "iqm_apollo"]):
        print("skipping noisy simulation")
        return

    # another optimizer, better for noisy simulations, not used
    # optimizer = SPSA
    # optimizer_iterations = 500
    # qaoa_iterations = 2
    # qubo_penalty = 250
    # optimizer_learning_rate = 0.3
    # optimizer_perturbation = 0.05

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

    if devices is None or "ibm_montreal" in devices:
        print(f"IBM Montreal, {info}")
        evaluate_single_tsp(circuit, tsp, tsp_solution, "ibm", "montreal",
                            title=f"IBM Montreal, seed={seed}")
    if devices is None or "ibm_washington" in devices:
        print(f"IBM Washington, {info}")
        evaluate_single_tsp(circuit, tsp, tsp_solution, "ibm", "washington",
                            title=f"IBM Washington, seed={seed}")
    if devices is None or "ionq_aria1" in devices:
        print(f"IonQ Aria 1, {info}")
        evaluate_single_tsp(circuit, tsp, tsp_solution, "ionq", "aria-1",
                            title=f"IonQ Aria 1, seed={seed}")
    if "ionq_harmony" in devices:  # skipped by default
        print(f"IonQ Harmony, {info}")
        evaluate_single_tsp(circuit, tsp, tsp_solution, "ionq", "harmony",
                            title=f"IonQ Harmony, seed={seed}")
    if devices is None or "iqm_apollo" in devices:
        print(f"IQM Apollo, {info}")
        evaluate_single_tsp(circuit, tsp, tsp_solution, "iqm", "apollo",
                            title=f"IQM Apollo, seed={seed}")


def evaluate_single_tsp(circuit: str, tsp: TspCircuitGenerator, tsp_solution: set[str],
                        vendor: str, noisy_backend: str | None = None, filtering=False,
                        title: str = ""):
    counts = ApiClient.simulate_circuit(circuit, vendor, noisy_backend=noisy_backend)["counts"]
    if filtering:
        counts = filter_counts(tsp.check_for_valid_tour, counts)
    show_histogram(counts, title, tsp_solution)

    right_counts, all_counts, percentage = evaluate_counts(counts, tsp_solution)
    print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")


if __name__ == '__main__':
    for seed in [123, 456, 789]:
        evaluate_tsp(2, seed)
