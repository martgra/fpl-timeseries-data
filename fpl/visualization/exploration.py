"""Preprocessing for exploring purposes."""
from IPython.display import display


def reorder_elements(data_frame):
    """Reorder elements dataframe for readability.

    Args:
        data_frame ([type]): [description]

    Returns:
        pd.DataFrame: Elements get team and web_name first.
    """
    try:
        _elements_columns = sorted(data_frame.columns.tolist())
        _elements_columns.insert(0, _elements_columns.pop(_elements_columns.index("team")))
        _elements_columns.insert(0, _elements_columns.pop(_elements_columns.index("web_name")))
        return data_frame[_elements_columns]
    except:
        print("Not able to shuffle elements table, check if data_frame holds elements")


def compare_elements(snapshot_list, element_id, element_value):
    """Display row(s) from successive snapshots.

    Args:
        snapshot_list (list): List holding pandas.DataFrame
        element_id (str): Element(s) to select
    """
    _df_temp = snapshot_list[0].loc[snapshot_list[0][element_id] == element_value]
    for i in snapshot_list:
        _df_temp = _df_temp.append(i.loc[i[element_id] == element_value], ignore_index=True)
    display(_df_temp)
    return _df_temp
