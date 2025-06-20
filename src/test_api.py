import os
import requests

API_URL = "http://127.0.0.1:5000"
BASE_FOLDER = "../circuits/test"


def _download_circuits(url, files, local_path):
    for file in files:
        if os.path.exists(os.path.join(local_path, os.path.basename(file))):
            continue

        response = requests.get(url + file)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(os.path.join(local_path, file)), exist_ok=True)
            with open(os.path.join(local_path, os.path.basename(file)), 'w+') as f:
                f.write(response.text)
        else:
            print(f"Failed to download {file}")


def download_openqasm2_circuits():
    url = "https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/refs/heads/master/"
    files = [
        "compiler-selection/Shor/shor-fix-15-qasm.qasm",
        "example-implementations/Grover-SAT/grover-fix-a-or-b-and-a-or-not-b.qasm",
        "example-implementations/Grover-SAT/grover-fix-aandb-sat-qasm.qasm",
        "example-implementations/Grover-SAT/grover-general-fix-qasm.qasm",
        # "example-implementations/Random%20Circuits/random1.qasm",
        # "example-implementations/Random%20Circuits/random2.qasm",
    ]
    local_path = os.path.join(BASE_FOLDER, "openqasm2")

    _download_circuits(url, files, local_path)


def download_openqasm3_circuits():
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
    local_path = os.path.join(BASE_FOLDER, "openqasm3")

    _download_circuits(url, files, local_path)


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


def _test_circuits(directory: str, openqasm_version: int = None):
    for file in os.listdir(directory):
        if file.endswith(".qasm"):
            print(f"{file}")
            with open(os.path.join(directory, os.path.basename(file)), 'r') as f:
                openqasm_circuit = f.read()
                print(select_device(openqasm_circuit, openqasm_version))


def test_openqasm2_circuits():
    print("Testing OpenQASM 2 circuits:")
    _test_circuits(os.path.join(BASE_FOLDER, "openqasm2"), 2)


def test_openqasm3_circuits():
    print("Testing OpenQASM 3 circuits:")
    _test_circuits(os.path.join(BASE_FOLDER, "openqasm3"), 3)


if __name__ == '__main__':
    # download_openqasm2_circuits()
    # download_openqasm3_circuits()

    # test_openqasm2_circuits()
    test_openqasm3_circuits()
