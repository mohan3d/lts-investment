from analyzer import get_intrinsic_value_calculator
from provider import MorningstarProvider
from provider import get_stock_info_provider

if __name__ == '__main__':
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

    ticker = 'MSFT'

    p = get_stock_info_provider(ticker)
    a = get_intrinsic_value_calculator(ticker, p)
    print(a.intrinsic_value_before_cash_debt)
    print(a.less_debt_per_share)
    print(a.plus_cash_per_share)
    print(a.final_intrinsic_value_per_share)

    print(*['-' * 50] * 3, sep='\n')

    ticker = 'MSFT'
    p = MorningstarProvider(ticker)
    a = get_intrinsic_value_calculator(ticker, p)
    print(a.intrinsic_value_before_cash_debt)
    print(a.less_debt_per_share)
    print(a.plus_cash_per_share)
    print(a.final_intrinsic_value_per_share)
