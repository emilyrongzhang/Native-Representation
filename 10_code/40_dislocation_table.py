from ast import literal_eval
import numpy as np
import pandas as pd
import re
import yaml

# Load states we want.
# This imports the yaml file in the code folder.
# We use the list of states and their fips codes a lot, so
# just saving in one place.
# This loads

with open("config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
states = cfg["states"]
samples = cfg["samples"]

###########
#
# Summary Tables
#
###########

gathered = list()

for state in states.keys():
    for level in ["upper", "lower"]:
        for year in [2010]:

            # # Debug
            # state = "04"
            # level = "upper"
            # year = 2010

            # Get points
            points = pd.read_csv(
                f"../20_intermediate_data/30_dislocation/"
                f"dislocation_{state}_{year}_{level}_{samples[state] * 100:.0f}pct.csv"
            )

            collapsed = (
                points[points.ai == 1]
                .groupby("NAMELSAD", as_index=False)[
                    ["district_ai_share", "partisan_dislocation"]
                ]
                .mean()
            )
            collapsed["state_fips"] = state
            collapsed["level"] = level
            collapsed["year"] = year
            collapsed["state"] = states[state]
            collapsed["sample"] = samples[state]
            gathered.append(collapsed)

df = pd.concat(gathered)
df.to_csv("../20_intermediate_data/40_district_summary_table.csv")
