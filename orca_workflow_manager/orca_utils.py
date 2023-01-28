from pathlib import Path

import ase
import cclib
import numpy as np
from ase import units
from ase.calculators.singlepoint import SinglePointCalculator


def parse_matrix(s: str):
    lines = (line.strip() for line in s.splitlines())
    try:
        n_rows = int(next(lines))
    except StopIteration as e:
        raise ValueError("Empty file") from e
    except ValueError as e:
        raise ValueError("First line is not an integer") from e

    n_processed_cols = 0
    matrix = []
    while n_processed_cols < n_rows:
        n_cols = len(next(lines).split())
        matrix_fragment = []
        for _ in range(n_rows):
            matrix_elems = next(lines).split()[1:]
            matrix_elems = [float(i) for i in matrix_elems]
            matrix_fragment.append(matrix_elems)
        matrix_fragment = np.array(matrix_fragment)
        matrix.append(matrix_fragment)
        n_processed_cols += n_cols
    matrix = np.hstack(matrix)
    return matrix


def parse_orca_hessian(hess_file: str, symmetrize: bool = True):
    with open(hess_file, "r") as f:
        s = f.readlines()
        s = [i.strip() for i in s]
    start_line = s.index("$hessian")
    s = "\n".join(s[start_line + 1 :])
    hess = parse_matrix(s)
    if symmetrize:
        # check max error and raise error if larger than 1e-3
        max_error = np.max(np.abs(hess - hess.T))
        if max_error > 1e-2:
            raise ValueError(f"Symmetrization error: max error = {max_error}")
        hess = (hess + hess.T) / 2
    return hess


def parse_orca_job(calc_dir):
    out_file = next(Path(calc_dir).glob("*.out"))
    prefix = out_file.stem
    job_output = cclib.io.ccread(str(out_file))
    extra_data = {}
    try:
        energy = job_output.scfenergies[-1]
        forces = -job_output.grads[-1]
        numbers = job_output.atomnos
        positions = job_output.atomcoords[-1]
        atoms = ase.Atoms(numbers=numbers, positions=positions)
        calc = SinglePointCalculator(atoms, energy=energy, forces=forces)
        atoms.calc = calc
    except AttributeError:
        atoms = None

    hess_file = Path(calc_dir) / f"{prefix}.hess"
    if hess_file.exists():
        hess = parse_orca_hessian(hess_file)
        # convert to eV/angstrom**2
        extra_data["hessian"] = hess * units.Ha / units.Bohr**2

    return atoms, extra_data
