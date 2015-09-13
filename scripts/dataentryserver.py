import sqlite3
import json
import os.path
import os
from bottle import Bottle, template, request, redirect, response
import csv
import datetime

startBSYear = 1970

daysInBSMonths = [
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #1970
    ( 31, 31, 32, 31, 32, 30, 30, 29, 30, 29,30, 30 ), #1971
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 30 ), #1972
    ( 30, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #1973
    ( 31, 31, 32, 30, 31, 31, 30, 29, 30, 29,30, 30 ), #1974
    ( 31, 31, 32, 32, 30, 31, 30, 29, 30, 29,30, 30 ), #1975
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #1976
    ( 30, 32, 31, 32, 31, 31, 29, 30, 29, 30,29, 31 ), #1977
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #1978
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #1979
    ( 30, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #1980
    ( 31, 31, 31, 32, 31, 31, 29, 30, 30, 29,30, 30 ), #1981
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #1982
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #1983
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #1984
    ( 31, 31, 31, 32, 31, 31, 29, 30, 30, 29,30, 30 ), #1985
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #1986
    ( 31, 32, 31, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #1987
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #1988
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #1989
    ( 30, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #1990
    ( 31, 32, 31, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #1991
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 30 ), #1992
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #1993
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #1994
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #1995
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #1996
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #1997
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #1998
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #1999
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,29, 31 ), #2000
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2001
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2002
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2003
    ( 30, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #2004
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2005
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2006
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2007
    ( 31, 31, 31, 32, 31, 31, 29, 30, 30, 29,29, 31 ), #2008
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2009
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2010
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2011
    ( 31, 31, 31, 32, 31, 31, 29, 30, 30, 29,30, 30 ), #2012
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2013
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2014
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2015
    ( 31, 31, 31, 32, 31, 31, 29, 30, 30, 29,30, 30 ), #2016
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2017
    ( 31, 32, 31, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2018
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #2019
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #2020
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2021
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 30 ), #2022
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #2023
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #2024
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2025
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2026
    ( 30, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #2027
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2028
    ( 31, 31, 32, 31, 32, 30, 30, 29, 30, 29,30, 30 ), #2029
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2030
    ( 30, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #2031
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2032
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2033
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2034
    ( 30, 32, 31, 32, 31, 31, 29, 30, 30, 29,29, 31 ), #2035
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2036
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2037
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2038
    ( 31, 31, 31, 32, 31, 31, 29, 30, 30, 29,30, 30 ), #2039
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2040
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2041
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2042
    ( 31, 31, 31, 32, 31, 31, 29, 30, 30, 29,30, 30 ), #2043
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2044
    ( 31, 32, 31, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2045
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2046
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #2047
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2048
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 30 ), #2049
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #2050
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #2051
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2052
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 30 ), #2053
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #2054
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2055
    ( 31, 31, 32, 31, 32, 30, 30, 29, 30, 29,30, 30 ), #2056
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2057
    ( 30, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #2058
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2059
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2060
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2061
    ( 30, 32, 31, 32, 31, 31, 29, 30, 29, 30,29, 31 ), #2062
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2063
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2064
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2065
    ( 31, 31, 31, 32, 31, 31, 29, 30, 30, 29,29, 31 ), #2066
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2067
    ( 31, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2068
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2069
    ( 31, 31, 31, 32, 31, 31, 29, 30, 30, 29,30, 30 ), #2070
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2071
    ( 31, 32, 31, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2072
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 31 ), #2073
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #2074
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2075
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 30 ), #2076
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,29, 31 ), #2077
    ( 31, 31, 31, 32, 31, 31, 30, 29, 30, 29,30, 30 ), #2078
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 29,30, 30 ), #2079
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 29,30, 30 ), #2080
    ( 31, 31, 32, 32, 31, 30, 30, 30, 29, 30,30, 30 ), #2081
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,30, 30 ), #2082
    ( 31, 31, 32, 31, 31, 30, 30, 30, 29, 30,30, 30 ), #2083
    ( 31, 31, 32, 31, 31, 30, 30, 30, 29, 30,30, 30 ), #2084
    ( 31, 32, 31, 32, 31, 31, 30, 30, 29, 30,30, 30 ), #2085
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,30, 30 ), #2086
    ( 31, 31, 32, 31, 31, 31, 30, 30, 29, 30,30, 30 ), #2087
    ( 30, 31, 32, 32, 30, 31, 30, 30, 29, 30,30, 30 ), #2088
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,30, 30 ), #2089
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,30, 30 ), #2090
    ( 31, 31, 32, 31, 31, 31, 30, 30, 29, 30,30, 30 ), #2091
    ( 31, 31, 32, 32, 31, 30, 30, 30, 29, 30,30, 30 ), #2092
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,30, 30 ), #2093
    ( 31, 31, 32, 31, 31, 30, 30, 30, 29, 30,30, 30 ), #2094
    ( 31, 31, 32, 31, 31, 31, 30, 29, 30, 30,30, 30 ), #2095
    ( 30, 31, 32, 32, 31, 30, 30, 29, 30, 29,30, 30 ), #2096
    ( 31, 32, 31, 32, 31, 30, 30, 30, 29, 30,30, 30 ), #2097
    ( 31, 31, 32, 31, 31, 31, 29, 30, 29, 30,30, 31 ), #2098
    ( 31, 31, 32, 31, 31, 31, 30, 29, 29, 30,30, 30 ), #2099
    ( 31, 32, 31, 32, 30, 31, 30, 29, 30, 29,30, 30 )  #2100
]
    
