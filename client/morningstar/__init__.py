from __future__ import absolute_import
import functools
from enum import Enum

import pandas as pd
import requests

from models import KeyRatios, ShortInterest, Quote

MORNING_STAR_API = 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T'
BASE_API_URL = 'https://api-global.morningstar.com/sal-service/v1/stock/newfinancials'
STOCK_ID_URL = 'https://www.morningstar.com/api/v1/search/entities?q={}&limit=1&autocomplete=false'


class QueryType(Enum):
    INCOME_STATEMENT = 'incomeStatement'
    BALANCE_SHEET = 'balanceSheet'
    CASH_FLOW = 'cashFlow'


def get_headers(additional_headers: dict = None) -> dict:
    headers = {
        'apikey': MORNING_STAR_API,
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'cache-control': 'no-cache',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/92.0.4515.107 Safari/537.36'
    }

    if additional_headers:
        headers.update(additional_headers)

    return headers


def get_stock_id(ticker: str) -> str:
    # TODO: refactor
    url = STOCK_ID_URL.format(ticker)
    resp = requests.get(url, headers=get_headers({"x-api-key": "Nrc2ElgzRkaTE43D5vA7mrWj2WpSBR35fvmaqfte"}))
    return resp.json()['results'][0]['id'].split('-')[-1]


def get_query_string(data_type: str, report_type: str) -> str:
    # TODO: refactor and be careful it needs 2 locale otherwise 401.
    return "dataType={}&reportType={}&locale=en&languageId=en&locale=en&clientId=MDC&benchmarkId=category&" \
           "component=sal-components-financials-details&version=3.49.0".format(data_type, report_type)


def get_api_url(ticker: str, query_type: str) -> str:
    stock_id = get_stock_id(ticker)
    return '{}/{}/{}/detail'.format(BASE_API_URL, stock_id, query_type)


def query_morningstar(url: str):
    headers = get_headers()
    return requests.get(url, headers=headers)


def get_entries(level):
    label = level.get('label')
    datum = level.get('datum')

    if label and datum:
        yield label, datum

    if 'subLevel' in level:
        for sub_level in level.get('subLevel'):
            yield from get_entries(sub_level)


def build_dataframe(data) -> pd.DataFrame:
    # TODO: refactor
    columns = data.get('columnDefs')

    index = []
    values = []

    for row in data.get('rows'):
        for label, datum in get_entries(row):
            datum = [v if v != '_PO_' else None for v in datum]
            index.append(label)
            values.append(datum)

    return pd.DataFrame(data=values, index=index, columns=columns, dtype=pd.Float32Dtype)


class MorningstarClient:
    def __init__(self, ticker: str):
        self._ticker = ticker

    @functools.cached_property
    def _stock_id(self):
        return get_stock_id(self._ticker)

    def _fetch(self, ticker: str, query_type: QueryType, quarterly: bool = False,
               restated: bool = False) -> pd.DataFrame:
        url = get_api_url(ticker, query_type.value) + '?' + get_query_string(
            data_type='Q' if quarterly else 'A',
            report_type='R' if restated else 'A',
        )

        resp = query_morningstar(url)
        data = resp.json()

        return build_dataframe(data)

    def income_statement(self, quarterly=False, restated=False):
        return self._fetch(self._ticker, query_type=QueryType.INCOME_STATEMENT, quarterly=quarterly, restated=restated)

    def balance_sheet(self, quarterly=False, restated=False):
        return self._fetch(self._ticker, query_type=QueryType.BALANCE_SHEET, quarterly=quarterly, restated=restated)

    def cash_flow(self, quarterly=False, restated=False):
        return self._fetch(self._ticker, query_type=QueryType.CASH_FLOW, quarterly=quarterly, restated=restated)

    def quote(self) -> Quote:
        """
        https://api-global.morningstar.com/sal-service/v1/stock/realTime/v3/0P000003MH/data?secExchangeList=&random=
        0.1532886868585801&languageId=en&locale=en&clientId=MDC&benchmarkId=category&component=sal-components-quote&version=3.49.0

        :return:
        """

    def key_ratios(self) -> KeyRatios:
        url = f'https://api-global.morningstar.com/sal-service/v1/stock/keyStats/{self._stock_id}?languageId=en&' \
              f'locale=en&clientId=MDC&benchmarkId=category&component=sal-components-quote&version=3.49.0'

        resp = query_morningstar(url)
        data = resp.json()
        results = dict()

        # TODO: refactor into a pythonic way (dict-comprehensions)
        for k, v in data.items():
            if 'freeCashFlow' != k:
                results[k] = v['stockValue']
                results[f'{k}Avg'] = v['indAvg']
            else:
                results[k] = v['cashFlowTTM']

        return KeyRatios.from_dict(results)

    def short_interest(self) -> ShortInterest:
        url = f'https://api-global.morningstar.com/sal-service/v1/stock/shortInterest/{self._stock_id}/data?' \
              f'languageId=en&locale=en&clientId=MDC&benchmarkId=category&component=sal-components-short-interest&' \
              f'version=3.49.0'

        resp = query_morningstar(url)
        data = resp.json()

        return ShortInterest.from_dict(data)


if __name__ == '__main__':
    """
    https://api-global.morningstar.com/sal-service/v1/stock/header/v2/data/0P000003MH/securityInfo?showStarRating=&languageId=en&locale=en&clientId=MDC&benchmarkId=category&component=sal-components-quote&version=3.49.0
    
    https://api-global.morningstar.com/sal-service/v1/stock/keyStats/0P000003MH?languageId=en&locale=en&clientId=MDC&benchmarkId=category&component=sal-components-quote&version=3.49.0
    """

    c = MorningstarClient('MSFT')
    print(c.key_ratios())
    print(c.short_interest())
