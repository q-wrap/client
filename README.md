# Client for q-wrap

This repository contains a client for the q-wrap API, allowing to test and evaluate the wrapper behind it.
See the [q-wrap repository](https://github.com/q-wrap/q-wrap) for more information.

## Installation

Install Python 3.13 or newer on your system. You can download it from the
[official Python website](https://www.python.org/downloads/). You can also try earlier versions, but these are not
tested for this application.

Clone this repository, where `<path>` is the URL of this repository and `--depth 1` is optional:

```bash
git clone --depth 1 <path>
```

Before you install the required packages, you should create and activate a virtual environment. However, this is
optional, and you are free to use another package manager like `uv` as well.

```bash
python -m venv venv  # Python 3.13 or newer

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

If you want to get an overview of the packages used by this application, see the `requirements_direct.txt` file,
instead, which only contains directly installed or imported packages without their dependencies.

## Usage

Make sure that your virtual environment is activated if you created one. You can then simply run the evaluation 
script at `src/evaluation/evaluation.py`.

If you want to execute the tests in `tests/test_api.py`, some additional files need to be placed in `circuits/`:

- `circuits/test/`: arbitrary OpenQASM 2 and 3 circuits from GitHub which are automatically downloaded when running
  the test script directly
- `circuits/mqt_bench/`: OpenQASM 2 circuits for benchmarking which need to be downloaded manually
  from the [MQT Bench](https://www.cda.cit.tum.de/mqtbench/), after selecting the 'Quantum Approximation Optimization 
  Algorithm (QAOA)' as benchmark and the abstraction level as specified below
  - `/general/`: circuits with 'Target-independent Level'
  - `/ibm_montreal/`: circuits with 'Target-dependent Mapped Level' for the IBM Montreal quantum computer

## Documentation

The file `docs/generate_tsp_simple.py` contains a simplified version of the TSP circuit generation code which might 
help in understanding the process. The evaluation code uses the class
`src.evaluation.generation.tsp.TspCircuitGenerator`, instead, which mainly adds more parameters.
