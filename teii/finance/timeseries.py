""" Time Series Finance Client classes """


import datetime as dt
import logging
from typing import Optional, Tuple, Union

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
                 logging_level: Union[int, str] = logging.INFO) -> None:
        """ TimeSeriesFinanceClient constructor. """

        super().__init__(ticker, api_key, logging_level)
        # Cambia 'nombre_del_archivo.log' al nombre que desees
        file_handler = logging.FileHandler('timeseries.log')
        file_handler.setLevel(logging.DEBUG)
        self._logger.addHandler(file_handler)

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

        # TODO
        #   Comprueba que no se produce ningún error y genera excepción
        #   'FinanceClientInvalidData' en caso contrario
        try:
            # Build Panda's data frame
            data_frame = pd.DataFrame.from_dict(self._json_data, orient='index', dtype='float')

            # Rename data fields
            data_frame = data_frame.rename(columns={key: name_type[0]
                                           for key, name_type in self._data_field2name_type.items()})

            # Set data field types
            data_frame = data_frame.astype(dtype={name_type[0]: name_type[1]
                                           for key, name_type in self._data_field2name_type.items()})

            # Set index type
            data_frame.index = data_frame.index.astype("datetime64[ns]")

            # Sort data
            self._data_frame = data_frame.sort_index(ascending=True)
            self._logger.info("DataFrame successfully built.")
        except Exception as e:
            self._logger.error("Error building DataFrame.", exc_info=True)
            raise FinanceClientInvalidData("Invalid data") from e
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
            self._logger.info(f"Metadata key '2. Symbol' = '{self._ticker}' found")
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
            self._logger.error("to_date cannot be less than from_date.")
            raise FinanceClientInvalidData("to_date cannot be less than from_date")

        # FIXME: type hint error
        if from_date is not None and to_date is not None:
            series = series.loc[from_date:to_date]   # type: ignore

        self._logger.info("Weekly price series successfully generated.")
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
            self._logger.error("to_date cannot be less than from_date.")
            raise FinanceClientInvalidData("to_date cannot be less than from_date")

        # FIXME: type hint error
        if from_date is not None and to_date is not None:
            series = series.loc[from_date:to_date]   # type: ignore

        self._logger.info("Weekly volume series successfully generated.")
        return series

    """
    def yearly_dividends
        Funcion para el calculo de los dividendos anuales asociados al ticker del FinanceClient
        en un periodo de años o a lo largo de toda su historia registrada.
    Parametres
    ----------
    from_year: entero.
        Numero que hace referencia desde que año estamos calculando en caso de nulo se hace desde el principio.
    to_year: entero
        Numero que hace referencia a la condicion de parada de la busqueda en caso de nulo se hará hasta el final.
    Returns
    -------
    serie: pd.Series
        Devuelve una pandas series con la asociacion fecha, dividendos totales del año.
    """
    def yearly_dividends(self,
                         from_year: Optional[int] = None,
                         to_year: Optional[int] = None) -> pd.Series:

        if self._data_frame is None:
            self._logger.info("Yearly dividends series successfully generated.")
            raise FinanceClientInvalidData("Data frame not initialized")

        # Asegurarte de que solo se está trabajando con la columna de dividendos
        dividends = self._data_frame['dividend']  # Asumiendo que 'dividend' es la columna de interés
        annual_dividends = dividends.resample('Y').sum()  # Esto debe ser una Series si 'dividend' es una Serie

        # Filtrar según los años proporcionados, si es necesario
        if from_year is not None:
            annual_dividends = annual_dividends[pd.to_datetime(annual_dividends.index).year >= from_year]
        if to_year is not None:
            annual_dividends = annual_dividends[pd.to_datetime(annual_dividends.index).year <= to_year]

        self._logger.info("Yearly dividends series successfully generated.")
        return annual_dividends

    """
     def highest_weekly_variation
     Parametres
     ----------
     from_date: date
        fecha de inicio de evaluacion de los datos en caso de nulo se recogen desde el inicio.
     to_date: date
        fecha de fin de evaluacion de los  en caso de nulo se realiza el fichero hasta el final.
     Returns
     -------
     Tupla:
     -------
        asocia la fecha examinada con las variaciones de la semana.
    """
    def highest_weekly_variation(self,
                                 from_date: Optional[dt.date] = None,
                                 to_date: Optional[dt.date] = None) -> Tuple[dt.date, float, float, float]:
        """Return highest weekly variation from 'from_date' to 'to_date'."""
        assert self._data_frame is not None

        series_high = self._data_frame['high']
        series_low = self._data_frame['low']
        # Utilizar las fechas convertidas para filtrar el DataFrame
        if from_date is not None and to_date is not None:
            # Asegurarse de que las fechas son inclusivas al final del período
            series_high = series_high.loc[from_date:to_date]  # type: ignore
            series_low = series_low.loc[from_date:to_date]  # type: ignore
        # Calcular la variación semanal entre precios altos y bajos

        series_high_low = series_high - series_low
        max_index = series_high_low.idxmax()

        # Asegurarse de que el índice es un Timestamp y extraer la fecha
        if not isinstance(max_index, pd.Timestamp):
            self._logger.error("Index must be a Timestamp.")
            raise ValueError("Index must be a Timestamp")

        self._logger.info("Highest weekly variation successfully calculated.")
        return max_index.date(), series_high[max_index], series_low[max_index], series_high_low[max_index]
