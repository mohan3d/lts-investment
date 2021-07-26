from typing import get_type_hints


def get_param(data: dict, name: str, _type: type):
    k = name
    v = data.get(k)

    if v == '_PO_':
        v = None

    if v:
        v = _type(v)

    return v


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

    cls.__str__ = __str__
    return cls


class Response:
    @classmethod
    def from_dict(cls, data: dict):
        params = get_type_hints(cls.__init__)
        args = [get_param(data, k, t) for k, t in params.items()]
        return cls(*args)


@auto_str
class Quote(Response):
    def __init__(
            self,
            lastPrice: float,
            bid: float,
            bidSize: float,
            ask: float,
            askSize: float,
            lotSize: float,
            volume: float,
            recentTradingDayOpenPrice: float,
            dayRangeHigh: float,
            dayRangeLow: float,
            lastClose: float,
            priceOfTradeAfter: float,
            timeOfTradeAfter: str,
            recentTradingDay: str,
            lastUpdateTime: str,
            recentTradingDayJulian: str,
            tradingStatus: str,
            marketCap: float,
            dividendYield: float,
            yearRangeHigh: float,
            yearRangeLow: float,
            avgVolume: float,
            dayChange: float,
            dayChangePer: float,
            currencyCode: str,
            currencySymbol: str,
            listedCurrency: str,
            exchangeID: str,
            exchangeName: str,
            exchangeTimeZone: str,
            type: str,
            ts: str
    ):
        self.lastPrice = lastPrice
        self.bid = bid
        self.bidSize = bidSize
        self.ask = ask
        self.askSize = askSize
        self.lotSize = lotSize
        self.volume = volume
        self.recentTradingDayOpenPrice = recentTradingDayOpenPrice
        self.dayRangeHigh = dayRangeHigh
        self.dayRangeLow = dayRangeLow
        self.lastClose = lastClose
        self.priceOfTradeAfter = priceOfTradeAfter
        self.timeOfTradeAfter = timeOfTradeAfter
        self.recentTradingDay = recentTradingDay
        self.lastUpdateTime = lastUpdateTime
        self.recentTradingDayJulian = recentTradingDayJulian
        self.tradingStatus = tradingStatus
        self.marketCap = marketCap
        self.dividendYield = dividendYield
        self.yearRangeHigh = yearRangeHigh
        self.yearRangeLow = yearRangeLow
        self.avgVolume = avgVolume
        self.dayChange = dayChange
        self.dayChangePer = dayChangePer
        self.currencyCode = currencyCode
        self.currencySymbol = currencySymbol
        self.listedCurrency = listedCurrency
        self.exchangeID = exchangeID
        self.exchangeName = exchangeName
        self.exchangeTimeZone = exchangeTimeZone
        self.type = type
        self.ts = ts


@auto_str
class KeyRatios(Response):
    def __init__(
            self,
            revenue3YearGrowth: float,
            revenue3YearGrowthAvg: float,
            netIncome3YearGrowth: float,
            netIncome3YearGrowthAvg: float,
            operatingMarginTTM: float,
            operatingMarginTTMAvg: float,
            netMarginTTM: float,
            netMarginTTMAvg: float,
            roaTTM: float,
            roaTTMAvg: float,
            roeTTM: float,
            roeTTMAvg: float,
            debitToEquity: float,
            debitToEquityAvg: float,
            freeCashFlow: float

    ):
        self.revenue3YearGrowth = revenue3YearGrowth
        self.revenue3YearGrowthAvg = revenue3YearGrowthAvg
        self.netIncome3YearGrowth = netIncome3YearGrowth
        self.netIncome3YearGrowthAvg = netIncome3YearGrowthAvg
        self.operatingMarginTTM = operatingMarginTTM
        self.operatingMarginTTMAvg = operatingMarginTTMAvg
        self.netMarginTTM = netMarginTTM
        self.netMarginTTMAvg = netMarginTTMAvg
        self.roaTTM = roaTTM
        self.roaTTMAvg = roaTTMAvg
        self.roeTTM = roeTTM
        self.roeTTMAvg = roeTTMAvg
        self.debitToEquity = debitToEquity
        self.debitToEquityAvg = debitToEquityAvg
        self.freeCashFlow = freeCashFlow


@auto_str
class ShortInterest(Response):
    def __init__(
            self,
            sharesOutstanding: float,
            sharesShorted: float,
            sharesShortedDate: str,
            floatSharesShorted: float,
            daysToConver: float,
            sharesShortedChanged: float,
            previousSharesShortedDate: str
    ):
        self.sharesOutstanding = sharesOutstanding
        self.sharesShorted = sharesShorted
        self.sharesShortedDate = sharesShortedDate
        self.floatSharesShorted = floatSharesShorted
        self.daysToConver = daysToConver
        self.sharesShortedChanged = sharesShortedChanged
        self.previousSharesShortedDate = previousSharesShortedDate


"""
{
  "sharesOutstanding": 7531.5746,
  "floatShares": 7527.9151,
  "sharesShorted": 50822833,
  "sharesShortedDate": "2021-06-30T05:00:00.000",
  "floatSharesShorted": 0.6751,
  "daysToConver": 2.1985,
  "sharesShortedChanged": 5.5782,
  "previousSharesShortedDate": "2021-06-15T05:00:00.000"
}
"""
if __name__ == '__main__':
    import typing

    # print(inspect.getfullargspec(QuoteResponse.__init__))
    print(typing.get_type_hints(Quote.__init__))
    print(typing.get_type_hints(Quote.__init__))

    d = {
        "performanceId": "0P000003MH",
        "securityName": "Microsoft Corp",
        "ticker": "MSFT",
        "starRating": "_PO_",
        "qualRating": "_PO_",
        "quantRating": "_PO_",
        "bestRatingType": "Qual",
        "investmentStyle": "3",
        "priceEarnings": "41.874513",
        "priceBook": "16.220001",
        "priceSale": "13.809072",
        "forwardPE": "34.36426116838488",
        "forwardDivYield": "0.0077",
        "starRatingDate": "2021-07-23T22:52:00Z",
        "numberOfMonths": 60,
        "beta": 0.788081
    }

    x = Quote.from_dict(d)
    print(x)
