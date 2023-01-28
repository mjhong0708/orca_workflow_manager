import os
import subprocess
from os import PathLike
from pathlib import Path
from typing import Union

import ase.db

from orca_workflow_manager.template import render_orca_input, render_slurm_script

initial_keys = {"calculated": False, "status": "Created"}


class ORCAWorkflow:
    def __init__(
        self,
        db_path: Union[str, PathLike],
        calc_root: Union[str, PathLike] = ".calculations",
        orca_template: str = "orca_pbe_def2-SVP_engrad.inp",
    ):
        """
        Args:
            db_path: Path to the database file or url
            calc_root: Path to the root directory for calculations
        """
        self.db_path = str(Path(db_path).absolute())
        self.calc_root = Path(calc_root)
        self.orca_template = orca_template

        self.db = ase.db.connect(self.db_path)

    def initialize_db(self):
        for row in self.db.select():
            row_id = row.id
            self.db.update(row_id, **initial_keys)

    def run(self, selections=None, n_tasks_per_job=4, node_partition="g3"):
        if selections is None:
            selections = []
        selections.append(("status", "!=", "Finished"))
        pwd = Path.cwd()
        calc_root = Path(self.calc_root)

        for row in self.db.select(selections):
            row_id = row.id
            calc_dir = calc_root / str(row_id)
            atoms = row.toatoms()
            charge = row.get("charge", 0)
            multiplicity = row.get("multiplicity", 1)
            job_name = "job_" + str(row_id)
            orca_input = render_orca_input(
                self.orca_template,
                n_tasks_per_job,
                charge,
                multiplicity,
                "input.xyz",
            )
            slurm_script = render_slurm_script(
                "slurm_orca.sh",
                job_name,
                node_partition,
                n_tasks_per_job,
                db=self.db_path,
            )
            calc_dir.mkdir(parents=True, exist_ok=True)
            atoms.write(calc_dir / "input.xyz")
            with open(calc_dir / "orca.inp", "w") as f:
                f.write(orca_input)

            with open(calc_dir / "slurm_job.sh", "w") as f:
                f.write(slurm_script)

            os.chdir(calc_dir)
            subprocess.check_call(["sbatch", "slurm_job.sh"])
            self.db.update(row.id, status="Running", orca_input=orca_input)
            os.chdir(pwd)
