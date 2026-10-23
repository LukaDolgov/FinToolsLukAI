def calculate_return(start_price: float, end_price: float):
    if start_price <= 0:
        raise ValueError("invalid starting price, must be > 0")
    stock_return = (end_price - start_price) / start_price
    return stock_return

def moving_average(prices: list[float], window: int) -> float:
    if window <= 0:
        raise ValueError("need window of length 1 or greater")
    if window > len(prices):
        raise ValueError("Window cannot exceed number of prices")
    sub_prices = prices[len(prices) - window:len(prices)]
    tsum = sum(sub_prices)
    res = tsum / window
    return res
    
