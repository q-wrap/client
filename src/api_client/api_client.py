import requests


class ApiClient:
    API_URL = "http://127.0.0.1:5000"

    @classmethod
    def select_device(cls, openqasm_circuit: str, openqasm_version: int | None = None) -> dict:
        request_data = {
            "openqasm_circuit": openqasm_circuit
        }

        if openqasm_version is not None:
            request_data["openqasm_version"] = openqasm_version

        response = requests.post(f"{cls.API_URL}/select", json=request_data)

        if response.status_code != 200:
            raise ValueError(f"Failed to select device: {response.status_code}\n{response.text}")

        return response.json()

    @classmethod
    def simulate_circuit(cls, openqasm_circuit: str, vendor: str, openqasm_version: int | None = None,
                         noisy_backend: str | None = None, compilation: str | None = None) -> dict:
        request_data = {
            "openqasm_circuit": openqasm_circuit,
            "vendor": vendor,
        }

        if openqasm_version is not None:
            request_data["openqasm_version"] = openqasm_version
        if noisy_backend is not None:
            request_data["noisy_backend"] = noisy_backend
        if compilation is not None:
            request_data["compilation"] = compilation

        response = requests.post(f"{cls.API_URL}/simulate", json=request_data)

        if response.status_code != 200:
            raise ValueError(f"Failed to simulate circuit: {response.status_code}\n{response.text}")

        return response.json()
