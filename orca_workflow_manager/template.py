from pathlib import Path

from jinja2 import Environment, FileSystemLoader

template_dir = Path(__file__).parent / "templates"
template_env = Environment(loader=FileSystemLoader(template_dir))


def render_orca_input(template_file, nproc, charge, multiplicity, xyzfile):
    if int(charge) != charge:
        raise ValueError("Charge must be an integer")

    if int(multiplicity) != multiplicity:
        raise ValueError("Multiplicity must be an integer")

    template = template_env.get_template(template_file)
    return template.render(
        nproc=nproc,
        charge=int(charge),
        multiplicity=int(multiplicity),
        xyzfile=xyzfile,
    )


def render_slurm_script(
    template_file,
    job_name,
    partition="g1",
    n_tasks=4,
    db=None,
    extra_commands=None,
):
    if extra_commands is None:
        extra_commands = []
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    return template.render(
        job_name=job_name,
        partition=partition,
        n_tasks=n_tasks,
        extra_commands=extra_commands,
        db=db,
    )
