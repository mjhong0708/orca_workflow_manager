from orca_workflow_manager import ORCAWorkflow


def main():
    workflow = ORCAWorkflow(
        "molecules.db", orca_template="orca_pbe_def2-SVP_engrad.inp"
    )
    workflow.run()


if __name__ == "__main__":
    main()