newYearBS = [
    datetime.datetime(1913, 4, 13), #1970
    datetime.datetime(1914, 4, 13), #1971
    datetime.datetime(1915, 4, 13), #1972
    datetime.datetime(1916, 4, 13), #1973
    datetime.datetime(1917, 4, 13), #1974
    datetime.datetime(1918, 4, 12), #1975
    datetime.datetime(1919, 4, 13), #1976
    datetime.datetime(1920, 4, 13), #1977
    datetime.datetime(1921, 4, 13), #1978
    datetime.datetime(1922, 4, 13), #1979
    datetime.datetime(1923, 4, 13), #1980
    datetime.datetime(1924, 4, 13), #1981
    datetime.datetime(1925, 4, 13), #1982
    datetime.datetime(1926, 4, 13), #1983
    datetime.datetime(1927, 4, 13), #1984
    datetime.datetime(1928, 4, 13), #1985
    datetime.datetime(1929, 4, 13), #1986
    datetime.datetime(1930, 4, 13), #1987
    datetime.datetime(1931, 4, 13), #1988
    datetime.datetime(1932, 4, 13), #1989
    datetime.datetime(1933, 4, 13), #1990
    datetime.datetime(1934, 4, 13), #1991
    datetime.datetime(1935, 4, 13), #1992
    datetime.datetime(1936, 4, 13), #1993
    datetime.datetime(1937, 4, 13), #1994
    datetime.datetime(1938, 4, 13), #1995
    datetime.datetime(1939, 4, 13), #1996
    datetime.datetime(1940, 4, 13), #1997
    datetime.datetime(1941, 4, 13), #1998
    datetime.datetime(1942, 4, 13), #1999
    datetime.datetime(1943, 4, 14), #2000
    datetime.datetime(1944, 4, 13), #2001
    datetime.datetime(1945, 4, 13), #2002
    datetime.datetime(1946, 4, 13), #2003
    datetime.datetime(1947, 4, 14), #2004
    datetime.datetime(1948, 4, 13), #2005
    datetime.datetime(1949, 4, 13), #2006
    datetime.datetime(1950, 4, 13), #2007
    datetime.datetime(1951, 4, 14), #2008
    datetime.datetime(1952, 4, 13), #2009
    datetime.datetime(1953, 4, 13), #2010
    datetime.datetime(1954, 4, 13), #2011
    datetime.datetime(1955, 4, 14), #2012
    datetime.datetime(1956, 4, 13), #2013
    datetime.datetime(1957, 4, 13), #2014
    datetime.datetime(1958, 4, 13), #2015
    datetime.datetime(1959, 4, 14), #2016
    datetime.datetime(1960, 4, 13), #2017
    datetime.datetime(1961, 4, 13), #2018
    datetime.datetime(1962, 4, 13), #2019
    datetime.datetime(1963, 4, 14), #2020
    datetime.datetime(1964, 4, 13), #2021
    datetime.datetime(1965, 4, 13), #2022
    datetime.datetime(1966, 4, 13), #2023
    datetime.datetime(1967, 4, 14), #2024
    datetime.datetime(1968, 4, 13), #2025
    datetime.datetime(1969, 4, 13), #2026
    datetime.datetime(1970, 4, 14), #2027
    datetime.datetime(1971, 4, 14), #2028
    datetime.datetime(1972, 4, 13), #2029
    datetime.datetime(1973, 4, 13), #2030
    datetime.datetime(1974, 4, 14), #2031
    datetime.datetime(1975, 4, 14), #2032
    datetime.datetime(1976, 4, 13), #2033
    datetime.datetime(1977, 4, 13), #2034
    datetime.datetime(1978, 4, 14), #2035
    datetime.datetime(1979, 4, 14), #2036
    datetime.datetime(1980, 4, 13), #2037
    datetime.datetime(1981, 4, 13), #2038
    datetime.datetime(1982, 4, 14), #2039
    datetime.datetime(1983, 4, 14), #2040
    datetime.datetime(1984, 4, 13), #2041
    datetime.datetime(1985, 4, 13), #2042
    datetime.datetime(1986, 4, 14), #2043
    datetime.datetime(1987, 4, 14), #2044
    datetime.datetime(1988, 4, 13), #2045
    datetime.datetime(1989, 4, 13), #2046
    datetime.datetime(1990, 4, 14), #2047
    datetime.datetime(1991, 4, 14), #2048
    datetime.datetime(1992, 4, 13), #2049
    datetime.datetime(1993, 4, 13), #2050
    datetime.datetime(1994, 4, 14), #2051
    datetime.datetime(1995, 4, 14), #2052
    datetime.datetime(1996, 4, 13), #2053
    datetime.datetime(1997, 4, 13), #2054
    datetime.datetime(1998, 4, 14), #2055
    datetime.datetime(1999, 4, 14), #2056
    datetime.datetime(2000, 4, 13), #2057
    datetime.datetime(2001, 4, 14), #2058
    datetime.datetime(2002, 4, 14), #2059
    datetime.datetime(2003, 4, 14), #2060
    datetime.datetime(2004, 4, 13), #2061
    datetime.datetime(2005, 4, 14), #2062
    datetime.datetime(2005, 4, 14), #2063
    datetime.datetime(2007, 4, 14), #2064
    datetime.datetime(2008, 4, 13), #2065
    datetime.datetime(2009, 4, 14), #2066
    datetime.datetime(2010, 4, 14), #2067
    datetime.datetime(2011, 4, 14), #2068
    datetime.datetime(2012, 4, 13), #2069
    datetime.datetime(2013, 4, 14), #2070
    datetime.datetime(2014, 4, 14), #2071
    datetime.datetime(2015, 4, 14), #2072
    datetime.datetime(2016, 4, 13), #2073
    datetime.datetime(2017, 4, 14), #2074
    datetime.datetime(2018, 4, 14), #2075
    datetime.datetime(2019, 4, 14), #2076
    datetime.datetime(2020, 4, 13), #2077
    datetime.datetime(2021, 4, 14), #2078
    datetime.datetime(2022, 4, 14), #2079
    datetime.datetime(2023, 4, 14), #2080
    datetime.datetime(2024, 4, 13), #2081
    datetime.datetime(2025, 4, 14), #2082
    datetime.datetime(2026, 4, 14), #2083
    datetime.datetime(2027, 4, 14), #2084
    datetime.datetime(2028, 4, 13), #2085
    datetime.datetime(2029, 4, 14), #2086
    datetime.datetime(2030, 4, 14), #2087
    datetime.datetime(2031, 4, 15), #2088
    datetime.datetime(2032, 4, 14), #2089
    datetime.datetime(2033, 4, 14), #2090
    datetime.datetime(2034, 4, 14), #2091
    datetime.datetime(2035, 4, 13), #2092
    datetime.datetime(2036, 4, 14), #2093
    datetime.datetime(2037, 4, 14), #2094
    datetime.datetime(2038, 4, 14), #2095
    datetime.datetime(2039, 4, 15), #2096
    datetime.datetime(2040, 4, 13), #2097
    datetime.datetime(2041, 4, 14), #2098
    datetime.datetime(2042, 4, 14), #2099
    datetime.datetime(2043, 4, 14)  #2100
]

