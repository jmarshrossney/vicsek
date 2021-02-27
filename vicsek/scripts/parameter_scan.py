import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm.autonotebook import tqdm
from pathlib import Path

def parameter_scan(
    model,
    parameter,
    start,
    stop,
    num,
    repeats,
    steps,
    outpath=None,
):
    pbar = tqdm(total=(num * repeats), desc="Simulations completed")

    for value in np.linspace(start, stop, num):

        # Update model with new value for parameter
        setattr(model, parameter, value)


        for rep in repeats:

            # Thermalise
            model.evolve(steps=steps)

            # Record order parameter
            model.order_parameter

            # Randomise positions and headings
            model.init_state()

            pbar.update()




    
