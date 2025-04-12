#!/usr/bin/env python

from pathlib import Path
import pandas as pd
from jinja2 import Environment, FileSystemLoader


def calculate_points(row, w_column_name, ot_column_name):
    if row[w_column_name] == "W":
        return 2 / 2
    elif row[w_column_name] == "L" and row[ot_column_name] == "OT":
        return 1 / 2
    return 0 / 2


def calculate_rolling_average(csv_file):
    df = pd.read_csv(csv_file)

    w_column_name = df.columns[df.columns.get_loc("GA") + 1]
    ot_column_name = df.columns[df.columns.get_loc(w_column_name) + 1]

    df_played = df.loc[df[w_column_name].notnull()].copy()
    df_played["P"] = df_played.apply(
        calculate_points, args=(w_column_name, ot_column_name), axis=1
    )
    df_played["10G PPct"] = df_played["P"].rolling(window=10).mean()
    return df_played


all_years = pd.DataFrame()
for csv in sorted(Path(".").glob("*.csv")):
    df_played = calculate_rolling_average(csv)
    df_played = df_played.set_index("GP")
    all_years[csv.name.split()[0]] = df_played["10G PPct"]

environment = Environment(loader=FileSystemLoader("templates/"))
template = environment.get_template("line-stack.html.j2")

content = template.render(
    title="Sabres 10G Rolling Points Percentage", dataframe=all_years, dark_mode=True
)
with open("docs/sabres-10g-rolling-points-pct.html", "w", encoding="utf-8") as f:
    f.write(content)
