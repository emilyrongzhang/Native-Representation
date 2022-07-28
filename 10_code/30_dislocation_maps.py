import geopandas as gpd
import numpy as np
import pandas as pd
import partisan_dislocation as pdn
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
# Plot states
#
###########

short_level = {"upper": "u", "lower": "l"}
projection = "ESRI:102010"


def plot_points(state_fips, level, year, color, sample_pct, legend=True):

    # state_fips = "02"
    # level = "upper"
    # year = 2010
    # color = "RdBu"
    # legend = True

    # Get points
    points = gpd.read_file(
        f"/Users/emilyzhang/Documents/GitHub/native_american_dislocation/20_intermediate_data/30_dislocation/"
        f"dislocation_{state_fips}_{year}_{level}_{sample_pct * 100:.0f}pct.geojson"
    )
    points = points.to_crs(projection)
    extrem = np.abs(points.partisan_dislocation).max()

    # Get districts
    districts = gpd.read_file(
        f"/Users/emilyzhang/Documents/GitHub/native_american_dislocation/00_source_data/state_legislative_districts/"
        f"{states[state_fips]}/{level}/"
        f"tl_2019_{state_fips}_sld{short_level[level]}.shp"
    )
    districts = districts.to_crs(projection)

    ai = points[points.ai == 1].copy()
    non_ai = points[points.ai == 0].copy()

    ax = non_ai.plot(color="grey", markersize=1, alpha=0.2, figsize=(12, 12))

    ai.plot(
        "partisan_dislocation",
        ax=ax,
        cmap=color,
        legend=legend,
        figsize=(9, 9),
        vmin=-extrem,
        vmax=extrem,
        markersize=0.3,
        alpha=0.5,
    )
    ax.set_title(
        states[state_fips] + "\n" + level.upper() + " Legislative" "\n " + str(year)
    )

    dist_scores = points.groupby("NAMELSAD", as_index=False)[
        ["partisan_dislocation", "knn_shr_ai", "district_ai_share"]
    ].mean()

    dist = pd.merge(
        districts,
        dist_scores,
        on="NAMELSAD",
        how="outer",
        validate="1:1",
        indicator=True,
    )
    dist._merge.value_counts()

    dist.boundary.plot(ax=ax, edgecolor="black", linewidth=0.5)

    def add_district_label(x):
        coords = x.geometry.centroid.coords[0]
        ax.annotate(
            # text=f"District {x['short_name']}",
            text=f'{x["short_name"]}, {x["district_ai_share"]:.0%} AI, {x["partisan_dislocation"]:.3f} Avg Dilut',
            xy=coords,
            ha="center",
            fontsize=4,
        )

    dist["short_name"] = dist["NAMELSAD"].str.replace(
        "State (Senate|House) District", "Dist", regex=True
    )
    dist.apply(add_district_label, axis=1)

    # ax.text(
    #     s='Red is "diluted", green is "packed"',
    #     horizontalalignment="center",
    #     verticalalignment="center",
    # )

    # ax.set_xlim([-1_100_000, -675_000])
    # ax.set_ylim([4_150_000, 4_550_000])
    ax.set_axis_off()

    ax.figure.savefig(
        f"/Users/emilyzhang/Documents/GitHub/native_american_dislocation/30_results/10_dislocation_maps/"
        f"ai_points_{state_fips}_{year}_{level}_{sample_pct * 100:.0f}pct.pdf"
    )
    print(ax)


# Run the func above in parallel across states.

# loops = [
#     {"state_fips": s, "level": level, "year": year}
#     for s in ["02", "04"]
#     for level in ["upper", "lower"]
#     for year in [2010]
# ]

for state in states.keys():
    for level in ["upper", "lower"]:
        for year in [2010]:
            plot_points(
                state_fips=state,
                level=level,
                year=year,
                color="Wistia",
                sample_pct=samples[state],
            )
