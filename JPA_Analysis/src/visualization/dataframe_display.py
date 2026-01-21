from __future__ import annotations

from typing import cast

import pandas as pd


def print_dataframe_table(title: str, df: pd.DataFrame) -> None:
    """
    Render a pandas DataFrame in the CLI with a consistent header/footer.

    Args:
        title: Short description displayed above the table.
        df: DataFrame to print.
    """
    print("\n===== ", title, " =====", sep="")
    if df.empty:
        print("(no rows)")
    else:
        print(cast(str, df.to_string(index=False)))
    print("==============================\n")
