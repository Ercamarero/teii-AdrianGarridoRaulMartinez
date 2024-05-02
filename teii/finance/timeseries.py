""" Time Series Finance Client classes """


import datetime as dt
import logging
from typing import Optional, Union

import pandas as pd

from teii.finance import FinanceClient, FinanceClientInvalidData

"""
TimeSeriesFinanceClient
    Clase que hereda de FinanceClient
Parametres
----------
     _data_field2name_type : diccionario
        para la gestion de los datos leidos


Returns
------
    TimeSeriesFinanceClient
"""


class TimeSeriesFinanceClient(FinanceClient):
    """ Wrapper around the AlphaVantage API for Time Series Weekly Adjusted.

        Source:
            https://www.alphavantage.co/documentation/ (TIME_SERIES_WEEKLY_ADJUSTED)
    """

    _data_field2name_type = {
        "1. open":                  ("open",     "float"),
        "2. high":                  ("high",     "float"),
        "3. low":                   ("low",      "float"),
        "4. close":                 ("close",    "float"),
        "5. adjusted close":        ("aclose",   "float"),
        "6. volume":                ("volume",   "int"),
        "7. dividend amount":       ("dividend", "float")
    }

    def __init__(self, ticker: str,
                 api_key: Optional[str] = None,
                 logging_level: Union[int, str] = logging.WARNING) -> None:
        """ TimeSeriesFinanceClient constructor. """

        super().__init__(ticker, api_key, logging_level)

        self._build_data_frame()
    """
    def _build_data_frame(self) -> None:
        Genera el Data frame y format data
    Raises
    ------
        FinanceCLientInvalidData
            datos inexistentes o innacesibles.
    """
    def _build_data_frame(self) -> None:
        """ Build Panda's DataFrame and format data. """
    try:
        if not self._json_data:
            raise FinanceClientInvalidData("No data available")

        data_frame = pd.DataFrame.from_dict(self._json_data, orient='index')

        # Comprobar que todos los campos requeridos están en el DataFrame
        required_fields = set(self._data_field2name_type.keys())
        missing_fields = required_fields - set(data_frame.columns)
        if missing_fields:
            raise FinanceClientInvalidData(f"Missing required data fields: {missing_fields}")

        # Renombrar los campos de datos y configurar los tipos de datos
        data_frame = data_frame.rename(columns={key: name_type[0] for key, name_type in self._data_field2name_type.items()})
        data_frame = data_frame.astype({name_type[0]: name_type[1] for key, name_type in self._data_field2name_type.items()})

        # Configurar el tipo de índice y ordenar los datos
        data_frame.index = pd.to_datetime(data_frame.index)
        self._data_frame = data_frame.sort_index(ascending=True)
    except Exception as e:
        raise FinanceClientInvalidData("Invalid data format or error in data processing") from e

    """
    def _build_base_query_url_params(self) -> str:
        Genera la query de los datos que queremos tratar.
    Returns
    -------
     String
        Query generada.
    """
    def _build_base_query_url_params(self) -> str:
        """ Return base query URL parameters.

        Parameters are dependent on the query type:
            https://www.alphavantage.co/documentation/
        URL format:
            https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol=TICKER&outputsize=full&apikey=API_KEY&data_type=json
        """

        return f"function=TIME_SERIES_WEEKLY_ADJUSTED&symbol={self._ticker}&outputsize=full&apikey={self._api_key}"

    """
    def _build_query_data_key(cls) -> str:
        String para la gestion de la periodicidad del ajuste de los datos.
    Returns
    -------
    String
        String con la periodicidad deseada.
    """
    @classmethod
    def _build_query_data_key(cls) -> str:
        """ Return data query key. """

        return "Weekly Adjusted Time Series"

    """
    def _validate_query_data(self) -> None:
        Validador de la presencia de un json con los datos que deseamos.
    Raises
    ------
        FinanceClientInvalidData
            los datos no se pueden localizar o usar.
    """
    def _validate_query_data(self) -> None:
        """ Validate query data. """

        try:
            assert self._json_metadata["2. Symbol"] == self._ticker
        except Exception as e:
            raise FinanceClientInvalidData("Metadata field '2. Symbol' not found") from e
        else:
            self._logger.info(f"Metadata key '2. Symbol' = '{self._ticker}' found")

    """
    def weekly_price(self,from_date: Optional[dt.date] = None,to_date: Optional[dt.date] = None) -> pd.Series:
        Genera una serie con la relacion precio semana del ticker deseado.
    Raises
    ------
        FinanceClientParamError
            En caso de fecha invalida devolver un error.
    Returns
    -------
        Serie Pandas
            Serie de precios indexados por semanas.
    """
    def weekly_price(self,
                     from_date: Optional[dt.date] = None,
                     to_date: Optional[dt.date] = None) -> pd.Series:
        """ Return weekly close price from 'from_date' to 'to_date'. """

        assert self._data_frame is not None

        series = self._data_frame['aclose']

        # TODO
        #   Comprueba que from_date <= to_date y genera excepción
        #   'FinanceClientParamError' en caso de error
        if isinstance(to_date, dt.date) and isinstance(from_date, dt.date) and to_date <= from_date:
            raise FinanceClientInvalidData("to_date cannot be less than from_date")

        # FIXME: type hint error
        if from_date is not None and to_date is not None:
            series = series.loc[from_date:to_date]   # type: ignore

        return series

    """
     def weekly_volume(self,from_date: Optional[dt.date] = None, to_date: Optional[dt.date] = None) -> pd.Series:
        Serie con el volumen semanal de ventas.
        Raises
        ------
        FinanceClientParamError
            En caso de fecha incorrecta
        Returns
        -------
        Serie Pandas
            Serie que contiene el volumen de ventas indexado por las semanas de un tramo.
    """
    def weekly_volume(self,
                      from_date: Optional[dt.date] = None,
                      to_date: Optional[dt.date] = None) -> pd.Series:
        """ Return weekly volume from 'from_date' to 'to_date'. """

        assert self._data_frame is not None

        series = self._data_frame['volume']

        # TODO
        #   Comprueba que from_date <= to_date y genera excepción
        #   'FinanceClientParamError' en caso de error
        if isinstance(to_date, dt.date) and isinstance(from_date, dt.date) and to_date <= from_date:
            raise FinanceClientInvalidData("to_date cannot be less than from_date")

        # FIXME: type hint error
        if from_date is not None and to_date is not None:
            series = series.loc[from_date:to_date]   # type: ignore

        return series
