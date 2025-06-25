import os
from typing import Callable
from unittest import TestCase, skip

import requests

API_URL = "http://127.0.0.1:5000"
TEST_FOLDER = "../circuits/test"
MQT_BENCH_FOLDER = "../circuits/mqt_bench"


class Downloader:
    @staticmethod
    def _download_circuits(url: str, files: list[str], local_path: str):
        for file in files:
            local_file_path = os.path.join(local_path, os.path.basename(file))

            if os.path.exists(local_file_path):  # file already downloaded
                continue

            response = requests.get(url + file)

            if response.status_code == 200:
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                with open(local_file_path, 'w+') as f:
                    f.write(response.text)
            else:
                print(f"Failed to download circuit: {response.status_code} ({file})")

    @classmethod
    def download_openqasm2_circuits(cls):
        url = "https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/refs/heads/master/"
        files = [
            "compiler-selection/Shor/shor-fix-15-qasm.qasm",
            "example-implementations/Grover-SAT/grover-fix-a-or-b-and-a-or-not-b.qasm",
            "example-implementations/Grover-SAT/grover-fix-aandb-sat-qasm.qasm",
            "example-implementations/Grover-SAT/grover-general-fix-qasm.qasm",
            # "example-implementations/Random%20Circuits/random1.qasm",
            # "example-implementations/Random%20Circuits/random2.qasm",
        ]
        local_path = os.path.join(TEST_FOLDER, "openqasm2")

        cls._download_circuits(url, files, local_path)

    @classmethod
    def download_openqasm3_circuits(cls):
        url = "https://raw.githubusercontent.com/openqasm/openqasm/refs/heads/main/examples/"
        files = [
            "adder.qasm",
            "alignment.qasm",
            "arrays.qasm",
            "cphase.qasm",
            # "dd.qasm",
            # "defcal.qasm",
            # "gateteleport.qasm",
            # "inverseqft1.qasm",
            # "inverseqft2.qasm",
            # "ipe.qasm",
            # "msd.qasm",
            # "qec.qasm",
            # "qft.qasm",
            # "qpt.qasm",
            # "rb.qasm",
            # "rus.qasm",
            # "scqec.qasm",
            # "t1.qasm",
            # "teleport.qasm",
            # "varteleport.qasm",
            # "vqe.qasm",
        ]
        local_path = os.path.join(TEST_FOLDER, "openqasm3")

        cls._download_circuits(url, files, local_path)


class ApiClient:
    @staticmethod
    def select_device(openqasm_circuit: str, openqasm_version: int = None) -> dict:
        request_data = {
            "openqasm_circuit": openqasm_circuit
        }

        if openqasm_version is not None:
            request_data["openqasm_version"] = openqasm_version

        response = requests.post(f"{API_URL}/select", json=request_data)

        if response.status_code != 200:
            raise ValueError(f"Failed to select device: {response.status_code}\n{response.text}")

        return response.json()

    @staticmethod
    def simulate_circuit(openqasm_circuit: str, vendor: str, openqasm_version: int = None,
                         noisy_backend: str = None) -> dict:
        request_data = {
            "openqasm_circuit": openqasm_circuit,
            "vendor": vendor,
        }

        if openqasm_version is not None:
            request_data["openqasm_version"] = openqasm_version
        if noisy_backend is not None:
            request_data["noisy_backend"] = noisy_backend

        response = requests.post(f"{API_URL}/simulate", json=request_data)

        if response.status_code != 200:
            raise ValueError(f"Failed to simulate circuit: {response.status_code}\n{response.text}")

        return response.json()


class Utils:
    @classmethod
    def for_all_circuits_in_directory(cls, func: Callable[[str], dict], directory: str):
        for file in os.listdir(directory):
            if file.endswith(".qasm"):
                cls.for_single_circuit(func, directory, file)

    @staticmethod
    def for_single_circuit(func: Callable[[str], dict], directory: str, file: str):
        print(f"{file}")
        with open(os.path.join(directory, file), 'r') as f:
            circuit = f.read()
            print(func(circuit))


class ApiTest(TestCase):
    @skip("Testing simulation only")
    def test_select_2(self):
        Utils.for_all_circuits_in_directory(
            lambda circuit: ApiClient.select_device(circuit, 2),
            os.path.join(TEST_FOLDER, "openqasm2"))

    @skip("Testing simulation only")
    def test_select_3(self):
        Utils.for_all_circuits_in_directory(
            lambda circuit: ApiClient.select_device(circuit, 3),
            os.path.join(TEST_FOLDER, "openqasm3"))

    def test_simulate_ibm(self):
        Utils.for_single_circuit(
            lambda circuit: ApiClient.simulate_circuit(circuit, "ibm", 2),
            os.path.join(MQT_BENCH_FOLDER, "general"), "qaoa_indep_qiskit_3.qasm")

    def test_simulate_ibm_noisy(self):
        Utils.for_single_circuit(
            lambda circuit: ApiClient.simulate_circuit(circuit, "ibm", 2, "montreal"),
            os.path.join(MQT_BENCH_FOLDER, "general"), "qaoa_indep_qiskit_3.qasm")
        Utils.for_single_circuit(
            lambda circuit: ApiClient.simulate_circuit(circuit, "ibm", 2, "washington"),
            os.path.join(MQT_BENCH_FOLDER, "general"), "qaoa_indep_qiskit_3.qasm")

    def test_simulate_ionq(self):
        Utils.for_single_circuit(
            lambda circuit: ApiClient.simulate_circuit(circuit, "ionq", 2),
            os.path.join(MQT_BENCH_FOLDER, "general"), "qaoa_indep_qiskit_3.qasm")

    def test_simulate_ionq_noisy(self):
        Utils.for_single_circuit(
            lambda circuit: ApiClient.simulate_circuit(circuit, "ionq", 2, "aria-1"),
            os.path.join(MQT_BENCH_FOLDER, "general"), "qaoa_indep_qiskit_3.qasm")
        Utils.for_single_circuit(
            lambda circuit: ApiClient.simulate_circuit(circuit, "ionq", 2, "harmony"),
            os.path.join(MQT_BENCH_FOLDER, "general"), "qaoa_indep_qiskit_3.qasm")

    def test_simulate_iqm_noisy(self):
        Utils.for_single_circuit(
            lambda circuit: ApiClient.simulate_circuit(circuit, "iqm", 2, "apollo"),
            os.path.join(MQT_BENCH_FOLDER, "general"), "qaoa_indep_qiskit_3.qasm")


if __name__ == '__main__':
    Downloader.download_openqasm2_circuits()
    Downloader.download_openqasm3_circuits()
