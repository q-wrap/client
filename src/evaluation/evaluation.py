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


def filter_counts(filter_function, counts: dict[str, int]) -> dict[str, int]:
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

    optimizer_ideal = COBYLA
    optimizer_iterations_ideal = 500
    qaoa_iterations_ideal = 3
    qubo_penalty_ideal = None
    openqasm_circuit_ideal = tsp.generate_openqasm(optimizer_ideal, optimizer_iterations_ideal,
                                                   qaoa_iterations_ideal)
    parameter_info_ideal = f"opt={optimizer_ideal.__name__}, opt_iter={optimizer_iterations_ideal}, " \
                           f"qaoa_iter={qaoa_iterations_ideal}, qubo_penalty={qubo_penalty_ideal},\nconstraint=None"

    counts_ibm_ideal = ApiClient.simulate_circuit(openqasm_circuit_ideal, "ibm")["counts"]
    show_histogram(counts_ibm_ideal, parameter_info_ideal + "\nIBM ideal")
    right_counts, all_counts, percentage = evaluate_counts(counts_ibm_ideal, tsp_solution)
    print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")

    # counts_ionq_ideal = ApiClient.simulate_circuit(openqasm_circuit_ideal, "ionq")["counts"]
    # show_histogram(counts_ionq_ideal, parameter_info_ideal + "\nIonQ ideal")
    # right_counts, all_counts, percentage = evaluate_counts(counts_ionq_ideal, tsp_solution)
    # print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")

    # optimizer_noisy = SPSA
    # optimizer_iterations_noisy = 500
    # qaoa_iterations_noisy = 2
    # qubo_penalty_noisy = 150
    # openqasm_circuit_noisy = tsp.generate_openqasm(optimizer_noisy, optimizer_iterations_noisy,
    #                                                qaoa_iterations_noisy)
    # parameter_info_noisy = f"opt={optimizer_noisy.__name__}, opt_iter={optimizer_iterations_noisy}, " \
    #                        f"qaoa_iter={qaoa_iterations_noisy}, qubo_penalty={qubo_penalty_noisy},\nconstraints=None"
    #
    # counts_ibm_montreal = ApiClient.simulate_circuit(openqasm_circuit_noisy, "ibm",
    #                                                  noisy_backend="montreal")["counts"]
    # # counts_ibm_montreal = filter_counts(tsp.check_for_valid_tour, counts_ibm_montreal)
    # show_histogram(counts_ibm_montreal, parameter_info_noisy + "\nIBM Montreal")
    # right_counts, all_counts, percentage = evaluate_counts(counts_ibm_montreal, tsp_solution)
    # print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")

    # counts_ibm_washington = ApiClient.simulate_circuit(openqasm_circuit_noisy, "ibm",
    #                                                    noisy_backend="washington")["counts"]
    # # counts_ibm_washington = filter_counts(tsp.check_for_valid_tour, counts_ibm_washington)
    # show_histogram(counts_ibm_washington, parameter_info_noisy + "\nIBM Washington")
    # right_counts, all_counts, percentage = evaluate_counts(counts_ibm_washington, tsp_solution)
    # print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")
    #
    # counts_ionq_aria = ApiClient.simulate_circuit(openqasm_circuit_noisy, "ionq",
    #                                               noisy_backend="aria-1")["counts"]
    # # counts_ionq_aria = filter_counts(tsp.check_for_valid_tour, counts_ionq_aria)
    # show_histogram(counts_ionq_aria, parameter_info_noisy + "\nIonQ Aria 1")
    # right_counts, all_counts, percentage = evaluate_counts(counts_ionq_aria, tsp_solution)
    # print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")
    #
    # counts_iqm_apollo = ApiClient.simulate_circuit(openqasm_circuit_noisy, "iqm",
    #                                                noisy_backend="apollo")["counts"]
    # # counts_iqm_apollo = filter_counts(tsp.check_for_valid_tour, counts_iqm_apollo)
    # show_histogram(counts_iqm_apollo, parameter_info_noisy + "\nIQM Apollo")
    # right_counts, all_counts, percentage = evaluate_counts(counts_iqm_apollo, tsp_solution)
    # print(f"correct results: {right_counts} out of {all_counts} ({percentage * 100:.2f} %)")


if __name__ == '__main__':
    evaluate_tsp()
