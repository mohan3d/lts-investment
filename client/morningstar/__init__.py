from __future__ import absolute_import

import enum
import functools

import pandas as pd
import requests

from models import KeyRatios, ShortInterest, Quote, Response

MORNING_STAR_API_KEY = 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T'
MORNING_STAR_X_API_KEY = 'Nrc2ElgzRkaTE43D5vA7mrWj2WpSBR35fvmaqfte'
MORNING_STAR_REALTIME_API_KEY = 'eyJlbmMiOiJBMTI4R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.XmuAS3x5r-0MJuwLDdD4jNC6zjsY7HAFNo' \
                                '2VdvGg6jGcj4hZ4NaJgH20ez313H8An9UJrsUj8ERH0R8UyjQu2UGMUnJ5B1ooXFPla0LQEbN_Em3-IG8' \
                                '4YPFcWVmEgcs1Fl2jjlKHVqZp04D21UvtgQ4xyPwQ-QDdTxHqyvSCpcE.ACRnQsNuTh1K_C9R.xpLNZ8C' \
                                'c9faKoOYhss1CD0A4hG4m0M7-LZQ0fISw7NUHwzQs2AEo9ZXfwOvAj1fCbcE96mbKQo8gr7Oq1a2-piYX' \
                                'M1X5yNMcCxEaYyGinpnf6PGqbdr6zbYZdqyJk0KrxWVhKSQchLJaLGJOts4GlpqujSqJObJQcWWbkJQYK' \
                                'G9K7oKsdtMAKsHIVo5-0BCUbjKVnHJNsYwTsI7xn2Om8zGm4A.nBOuiEDssVFHC_N68tDjVA'

BASE_API_URL = 'https://api-global.morningstar.com/sal-service/v1/stock'
STOCK_ID_URL = 'https://www.morningstar.com/api/v1/search/entities?q={}&limit=1&autocomplete=false'


class QueryType(enum.Enum):
    INCOME_STATEMENT = 'incomeStatement'
    BALANCE_SHEET = 'balanceSheet'
    CASH_FLOW = 'cashFlow'

    QUOTE = 'realTime/v3'
    KEY_RATIOS = 'keyStats'
    SHORT_INTEREST = 'shortInterest'


def get_headers(additional_headers: dict = None) -> dict:
    headers = {
        'apikey': MORNING_STAR_API_KEY,
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'cache-control': 'no-cache',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/92.0.4515.107 Safari/537.36',
        'x-api-key': MORNING_STAR_X_API_KEY,
        'x-api-realtime-e': MORNING_STAR_REALTIME_API_KEY,
    }

    if additional_headers:
        headers.update(additional_headers)

    return headers


def get_query_string(data_type: str, report_type: str) -> str:
    # TODO: refactor and be careful it needs 2 locale otherwise 401.
    return "dataType={}&reportType={}&locale=en&languageId=en&locale=en&clientId=MDC&benchmarkId=category&" \
           "component=sal-components-financials-details&version=3.49.0".format(data_type, report_type)


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


def fetch_json(url: str, extra_headers: dict = None) -> dict:
    headers = get_headers(extra_headers)
    resp = requests.get(url, headers=headers)

    return resp.json()


class MorningstarClient:
    def __init__(self, ticker: str):
        self._ticker = ticker

    def income_statement(self, quarterly=False, restated=False) -> pd.DataFrame:
        return self._fetch_dataframe(query_type=QueryType.INCOME_STATEMENT, quarterly=quarterly, restated=restated)

    def balance_sheet(self, quarterly=False, restated=False) -> pd.DataFrame:
        return self._fetch_dataframe(query_type=QueryType.BALANCE_SHEET, quarterly=quarterly, restated=restated)

    def cash_flow(self, quarterly=False, restated=False) -> pd.DataFrame:
        return self._fetch_dataframe(query_type=QueryType.CASH_FLOW, quarterly=quarterly, restated=restated)

    def quote(self) -> Quote:
        data = self._fetch_data(QueryType.QUOTE)

        return Quote.from_dict(data)

    def key_ratios(self) -> KeyRatios:
        data = self._fetch_data(QueryType.KEY_RATIOS)

        # TODO: refactor into a pythonic way (dict-comprehensions)
        results = dict()
        for k, v in data.items():
            if 'freeCashFlow' != k:
                results[k] = v['stockValue']
                results[f'{k}Avg'] = v['indAvg']
            else:
                results[k] = v['cashFlowTTM']

        return KeyRatios.from_dict(results)

    def short_interest(self) -> ShortInterest:
        data = self._fetch_data(QueryType.SHORT_INTEREST)

        return ShortInterest.from_dict(data)

    @functools.cached_property
    def _stock_id(self):
        url = STOCK_ID_URL.format(self._ticker)
        data = fetch_json(url)
        return data['results'][0]['id'].split('-')[-1]

    def _fetch_dataframe(self, query_type: QueryType, quarterly: bool = False, restated: bool = False) -> pd.DataFrame:
        querystring = get_query_string(data_type='Q' if quarterly else 'A', report_type='R' if restated else 'A')
        url = f'{BASE_API_URL}/newfinancials/{self._stock_id}/{query_type.value}/detail?{querystring}'

        data = fetch_json(url)

        return build_dataframe(data)

    def _fetch_data(self, query_type: QueryType) -> dict:
        url = f'{BASE_API_URL}/{query_type.value}/{self._stock_id}'

        # Append /data only if it is quote or short interest request.
        if query_type in (QueryType.QUOTE, QueryType.SHORT_INTEREST):
            url = url + '/data'

        return fetch_json(url)