#def bs2ad(year, month, day):
def bs2ad(date):
    #accepts date in the format YYYY/MM/DD
    try:
        date_a = date.split("/", 3)
        year = int(date_a[0])
        month = int(date_a[1])
        day = int(date_a[2])
    except:
        return ""
        
    if year < startBSYear or year > (startBSYear + len(newYearBS) - 1) :
        raise Exception

    if month < 1 or month > 12:
        raise Exception

    offset = year - startBSYear

    newYearDayAD = newYearBS[offset]
    daysInCurrentBSMonths = daysInBSMonths[offset]

    if day < 1 or day > daysInCurrentBSMonths[month - 1]:
        print daysInCurrentBSMonths
        print daysInCurrentBSMonths[month - 1]
        raise Exception

    dayDelta = 0
    for i in range(0, month-1):
        dayDelta += daysInCurrentBSMonths[i]
    dayDelta += day

    timeDelta = datetime.timedelta(days=dayDelta-1)

    datead = newYearDayAD + timeDelta

    return datead.strftime('%Y-%m-%d')


def ad2bs(date):
    bsYear = 0
    currentnewYearDayAD = None
    for i, newYearDayAD in reversed(list(enumerate(newYearBS))):
        if date >= newYearDayAD:
            bsYear = i+startBSYear
            currentnewYearDayAD = newYearDayAD
            break

    if currentnewYearDayAD == None:
        raise Exception

    timeDelta = date - currentnewYearDayAD
    timeDeltaDays = timeDelta.days

    offset = bsYear - startBSYear

    daysInCurrentBSMonths = daysInBSMonths[offset]

    bsMonth = None
    bsDay = None
    for i in range(0, len(daysInCurrentBSMonths)):
        currentDays = daysInCurrentBSMonths[i]
        if timeDeltaDays < daysInCurrentBSMonths[i]:
            bsMonth = i + 1
            bsDay = timeDeltaDays + 1
            break

        timeDeltaDays -= daysInCurrentBSMonths[i]

    if bsMonth == None:
        raise Exception

    return (bsYear, bsMonth, bsDay)

