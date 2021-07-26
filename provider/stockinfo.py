from __future__ import absolute_import

import functools

import finviz
import yfinance

from client import MorningstarClient
from .utils import to_million, from_any_to_million, first_valid_index, last_valid_index, BILLION_TO_MILLION_RATE


class StockInfoProvider:
    def __init__(self, ticker: str):
        self._ticker = ticker

    @property
    def beta(self) -> float:
        raise NotImplementedError

    @property
    def total_shares(self) -> float:
        raise NotImplementedError

    @property
    def eps_next_5_years(self) -> float:
        raise NotImplementedError

    @property
    def previous_close(self) -> float:
        raise NotImplementedError

    @property
    def operating_cashflow(self) -> float:
        raise NotImplementedError

    @property
    def total_cash(self) -> float:
        raise NotImplementedError

    @property
    def total_debt(self) -> float:
        raise NotImplementedError

    @property
    def last_close(self) -> float:
        return self.previous_close

    @property
    def ops_cashflow(self) -> float:
        return self.operating_cashflow

    @property
    def shares_outstanding(self) -> float:
        return self.total_shares

    @property
    def ticker(self) -> str:
        return self._ticker

    @staticmethod
    def _get_or_default(d, k: str, default: float = 0.0, index_selection=first_valid_index) -> float:
        # TODO:
        try:
            v = d.loc[k]
            index = index_selection(v)
            return v.loc[index]
        except:
            return default


class FinvizProvider(StockInfoProvider):
    @functools.cached_property
    def _finviz_info(self):
        return finviz.get_stock(self._ticker)

    @property
    def beta(self) -> float:
        return float(self._finviz_info.get('Beta'))

    @property
    def total_shares(self) -> float:
        return from_any_to_million(self._finviz_info.get('Shs Outstand'))

    @property
    def eps_next_5_years(self) -> float:
        return float(self._finviz_info.get('EPS next 5Y')[:-1])

    @property
    def previous_close(self) -> float:
        raise NotImplementedError

    @property
    def operating_cashflow(self) -> float:
        raise NotImplementedError

    @property
    def total_cash(self) -> float:
        raise NotImplementedError

    @property
    def total_debt(self) -> float:
        raise NotImplementedError


class YahooProvider(StockInfoProvider):
    @functools.cached_property
    def _yahoo_finance(self):
        return yfinance.Ticker(self.ticker)

    @property
    def beta(self) -> float:
        raise NotImplementedError

    @property
    def total_shares(self) -> float:
        raise NotImplementedError

    @property
    def eps_next_5_years(self) -> float:
        raise NotImplementedError

    @property
    def previous_close(self) -> float:
        return self._yahoo_finance.info.get('previousClose')

    @property
    def operating_cashflow(self) -> float:
        return to_million(self._yahoo_finance.info.get('operatingCashflow'))

    @property
    def total_cash(self) -> float:
        return to_million(self._yahoo_finance.info.get('totalCash'))

    @property
    def total_debt(self) -> float:
        balancesheet = self._yahoo_finance.quarterly_balancesheet
        debt = \
            self._get_or_default(balancesheet, 'Long Term Debt', index_selection=first_valid_index) + \
            self._get_or_default(balancesheet, 'Short Long Term Debt', index_selection=first_valid_index)

        return to_million(debt)


class MorningstarProvider(StockInfoProvider):
    def __init__(self, ticker: str):
        super().__init__(ticker)
        self._client = MorningstarClient(ticker)

    @functools.cached_property
    def _raw_cashflow(self):
        return self._client.cash_flow()

    @functools.cached_property
    def _raw_quarterly_balancesheet(self):
        return self._client.balance_sheet(quarterly=True)

    @functools.cached_property
    def _raw_quote(self):
        return self._client.quote()

    @functools.cached_property
    def _raw_short_interest(self):
        return self._client.short_interest()

    @functools.cached_property
    def _raw_key_ratios(self):
        return self._client.key_ratios()

    @property
    def beta(self) -> float:
        return self._raw_quote.beta

    @property
    def total_shares(self) -> float:
        return self._raw_short_interest.sharesOutstanding

    @property
    def eps_next_5_years(self) -> float:
        # Morning Star provides next 3 years, will be used instead.
        return self._raw_key_ratios.revenue3YearGrowth

    @property
    def previous_close(self) -> float:
        return self._raw_quote.lastPrice

    @property
    def operating_cashflow(self) -> float:
        key = 'Cash Generated from Operating Activities'

        return BILLION_TO_MILLION_RATE * self._get_or_default(self._raw_cashflow, key, index_selection=last_valid_index)

    @property
    def total_cash(self) -> float:
        key = 'Cash, Cash Equivalents and Short Term Investments'
        cash = self._get_or_default(self._raw_quarterly_balancesheet, key, index_selection=last_valid_index)

        return BILLION_TO_MILLION_RATE * cash

    @property
    def total_debt(self) -> float:
        balancesheet = self._raw_quarterly_balancesheet
        current_debt_key = 'Current Debt and Capital Lease Obligation'
        long_term_debt_key = 'Long Term Debt'

        debt = self._get_or_default(balancesheet, current_debt_key, index_selection=last_valid_index) + \
               self._get_or_default(balancesheet, long_term_debt_key, index_selection=last_valid_index)

        return BILLION_TO_MILLION_RATE * debt


class HybridProvider(StockInfoProvider):
    def __init__(self, ticker: str, finviz_provider: FinvizProvider, yahoo_provider: YahooProvider):
        super().__init__(ticker)
        self._yahoo = yahoo_provider
        self._finviz = finviz_provider

    @property
    def beta(self) -> float:
        return self._finviz.beta

    @property
    def previous_close(self) -> float:
        return self._yahoo.previous_close

    @property
    def operating_cashflow(self) -> float:
        return self._yahoo.operating_cashflow

    @property
    def total_cash(self) -> float:
        return self._yahoo.total_cash

    @property
    def total_debt(self) -> float:
        return self._yahoo.total_debt

    @property
    def total_shares(self) -> float:
        return self._finviz.total_shares

    @property
    def eps_next_5_years(self) -> float:
        return self._finviz.eps_next_5_years


def get_stock_info_provider(ticker: str) -> StockInfoProvider:
    return HybridProvider(
        ticker,
        finviz_provider=FinvizProvider(ticker),
        yahoo_provider=YahooProvider(ticker),
    )
