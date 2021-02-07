import pytest

from aqi import aqi

values_1 = [46.3, 27.4,59.8, 129.2, 130.6, 215.4, 143.2, 93.7, 101.8, 49.3, 80.2, 123.3]
values_2 = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
values_3 = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 1000]
values_4 = [500, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]


def test_aqi():
    ''' PyTest neće raditi ako ima __init__.py fajl... :/ '''
    
    test_1 = aqi(values_1)
    test_2 = aqi(values_2)
    test_3 = aqi(values_3)
    test_4 = aqi(values_4)


    assert test_1.aqi == 149.0
    assert test_2.aqi == 41.0
    assert test_3.koncentracija == 10.2
    assert test_4.koncentracija == 257.5
    assert test_1.opis == "nezdravo za osjetljive"