app = Bottle()

class DataBase:
    def __init__(self, filename, schema):
        self.schema = schema
        self.db  = sqlite3.connect(filename)
        
        self.create()


    def close(self):
        self.db.close()


    def create(self):
        result, = self.db.execute(
            "SELECT COUNT() FROM sqlite_master WHERE type='table' AND name='data';").fetchone()

        if result == 0:
            query = "CREATE TABLE IF NOT EXISTS data ("
            for i in range(0, len(self.schema)):
                col = self.schema[i]
                if len(col) > 1:
                    query += col[0]
                    query += " "
                    if col[1] == "INTINDX":
                        query += "INTEGER PRIMARY KEY"
                    elif col[1] == "INT":
                        query += "INTEGER"
                    elif col[1] == "REAL":
                        query += "REAL"
                    elif col[1] == "DATE":
                        query += "DATE"
                    elif col[1] == "TIME":
                        query += "TIME"
                    else:
                        query += "TEXT"
                    if (i != len(self.schema)-1):
                        query += ", "
            query += ");"

            self.db.execute(query)
            self.db.commit()

        iqcols = ''
        iqvalues = ''
        uqvalues = ''
        sqcols = ''
        for i in range(0, len(self.schema)):
            col = self.schema[i]
            if len(col) > 1:
                sqcols += col[0]
                if (i != len(self.schema)-1):
                    sqcols += ", "
                if col[1] != 'INTINDX':
                    iqcols += col[0]
                    iqvalues += ':' + col[0]
                    uqvalues += "{0} = :{0} ".format(col[0])
                    if (i != len(self.schema)-1):
                        iqcols += ", "
                        iqvalues += ", "
                        uqvalues += ", "
                

        self.iquery = "INSERT INTO  data({0}) VALUES({1})".format(iqcols, iqvalues)
        self.uquery = "UPDATE data SET {0} WHERE {1}=:{1}".format(uqvalues, '{0}')
        self.squery = "SELECT {0} FROM data WHERE {1}=:{1}".format(sqcols, '{0}')

        result, = self.db.execute(
            "SELECT COUNT() FROM sqlite_master WHERE type='table' AND name='uniquecounter';").fetchone()

        if result == 0:
            query = "CREATE TABLE IF NOT EXISTS uniquecounter (id INTEGER PRIMARY KEY, counter INTEGER)"
            self.db.execute(query)
            query = "INSERT INTO  uniquecounter(counter) VALUES(1)"
            self.db.execute(query)
            self.db.commit()


    def add(self, data):
        datai = {}
        for col in self.schema:
            if len(col) >  1:
                if col[1] != 'INTINDX':
                    try:
                        datai[col[0]] = data[col[0]]
                    except KeyError:
                        datai[col[0]] = ''

        print(datai)

        try:
            result = self.db.execute(self.iquery, datai)
            
            self.db.commit()

            return result.lastrowid
        except sqlite3.DatabaseError:
            self.db.rollback()

            return False


    def update(self, data):
        datai = {}
        indexcol = ""
        for col in self.schema:
            if len(col) > 1:
                if col[1] == 'INTINDX':
                    indexcol = col[0]
                try:
                    datai[col[0]] = data[col[0]]
                except KeyError:
                    datai[col[0]] = ''

        if indexcol == "":
            return False

        query = self.uquery.format(indexcol)

        try:
            result = self.db.execute(query, datai)
            
            self.db.commit()

            return True
        except sqlite3.DatabaseError:
            self.db.rollback()

            return False


    def get(self, col, filter):
        query = self.squery.format(col)

        try:
            row = self.db.execute(query, { col : filter }).fetchone()
        except sqlite3.DatabaseError:
            return False

        if row == None:
            return False

        result = {}
        coli = 0
        for i in range(0, len(self.schema)):
            col = self.schema[i]
            if len(col) > 1:
                result[col[0]] = row[coli]
                coli += 1

        return result


    def list(self, cols, filter=""):
        query = "SELECT {0} FROM data".format(cols)
        if filter != "":
            query += " WHERE {0}".format(filter)
        
        try:
            rows = self.db.execute(query)
        except sqlite3.DatabaseError:
            return False

        return rows


    def getuniqueid(self):
        counter, = self.db.execute('SELECT counter FROM uniquecounter WHERE id = 1').fetchone()

        uniqueid = counter

        counter += 1

        try:
            result = self.db.execute("UPDATE uniquecounter SET counter={0} WHERE id=1".format(counter))
            
            self.db.commit()

            return uniqueid
        except sqlite3.DatabaseError:
            self.db.rollback()

            return False


