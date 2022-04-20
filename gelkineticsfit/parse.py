# Functions to parse fraction folded data

from pathlib import Path
import pandas as pd


def parse_raw_kinetics_xlsx(file_path: Path, time_range: list=[0, 10800]) -> dict:
    """
    Parse a .xlsx file containing raw kinetic data from BAM folding reactions in the format used
    in the source_data for the BAM-Fab paper. Sheet specifies the overall condition (e.g. BAM-WT + DAR-B)
    Top row header specifies file name for folding reaction, Second row header first column is time, 
    subsequent columns are Unfolded, Folded, fraction folded for each repeat then Summary statitistics
    (average, range, etc.). Removes the Unfolded, Folded and summary statistics rows. 
    Returns a dictionary of form:
    
    data_dict = {
        "condition" : {
            "reaction" : DataFrame
        }
    }

    Where the "condition" is the name of the sheet, "reaction the name of that particular
    folding reaction as specified in the top row of the sheet and DataFrame has two columns:
    column 1 is the time and column 2 is the fraction folded.
    """

    raw_dict = pd.read_excel(file_path, sheet_name=None, header =[0,1])

    data_dict = {}
    for condition, raw_df in raw_dict.items():    
        # get the time column from the first column in the sheet
        time_col = raw_df.droplevel(level=0, axis="columns").iloc[:, 0]

        data_dict[condition] = {}
        for reaction, reaction_data in raw_dict[condition].groupby(level=0, axis="columns"):
            df = reaction_data.copy(deep=True)
            df = df.droplevel(level=0, axis="columns")
            # Only select the Fraction folded columns
            df = df.loc[:, df.columns.str.match('^Fraction folded')]
            if df.empty: # remove any empty columns that have been created
                continue
            else:
                df.insert(loc=0, column="Time (s)", value=time_col) # add time column
                # exclude values outside time range
                df = df[df["Time (s)"].between(time_range[0], time_range[1])]
            
            data_dict[condition][reaction] = df
    
    return data_dict