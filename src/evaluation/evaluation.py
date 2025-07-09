from matplotlib import pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit_algorithms.optimizers import COBYLA, SPSA

from api_client import ApiClient
from generation import TspCircuitGenerator


def show_histogram(counts: dict[str, int], title: str = None):
    plot_histogram(counts)
    if title:
        plt.title(title, fontsize=10)
    plt.show()


def evaluate_counts(counts: dict[str, int], solutions: set[str]) -> tuple[int, int, float]:
    correct_counts = 0

    for bitstring in solutions:
        if bitstring in counts.keys():
            correct_counts += counts[bitstring]

    all_counts = sum(counts.values())
    return correct_counts, all_counts, correct_counts / all_counts


def evaluate_tsp():
    tsp = TspCircuitGenerator(2, 456)
    tsp_solution = tsp.solution_to_bitstrings(tsp.solve_by_brute_force())
    print(f"optimal solution: {tsp_solution}")

    optimizer_ideal = COBYLA
    optimizer_iterations_ideal = 200
    qaoa_iterations_ideal = 20
    qubo_penalty_ideal: float
    openqasm_circuit_ideal = tsp.generate_openqasm(optimizer_ideal, optimizer_iterations_ideal,
                                                   qaoa_iterations_ideal)
    parameter_info_ideal = f"opt={optimizer_ideal.__name__}, opt_iter={optimizer_iterations_ideal}, " \
                           f"qaoa_iter={qaoa_iterations_ideal}, qubo_penalty=None,\nconstraint=start_linear"

    counts_ibm_ideal = ApiClient.simulate_circuit(openqasm_circuit_ideal, "ibm")["counts"]
    show_histogram(counts_ibm_ideal, parameter_info_ideal + "\nIBM ideal")
    right_counts, all_counts, percentage = evaluate_counts(counts_ibm_ideal, tsp_solution)
    print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")

    counts_ionq_ideal = ApiClient.simulate_circuit(openqasm_circuit_ideal, "ionq")["counts"]
    show_histogram(counts_ionq_ideal, parameter_info_ideal + "\nIonQ ideal")
    right_counts, all_counts, percentage = evaluate_counts(counts_ionq_ideal, tsp_solution)
    print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")

    optimizer_noisy = SPSA
    optimizer_iterations_noisy = 1000
    qaoa_iterations_noisy = 30
    qubo_penalty_noisy: float
    openqasm_circuit_noisy = tsp.generate_openqasm(optimizer_noisy, optimizer_iterations_noisy,
                                                   qaoa_iterations_noisy)
    parameter_info_noisy = f"opt={optimizer_noisy.__name__}, opt_iter={optimizer_iterations_noisy}, " \
                           f"qaoa_iter={qaoa_iterations_noisy}, qubo_penalty=None,\nconstraints=start_linear"

    counts_ibm_montreal = ApiClient.simulate_circuit(openqasm_circuit_noisy, "ibm")["counts"]
    show_histogram(counts_ibm_montreal, parameter_info_noisy + "\nIBM Montreal")
    right_counts, all_counts, percentage = evaluate_counts(counts_ibm_montreal, tsp_solution)
    print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")

    counts_ibm_washington = ApiClient.simulate_circuit(openqasm_circuit_noisy, "ibm")["counts"]
    show_histogram(counts_ibm_washington, parameter_info_noisy + "\nIBM Washington")
    right_counts, all_counts, percentage = evaluate_counts(counts_ibm_washington, tsp_solution)
    print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")


if __name__ == '__main__':
    evaluate_tsp()
