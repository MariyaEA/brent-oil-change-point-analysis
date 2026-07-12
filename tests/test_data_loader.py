from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import DataValidationError, load_brent_prices


def test_load_brent_prices_parses_both_date_formats(tmp_path: Path) -> None:
    path = tmp_path / "prices.csv"
    path.write_text(
        'Date,Price\n20-May-87,18.63\n"Apr 22, 2020",13.77\n',
        encoding="utf-8",
    )

    frame = load_brent_prices(path)

    assert frame["Date"].dt.year.tolist() == [1987, 2020]
    assert frame["Price"].tolist() == [18.63, 13.77]


def test_load_brent_prices_rejects_missing_columns(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    pd.DataFrame({"date": ["2020-01-01"], "value": [1.0]}).to_csv(path, index=False)

    with pytest.raises(DataValidationError, match="Missing required"):
        load_brent_prices(path)


def test_load_brent_prices_gives_clear_missing_file_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Input file not found"):
        load_brent_prices(tmp_path / "missing.csv")


def test_load_brent_prices_rejects_nonpositive_prices(tmp_path: Path) -> None:
    path = tmp_path / "prices.csv"
    pd.DataFrame({"Date": ["01-Jan-20"], "Price": [0]}).to_csv(path, index=False)

    with pytest.raises(DataValidationError, match="strictly positive"):
        load_brent_prices(path)
