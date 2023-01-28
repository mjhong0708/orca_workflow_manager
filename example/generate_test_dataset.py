import ase.build
import ase.db

molecules = [
    ase.build.molecule("H2O"),
    # ase.build.molecule("CH4"),
    # ase.build.molecule("CO2"),
    # ase.build.molecule("NH3"),
    # ase.build.molecule("C2H4"),
    # ase.build.molecule("C2H6"),
    # ase.build.molecule("C2H2"),
    # ase.build.molecule("C6H6"),
] * 20

db = ase.db.connect("molecules.db", append=False)
for mol in molecules:
    db.write(mol, calculated=False, status="Created")
