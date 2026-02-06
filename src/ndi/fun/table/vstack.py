import pandas as pd

def vstack(tables):
    """
    Vertically stack tables (DataFrames), aligning columns.

    Args:
        tables (list of pd.DataFrame): List of tables to stack.

    Returns:
        pd.DataFrame: Stacked table.
    """
    if not tables:
        return pd.DataFrame()

    return pd.concat(tables, ignore_index=True)
