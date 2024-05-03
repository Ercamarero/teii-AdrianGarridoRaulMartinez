""" Unit tests for teii.finance.timeseries module """


import datetime as dt

import pytest
from pandas.testing import assert_series_equal
from unittest.mock import patch
from requests.exceptions import ConnectionError
from teii.finance import (FinanceClientInvalidAPIKey, FinanceClientInvalidData,
                          TimeSeriesFinanceClient, FinanceClientAPIError, FinanceClient)


def test_constructor_success(api_key_str,
                             mocked_requests):
    TimeSeriesFinanceClient("AAPL", api_key_str)
    TimeSeriesFinanceClient("IBM", api_key_str)


def test_constructor_failure_invalid_api_key():
    with pytest.raises(FinanceClientInvalidAPIKey):
        TimeSeriesFinanceClient("IBM")


def test_constructor_env(mocked_requests, monkeypatch):
    monkeypatch.setenv('TEII_FINANCE_API_KEY', 'https://www.alphavantage.co/support/#api-key')
    # Llama al constructor de TimeSeriesFinanceClient
    TimeSeriesFinanceClient("AAPL")

    # Asegura que el cliente se ha creado correctamente


def test_weekly_price_invalid_dates(api_key_str,
                                    mocked_requests):
    with pytest.raises(FinanceClientInvalidData):
        fc = TimeSeriesFinanceClient("IBM", api_key_str)
        fc.weekly_price(from_date=dt.date(year=2023, month=1, day=1), to_date=dt.date(year=2022, month=1, day=1))


def test_weekly_price_no_dates(api_key_str,
                               mocked_requests,
                               pandas_series_IBM_prices):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.weekly_price()

    assert ps.count() == 1276   # 2009-11-12 to 2024-04-15 (1276 business weeks)

    assert ps.count() == pandas_series_IBM_prices.count()

    assert_series_equal(ps, pandas_series_IBM_prices)


def test_weekly_price_dates(api_key_str,
                            mocked_requests,
                            pandas_series_IBM_prices_filtered):
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps = fc.weekly_price(dt.date(year=2021, month=1, day=1),
                         dt.date(year=2023, month=12, day=31))

    assert ps.count() == 156    # 2021-01-01 to 2023-12-31 (156 business weeks)

    assert ps.count() == pandas_series_IBM_prices_filtered.count()

    assert_series_equal(ps, pandas_series_IBM_prices_filtered)


def test_weekly_volume_invalid_dates(api_key_str, mocked_requests):

    with pytest.raises(FinanceClientInvalidData):
        fc = TimeSeriesFinanceClient("IBM", api_key_str)
        fc.weekly_volume(from_date=dt.date(year=2023, month=1, day=1), to_date=dt.date(year=2022, month=1, day=1))


def test_weekly_volume_no_dates(api_key_str, mocked_requests):

    fc = TimeSeriesFinanceClient("IBM", api_key_str)
    ps = fc.weekly_volume()
    assert ps is not None


def test_weekly_volume_dates(api_key_str, mocked_requests):

    fc = TimeSeriesFinanceClient("IBM", api_key_str)
    ps = fc.weekly_volume(dt.date(year=2021, month=1, day=1),
                          dt.date(year=2023, month=12, day=31))
    assert ps is not None


# Clase auxiliar para poder ejecutar los test de FinanceClient Libremente.
"""
    Esta clase esta diseñada para cometer todos los errores posibles que se puedan dar en FinanceClient.
"""


class MockFinanceClient(FinanceClient):
    def _build_base_query_url_params(self):
        return "fake_url_params"

    def _build_query_data_key(self):
        return "fake_data_key"

    def _validate_query_data(self):
        pass  # No realiza ninguna validación real


def test_constructor_unsuccessful_request():
    # Simula que requests.get() lanza una ConnectionError
    with patch('requests.get', side_effect=ConnectionError("No se puede establecer conexión")):
        # Espera que el constructor de FinanceClient lance una FinanceClientAPIError
        with pytest.raises(FinanceClientAPIError) as exc_info:
            # Suponiendo que el constructor de FinanceClient hace una llamada a la API
            MockFinanceClient("IBM", "dummy_api_key")
        # Verifica que el mensaje de la excepción es el esperado
        assert "Unsuccessful API access" in str(exc_info.value)
