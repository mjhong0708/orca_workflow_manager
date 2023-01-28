from pathlib import Path

import ase.db
import ase.io
import click

from orca_workflow_manager.orca_utils import parse_orca_job


def get_row_id(d=None):
    if d is None:
        d = Path.cwd()
    return int(d.stem)


class Status:
    CREATED = "Created"
    RUNNING = "Running"
    FINISHED = "Finished"
    FAILED = "Failed"


class DBManager:
    def __init__(self, db_path):
        self.db = ase.db.connect(db_path)

    def update(self, row_id, atoms=None, status="FAILED", **kwargs):
        self.db.update(row_id, atoms, status=status, **kwargs)


@click.command()
@click.option("--db", default="mydata.db", help="Database file")
@click.option("-t", "--job-type", default="orca", help="Type of slurm job")
def save_db(db, job_type):
    if job_type == "orca":
        save_orca_job_to_db(db)
    else:
        e = f"Unknown job type: {job_type}"
        raise ValueError(e)


@click.command()
@click.option("--db", default="mydata.db", help="Database file")
@click.option("-s", "--status", default="FAILED")
def update_db_status(db, status):
    db_manager = DBManager(db)
    row_id = get_row_id()
    row = db_manager.db.get(id=row_id)
    db_manager.db.update(row.id, status=status)


def save_orca_job_to_db(db):
    db_manager = DBManager(db)
    pwd = Path.cwd()
    row_id = get_row_id()

    atoms, data = parse_orca_job(pwd)
    if atoms is None:
        status = Status.FAILED
    else:
        status = Status.FINISHED

    db_manager.update(row_id, atoms, status=status, data=data)
