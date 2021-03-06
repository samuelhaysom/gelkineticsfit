from pathlib import Path
import numpy as np
import pandas as pd

def opd_fits_to_sheet(fitting_dict: dict) -> pd.DataFrame:
    """Takes a fitting_dict generated by calcs.get_fit_params_dict2() and 
    generates a pd.DataFrame containing the results that can be exported to
    .csv or .xlsx
    Returns:
    fitting_df :

    """

    # Make an output df to put the data into
    