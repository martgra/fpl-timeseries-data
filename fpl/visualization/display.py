"""Module to hold reusable functions for visualization purposes."""

import pandas as pd


def make_race_bar_data(
    data: pd.DataFrame, index="web_name", columns="download_time", values="diff"
):
    """Return dataframe pivoted for florish race bar chart.

    Args:
        data (pd.DataFrame): DataFrame holding time series for race bar chart
        index (str): Index used for naming the bars. Defaults to "web_name".
        columns (str): Should be the temporal value. Usually "download_time".
            Defaults to "download_time".
        values (str): Name of column holding the value. Defaults to "diff".

    Returns:
        pandas.DataFrame: Transformed data.
    """
    if isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
    data = pd.pivot_table(data, index=index, columns=columns, values=values)
    stripped_values = list([i[:16] for i in data.columns])
    data.columns = stripped_values
    return data