class DataEntry(Bottle):
    def __init__(self, settingsfile):
        Bottle.__init__(self)
        self.settings = self.loadSettings(settingsfile)

        if self.settings == False:
            self.alert('Error', 'Error loading settings from "{0}"'.format(settingsfile))
            
        self.schema = self.settings['schema']

        self.db = DataBase(self.settings['dbfile'], self.schema)

        self.imageStore = self.settings['imagestore']

        self.status = ""


    def loadSettings(self, settingsfile):
        settingstr = ""
        try:
            with open(settingsfile) as f:
                settingstr = f.read()
            settings = json.loads(settingstr)
        except IOError:
            print 'Settings file not found at {0}'.format(settingsfile)
            return False

        if 'dbfile' in settings and 'imagestore' in settings and 'schema' in settings:
            if len(settings['schema']) > 0:
                return settings

        print 'Settings format wrong in {0}'.format(settingsfile)
        return False


    def alert(self, title, message):
        print("{0} : {1}".format(title, message))


    def setStatus(self, message):
        self.status = message


    def template(self, name, page=None):
        try:
            filename = "{0}{1}.html".format(self.settings['templates'],name)
            with open(filename) as f:
                templatestr = f.read()
            return template(templatestr, page=page, status=self.status)
            
        except IOError:
            return 'Template not found at {0}'.format(filename)


    def listPatients(self, filter):
        patientList = {}
        patientList['headers'] = ("#", "IP", "Name", "Age", "Sex")
        patientList['rows'] = self.db.list('patientid, ipnumber, name, age, sex', filter)

        return self.template('list', patientList)


    def viewPatientById(self, patientid):
        page = {}
        data = self.db.get('patientid', patientid)

        if data == False:
            return self.template("error", "Patient {0} not found".format(patientid))
        
        page['form'] = self.generateForm(data)
        page['action'] = "/patients/{0}/update".format(patientid)

        return '<form method="post" action="{0}">{1}<input type="submit" value="Save"></form>'.format(page['action'], page['form'])


    def viewPatientByIp(self, ipnumber):
        page = {}
        data = self.db.get('ipnumber', ipnumber)

        if data == False:
            return self.template("error", "Patient with IP Number {0} not found".format(ipnumber))

        patientid = data['patientid']

        page['form'] = self.generateForm(data)
        page['action'] = "/patients/{0}/update".format(patientid)

        return '<form method="post" action="{0}">{1}<input type="submit" value="Save"></form>'.format(page['action'], page['form'])


    def newPatientForm(self):
        page = {}
        
        page['form'] = self.generateForm()
        page['action'] = "/patients/new"

        return '<form method="post" action="{0}" >{1}<input type="submit" value="Save"></form>'.format(page['action'], page['form'])


    def addPatient(self, data):
        patientid = self.db.add(data)

        return patientid


    def processForm(self, form):
        data = {}

        for col in self.schema:
            if len(col) > 1:
                data[col[0]] = form.get(col[0])

        return data


    def generateForm(self, data={}):
        form = '<table>'
        for col in self.schema:
            if len(col) > 1:
                if col[0] in data:
                    form += self.generateInput(col, data[col[0]])
                else:
                    form += self.generateInput(col)
            else:
                form += '<tr><td colspan="2" style="text-align: center;"><b>{0}</b></td></tr>'.format(col[0])
        form += '</table>'
        return form


    def generateInput(self, col, value=""):
        value = template("{{value}}", value = value)
        form = '<tr>'
        form += '<td><label for="{0}">{1}</label></td>'.format(col[0], col[2])
        form += '<td>'
        if col[1] == 'SEL':
            selList = ''
            for selvalue, sellabel in col[3].iteritems():
                seleted = ""
                if value == selvalue:
                    seleted = "selected"
                selList += '<option value="{0}" {2}>{1}</option>'.format(selvalue, sellabel, seleted)
            form += '<select id="{0}" name="{0}"/ >{1}</select>'.format(col[0], selList)
        elif col[1] == 'INTINDX':
            disabled = "disabled"
            form += '<input id="{0}" name="{0}" type="text" value="{1}" {2} />'.format(col[0], value, disabled)
        elif col[1] == 'DATE':
            form += '<input id="{0}" name="{0}" type="date" value="{1}"/>'.format(col[0], value)
        elif col[1] == 'TIME':
            form += '<input id="{0}" name="{0}" type="time" value="{1}" />'.format(col[0], value)
        elif col[1] == 'INT':
            form += '<input id="{0}" name="{0}" type="number" value="{1}" />'.format(col[0], value)
        elif col[1] == 'REAL':
            form += '<input id="{0}" name="{0}" type="number" value="{1}" />'.format(col[0], value)
        else:
            form += '<input id="{0}" name="{0}" type="text" value="{1}" />'.format(col[0], value)
        form += '</td>'
        form += '</tr>'
        return form


    def getCSV(self):
        selectcols = []
        coltitles = []
        for col in self.schema:
            if len(col) > 1:
                selectcols.append(col[0])
                coltitles.append(col[2])
                
        selectcolsstr = ",".join(selectcols)
        coltitlesstr = ",".join(coltitles)
            
        rows = self.db.list(selectcolsstr, "")

        result = "{0}\r\n".format(coltitlesstr)
        result += "{0}\r\n".format(selectcolsstr)

        for row in rows:
            rowstr = []
            for col in row:
                if col == None:
                    col = ""
                colstr = str(col)
                colstr = colstr.replace("\"", "\"\"")
                colstr = "\"{0}\"".format(colstr)
                rowstr.append(colstr)
            result += "{0}\r\n".format(",".join(rowstr))
            
        return result


    def getCSVbs2ad(self):
        selectcols = []
        coltitles = []
        for col in self.schema:
            if len(col) > 1:
                selectcols.append(col[0])
                coltitles.append(col[2])
                
        selectcolsstr = ",".join(selectcols)
        coltitlesstr = ",".join(coltitles)
            
        rows = self.db.list(selectcolsstr, "")

        result = "{0}\r\n".format(coltitlesstr)
        result += "{0}\r\n".format(selectcolsstr)

        for row in rows:
            rowstr = []
            row_a = []
            
            for col in row:
                row_a.append(col)
                
            if row_a[8] != None:
                row_a[6] = bs2ad(row_a[8])

            if row_a[9] != None:
                row_a[7] = bs2ad(row_a[9])

            for col in row_a:
                if col == None:
                    col = ""
                colstr = str(col)
                colstr = colstr.replace("\"", "\"\"")
                colstr = "\"{0}\"".format(colstr)
                rowstr.append(colstr)
            result += "{0}\r\n".format(",".join(rowstr))
            
        return result



    def importCSV(self, csvfile):
        csvreader = csv.reader(csvfile)
        colLables = csvreader.next()
        colNames = csvreader.next()
        for row in csvreader:
            data = {}
            try:
                for i in range(0, len(colNames)):
                    data[colNames[i]] = row[i]
            except KeyError:
                print "Too few cols"

            patientid = self.addPatient(data)

            print "Added new patient {0}".format(patientid)

        return True
            
        


