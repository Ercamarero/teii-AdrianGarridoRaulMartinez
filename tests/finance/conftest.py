""" Unit tests for teii.finance subpackage """


import json
import unittest.mock as mock
from importlib import resources

import pandas as pd
from pytest import fixture

import teii.finance.finance


@fixture(scope='session')
def api_key_str():
    return ("nokey")


@fixture(scope='package')
def mocked_requests():
    def mocked_get(url):
        response = mock.Mock()
        response.status_code = 200
        if 'IBM' in url:
            json_filename = 'TIME_SERIES_WEEKLY_ADJUSTED.IBM.json'
        elif 'AAPL' in url:
            json_filename = 'TIME_SERIES_WEEKLY_ADJUSTED.AAPL.json'
        else:
            raise ValueError('Ticker no soportado')
        with resources.open_text('teii.finance.data', json_filename) as json_file:
            json_data = json.load(json_file)
        response.json.return_value = json_data
        return response

    mocked_requests = mock.Mock()
    mocked_requests.get.side_effect = mocked_get

    teii.finance.finance.requests = mocked_requests

def mocked_requests_get(*args, **kwargs):
    """Simulate requests.get for test purposes."""
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == "https://api.example.com/data?ticker=NODATA":
        return MockResponse({
            "Meta Data": {
                "2. Symbol": "NODATA",
                "4. Last Refreshed": "2024-04-25"
            },
            "Weekly Adjusted Time Series": {}  # No weekly data available
        }, 200)
    return MockResponse(None, 404)

@fixture(scope='package')
def pandas_series_IBM_prices():
    with resources.path('teii.finance.data', 'TIME_SERIES_WEEKLY_ADJUSTED.IBM.aclose.unfiltered.csv') as path2csv:
        df = pd.read_csv(path2csv, index_col=0, parse_dates=True)
        ds = df['aclose']
    return ds


@fixture(scope='package')
def pandas_series_IBM_prices_filtered():
    with resources.path('teii.finance.data', 'TIME_SERIES_WEEKLY_ADJUSTED.IBM.aclose.filtered.csv') as path2csv:
        df = pd.read_csv(path2csv, index_col=0, parse_dates=True)
        ds = df['aclose']
    return ds
