from pprint import pprint
import finviz
from provider import get_stock_info_provider, MorningstarProvider
import yfinance as yf

from provider import get_stock_info_provider
from analyzer import get_intrinsic_value_calculator

if __name__ == '__main__':
    # ticker = "JNJ"
    # # ticker = "MSFT"
    # p = get_stock_info_provider(ticker)
    # a = get_intrinsic_value_calculator(ticker, p)
    # # print(a.pv_of_20_year_cashflow)
    # # print(a.intrinsic_value_before_cash_debt)
    # # print(a.less_debt_per_share)
    # # print(a.plus_cash_per_share)
    # # print(a.operating_cash_flow_projected)
    # print(a.final_intrinsic_value_per_share)
    # print(a.discount)

    tickers = [
        "MA",
        "JPM",
        "BAC",
        "AAPL",
        "MSFT",
        "CRM",
        "NOW",
        "PG",
        "PEP",
        "MMM",
        "BA",
        "JNJ",
        "UNH",
        "FB",
        "GOOGL",
        "AMZN",
        "HD",
        "NKE"
    ]

    # for ticker in tickers:
    #     p = get_stock_info_provider(ticker)
    #     a = get_intrinsic_value_calculator(ticker, p)
    #
    #     try:
    #         print("{}: {}".format(ticker, a.final_intrinsic_value_per_share))
    #     except Exception as e:
    #         print("{}: {}".format(ticker, e))

    # ticker = 'NVDA'
    # ticker = 'THO'
    ticker = 'MSFT'
    p = get_stock_info_provider(ticker)
    a = get_intrinsic_value_calculator(ticker, p)
    # print(a.operating_cash_flow_projected)
    print(a.intrinsic_value_before_cash_debt)
    print(a.less_debt_per_share)
    print(a.plus_cash_per_share)
    print(a.final_intrinsic_value_per_share)
    # print(p.beta)
    # print(p.shares_outstanding)
    # print(p.last_close)
    # print(p.operating_cashflow)
    # print(p.total_cash)
    # print(p.total_debt)
    # print(p.eps_next_5_years)
    # print(p.operating_cashflow)

    # import morningstar_stmt as ms
    # from morningstar_stmt import tickerlist as tl
    #
    # ms.download_stmt(tl.all)

    # from client import MorningstarClient
    #
    # c = MorningstarClient('MSFT')
    # cashflow = c.cash_flow()
    # print(cashflow.loc['Cash Generated from Operating Activities'])
    #
    # balancesheet = c.balance_sheet(quarterly=True)
    # print(balancesheet.loc['Cash, Cash Equivalents and Short Term Investments'])
    #
    # print(balancesheet.loc['Current Debt and Capital Lease Obligation'])
    # print(balancesheet.loc['Long Term Debt'])
    #
    # mp = MorningstarProvider('MSFT')
    # print(mp.operating_cashflow)
    # print(mp.total_cash)
    # print(mp.total_debt)

    print('-' * 50)
    print('-' * 50)
    print('-' * 50)

    ticker = 'MSFT'
    p = MorningstarProvider(ticker)
    a = get_intrinsic_value_calculator(ticker, p)
    print(a.intrinsic_value_before_cash_debt)
    print(a.less_debt_per_share)
    print(a.plus_cash_per_share)
    print(a.final_intrinsic_value_per_share)
    # print(p.beta)
    # print(p.shares_outstanding)
    # print(p.last_close)
    # print(p.operating_cashflow)
    # print(p.total_cash)
    # print(p.total_debt)
    # print(p.eps_next_5_years)
