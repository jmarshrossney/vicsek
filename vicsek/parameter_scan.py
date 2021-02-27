import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import itertools

plt.style.use(Path(__file__).resolve().parent / "vicsek.mplstyle")


class ParameterScan:
    def __init__(self, path_to_database):

        self.path_to_database = path_to_database

        print(
            f"Number of parameter combinations associated with this database: {self.size}"
        )

    @property
    def path_to_database(self):
        return self._path_to_database

    @path_to_database.setter
    def path_to_database(self, new_path):
        new_path = Path(new_path)
        if new_path.is_file():  # file provided, already exists
            pass
        elif new_path.is_dir():  # directory provided, already exists
            new_path = new_path / "database.csv"
        else:
            if new_path.suffix == "":  # directory provided, doesn't yet exist
                new_path.mkdir(parents=True)
                new_path = new_path / "database.csv"
            elif new_path.suffix == ".csv":  # file provided, doesn't yet exist
                if not new_path.parent.exists():
                    new_path.parent.mkdir(parents=True)
            else:
                raise ValueError("Please provide a directory or .csv file")

        self._path_to_database = new_path

    @property
    def size(self):
        """Returns the number of combinations of parameters that have been measured
        so far."""
        try:
            df = pd.load_csv(self.path_to_database)
            return df.shape[0]
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return 0

    def scan(self):
        pass
