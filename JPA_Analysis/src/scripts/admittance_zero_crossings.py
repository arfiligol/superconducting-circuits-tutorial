from __future__ import annotations

from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
from IPython.display import display

from src.utils import RAW_LAYOUT_ADMITTANCE_DIR


def zero_crosses(
    group: pd.DataFrame,
    freq_col: str,
    imag_col: str,
    label_col: str,
) -> pd.DataFrame:
    y = group[imag_col]
    sign = pd.Series(np.sign(y), index=y.index)
    next_sign = sign.shift(-1)
    crossing_rows = group[(sign == 0) | (sign * next_sign < 0)].copy()
    if crossing_rows.empty:
        return crossing_rows

    idx = crossing_rows.index
    freqs: list[float] = []
    for i in idx:
        pos = cast(int, group.index.get_loc(i))
        if sign.loc[i] == 0 or pos == len(group) - 1:
            freqs.append(float(cast(float, group.loc[i, freq_col])))
            continue
        f1 = float(cast(float, group.iloc[pos][freq_col]))
        f2 = float(cast(float, group.iloc[pos + 1][freq_col]))
        y1 = float(cast(float, y.iloc[pos]))
        y2 = float(cast(float, y.iloc[pos + 1]))
        freqs.append(f1 - y1 * (f2 - f1) / (y2 - y1))
    crossing_rows[freq_col] = freqs
    return crossing_rows[[label_col, freq_col, imag_col]]


def main() -> None:
    data_file: Path = RAW_LAYOUT_ADMITTANCE_DIR / "LJPAL658_v2_Admittance_Imaginary_Part.csv"
    df = pd.read_csv(data_file)
    display(df.head(0))

    label_col = "L_jun [nH]"
    freq_col = "Freq [GHz]"
    imag_col = "im(Yt(Rectangle1_T1,Rectangle1_T1)) []"

    labels = df[label_col].unique()

    zero_df = (
        df.sort_values(freq_col)
        .groupby(label_col, group_keys=False)
        .apply(zero_crosses, freq_col=freq_col, imag_col=imag_col, label_col=label_col)
    )

    display(labels)
    display(zero_df)


if __name__ == "__main__":
    main()