if __name__ == '__main__':
    settingsfile = '/sdcard/sl4a/res/dataentry.settings'
    #settingsfile = '../res/dataentry.settings'

    app = DataEntry(settingsfile)

    @app.get("/")
    def index():
        redirect("/patients/")


    @app.get("/patients")
    def index():
        redirect("/patients/")


    @app.get("/patients/")
    def list():
        return app.listPatients("")


    @app.post("/search")
    def search():
        ipnumber = request.forms.get('ipnumber')
        return patientip(ipnumber)


    @app.get("/patients.csv")
    def exportcsv():
        response.set_header("Content_Type", "text/csv")
        return app.getCSV()


    @app.get("/patients-bs2ad.csv")
    def exportcsv():
        response.set_header("Content_Type", "text/csv")
        return app.getCSVbs2ad()


    @app.get("/patients/importcsv")
    def importcsv():
        return app.template("importcsv")


    @app.post("/patients/importcsv")
    def do_importcsv():
        category   = request.forms.get('category')
        upload     = request.files.get('upload')
        name, ext = os.path.splitext(upload.filename)
        if ext not in ('.csv'):
            return 'File extension not allowed.'

        #upload.save(app.settings["tmp"]) # appends upload.filename automatically
        #filename = app.settings["tmp"]+upload.filename
        
        if app.importCSV(upload.file):
            return 'CSV Uploaded'
        else:
            return "An Error Occured"

        redirect("/list")


    @app.get("/patients/<patientid>")
    def patient(patientid):
        return app.viewPatientById(patientid)


    @app.get("/patients/ip/<ipnumber>")
    def patientip(ipnumber):
        return app.viewPatientByIp(ipnumber)


    @app.post("/patients/<patientid>/update")
    def updatepatient(patientid):
        data = app.processForm(request.forms)

        data['patientid'] = int(patientid)

        result = app.db.update(data)

        if patientid != False:
            redirect("/patients/{0}".format(patientid))
            return 'Patient updates {0}'.format(patientid)
        else:
            return 'Error updating patient'


    @app.get("/patients/new")
    def newpatient():
        return app.newPatientForm()


    @app.post("/patients/new")
    def do_newpatient():
        data = app.processForm(request.forms)

        patientid = app.db.add(data)

        if patientid != False:
            redirect("/patients/{0}".format(patientid))
            return 'Patient saved {0}'.format(patientid)
        else:
            return 'Error saving patient'


    app.run(host="0.0.0.0", port="8080")
    
    '''
    try:
        main.start()
    except sqlite3.InterfaceError:
        main.alert('Error', 'Database interface error')
    except sqlite3.DatabaseError:
        main.lert('Error', 'Database error')
    finally:
        main.exit()
    '''


