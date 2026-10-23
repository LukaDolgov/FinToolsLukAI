import pytest
from tools import calculate_return, moving_average

def test_positive_return():
    res = calculate_return(100, 125)
    assert res == 0.25


def test_negative_return():
    res = calculate_return(100, 75)
    assert res == -0.25

def test_invalid_start_price():
    with pytest.raises(ValueError):
        calculate_return(0, 100)

def test_moving_avgs():
    prices = [10, 12, 14, 16, 18]
    result = moving_average(prices, 3)
    assert result == 16.0
    
def test_invalid_window():
    with pytest.raises(ValueError):
        moving_average([10, 20, 30], 0)
def test_window_too_large():
    with pytest.raises(ValueError):
        moving_average([10, 20, 30], 5)