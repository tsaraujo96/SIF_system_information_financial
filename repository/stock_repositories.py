import json
from datetime import datetime, timedelta
from tkinter import Entry
from typing import List, Tuple, Dict
from urllib.request import urlopen, Request

import requests
from bs4 import BeautifulSoup as Soup

from domain import NameStockError


class StockRepository:
    @staticmethod
    def get_all_papers(ativo_objeto: Entry) -> str:

        uclient = urlopen(
            Request(
                f"https://query1.finance.yahoo.com/v1/finance/search?q={ativo_objeto.get()}&quotesCount=1",
                headers={"User-Agent": "Mozilla/5.0"},
            )
        )
        page_soup = Soup(uclient.read(), "html.parser")
        uclient.close()
        json_soup = json.loads(page_soup.get_text())

        if not json_soup["quotes"]:
            raise NameStockError()

        paper_in_yahoo = json_soup["quotes"][0]["symbol"]
        return paper_in_yahoo

    def get_json_and_build_fields(self, ativo_objeto: str, list_of_date: List[Tuple[str, str]]) -> List[Dict]:

        list_info = []

        for tuple_date in list_of_date:

            url = (
                f"https://query1.finance.yahoo.com/v8/finance/chart/{ativo_objeto}?&period1={tuple_date[0]}"
                f"&period2={tuple_date[1]}&interval=1m&range=7d&includePrePost=true "
            )
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()

            info_dict = self._data_factory(r)
            list_info.append(info_dict)

        return list_info

    def _data_factory(self, r):

        info_dict = dict(
            date=self._convert_date(r["chart"]["result"][0]["timestamp"]),
            open=r["chart"]["result"][0]["indicators"]["quote"][0]["open"],
            close=r["chart"]["result"][0]["indicators"]["quote"][0]["close"],
            high=r["chart"]["result"][0]["indicators"]["quote"][0]["high"],
            low=r["chart"]["result"][0]["indicators"]["quote"][0]["low"],
            volume=r["chart"]["result"][0]["indicators"]["quote"][0]["volume"],
        )

        return info_dict

    @staticmethod
    def _convert_date(date):
        date = [datetime.utcfromtimestamp(ts) for ts in date]
        date = [d - timedelta(hours=3) for d in date]
        date = [d.strftime("%Y-%m-%d %H:%M:%S") for d in date]
        return date