import os
import urllib
import zipfile
from datetime import datetime

import pandas as pd
import wget
from tqdm import tqdm

BASE_DIR = "src/data"
BASE_URL = "https://data.binance.vision/data/futures/um/daily"
FIRST_LINE = "open_time,open,high,low,close,volume,close_time,quote_volume,\
count,taker_buy_volume,taker_buy_quote_volume,ignore"


def get_missing_dates(start_date: str) -> list[str]:
    today = datetime.today().strftime("%Y-%m-%d")
    miss_dates = pd.date_range(
        start=start_date, end=today, inclusive="left"
    ).to_list()
    miss_dates = [date.strftime("%Y-%m-%d") for date in miss_dates]
    return miss_dates


def collect_orderbook(
    save_dir: str,
    mode: str = "klines",
    symbol: str = "BTCUSDT",
    timing: str = "1m",
    start_date="2020-01-01",
) -> None:
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    if not os.path.exists(f"{save_dir}/{symbol}-{timing}.csv"):
        collect_df = pd.DataFrame(
            columns=[column for column in FIRST_LINE.split(",")]
        )
    else:
        collect_df = pd.read_csv(f"{save_dir}/{symbol}-{timing}.csv")
        start_date = collect_df.iloc[-1]["date"]
    missing_dates = get_missing_dates(start_date)
    for date in tqdm(missing_dates):
        download_url = (
            f"{BASE_URL}/{mode}/{symbol}/{timing}/{symbol}-{timing}-{date}.zip"
        )
        locale_name = f"{save_dir}/{symbol}-{timing}-{date}"
        try:
            wget.download(url=download_url, out=save_dir)
        except urllib.error.HTTPError:
            collect_df.to_csv(f"{save_dir}/{symbol}-{timing}.csv")
            break

        with zipfile.ZipFile(f"{locale_name}.zip", "r") as zip_ref:
            zip_ref.extractall(save_dir)

        # check missing headers in .csv
        with open(f"{locale_name}.csv", "r") as file:
            data = file.read()
            if data[:9] != "open_time":
                with open(f"{locale_name}.csv", "w") as modified:
                    modified.write(f"{FIRST_LINE}\n" + data)

        tmp_df = pd.read_csv(f"{locale_name}.csv")

        # format timestamp to YYYY-MM-DD HH:mm
        timestamps = tmp_df["open_time"]
        format_dates = []
        for ts in timestamps:
            ts = float(str(ts)[:10])
            format_dates.append(
                datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
            )
        tmp_df["date"] = format_dates
        collect_df = pd.concat([collect_df, tmp_df], axis=0)

        os.remove(f"{locale_name}.zip")
        os.remove(f"{locale_name}.csv")

    collect_df.to_csv(f"{save_dir}/{symbol}-{timing}.csv")


if __name__ == "__main__":
    collect_orderbook(save_dir=BASE_DIR)
