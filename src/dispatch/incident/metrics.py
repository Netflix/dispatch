import json
import logging
import math
from calendar import monthrange
from datetime import date
from itertools import groupby

import pandas as pd
from sqlalchemy import and_
from statsmodels.tsa.api import ExponentialSmoothing

from dispatch.database.service import apply_filter_specific_joins, apply_filters
from dispatch.incident.type.models import IncidentType

from .models import Incident

log = logging.getLogger(__name__)


def month_grouper(item):
    """Determines the last day of a given month."""
    key = date(
        item.reported_at.year,
        item.reported_at.month,
        monthrange(item.reported_at.year, item.reported_at.month)[-1],
    )
    return key


def create_incident_metric_query(
    db_session,
    end_date: date,
    start_date: date = None,
    filter_spec: list[dict] | str | None = None,
):
    """Fetches eligible incidents."""
    query = db_session.query(Incident)

    if filter_spec:
        if isinstance(filter_spec, str):
            filter_spec = json.loads(filter_spec)
        query = apply_filter_specific_joins(Incident, filter_spec, query)
        query = apply_filters(query, filter_spec)

    if start_date:
        query = query.filter(
            and_(Incident.reported_at <= end_date, Incident.reported_at >= start_date)
        )
    else:
        query = query.filter(Incident.reported_at <= end_date)

    # exclude incident types
    query = query.filter(IncidentType.exclude_from_metrics.isnot(True))
    return query.all()


def make_forecast(incidents: list[Incident]):
    """Makes an incident forecast."""
    incidents_sorted = sorted(incidents, key=month_grouper)

    dataframe_dict = {"ds": [], "y": []}

    for last_day, items in groupby(incidents_sorted, month_grouper):
        dataframe_dict["ds"].append(str(last_day))
        dataframe_dict["y"].append(len(list(items)))

    dataframe = pd.DataFrame.from_dict(dataframe_dict)

    if dataframe.empty:
        return [], []

    # reset index to by month and drop month column
    dataframe.index = dataframe.ds
    dataframe.index.freq = "M"
    dataframe.drop("ds", inplace=True, axis=1)

    # fill periods without incidents with 0
    idx = pd.date_range(dataframe.index[0], dataframe.index[-1], freq="ME")
    dataframe.index = pd.DatetimeIndex(dataframe.index)
    dataframe = dataframe.reindex(idx, fill_value=0)

    row_count, _ = dataframe.shape

    if row_count > 3:
        try:
            forecaster = ExponentialSmoothing(
                dataframe, seasonal_periods=12, trend="add", seasonal="add"
            ).fit()
        except Exception as e:
            log.warning(f"Issue forecasting incidents: {e}")
            return [], []
        forecast = forecaster.forecast(12)
        forecast_df = pd.DataFrame({"ds": forecast.index.astype("str"), "that": forecast.values})

        forecast_data = forecast_df.to_dict("series")

        # drop day data
        categories = [d[:-3] for d in forecast_data["ds"]]
        predicted_counts = [max(math.ceil(x), 0) for x in list(forecast_data["that"])]
        return categories, predicted_counts
    else:
        return [], []
