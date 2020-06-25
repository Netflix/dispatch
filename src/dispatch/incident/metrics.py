import math
import logging
from itertools import groupby

from sqlalchemy.sql.expression import true
from datetime import date
from dateutil.relativedelta import relativedelta

from calendar import monthrange

import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing

from dispatch.incident_type.models import IncidentType
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


def get_incident_counts(db_session, months=2):
    """Counts the number of incident in the last n months."""
    incidents = (
        db_session.query(Incident)
        .join(IncidentType)
        .filter(IncidentType.exclude_from_metrics.isnot(True))
        .filter(Incident.reported_at > date.today().replace(day=1) + relativedelta(months=-2))
        .all()
    )

    counts = []
    incidents_sorted = sorted(incidents, key=month_grouper)
    for (key, items) in groupby(incidents_sorted, month_grouper):
        items = list(items)
        counts.append(len(items))
    return counts


def make_forecast(
    db_session, incident_type: str = None, periods: int = 24, grouping: str = "month"
):
    """Makes an incident forecast."""
    query = db_session.query(Incident).join(IncidentType)

    # exclude incident types
    query = query.filter(IncidentType.exclude_from_metrics.isnot(True))

    # exclude last two months
    query = query.filter(
        Incident.reported_at < date.today().replace(day=1) + relativedelta(months=-2)
    )

    if incident_type != "all":
        if incident_type:
            query = query.filter(IncidentType.name == incident_type)

    if grouping == "month":
        grouper = month_grouper
        query.filter(Incident.reported_at > date.today() + relativedelta(months=-periods))

    incidents = query.all()
    incidents_sorted = sorted(incidents, key=grouper)

    dataframe_dict = {"ds": [], "y": []}

    for (last_day, items) in groupby(incidents_sorted, grouper):
        dataframe_dict["ds"].append(str(last_day))
        dataframe_dict["y"].append(len(list(items)))

    dataframe = pd.DataFrame.from_dict(dataframe_dict)

    if dataframe.empty:
        return {
            "categories": [],
            "series": [{"name": "Predicted", "data": []}],
        }

    # reset index to by month and drop month column
    dataframe.index = dataframe.ds
    dataframe.index.freq = "M"
    dataframe.drop("ds", inplace=True, axis=1)

    # fill periods without incidents with 0
    idx = pd.date_range(dataframe.index[0], dataframe.index[-1], freq="M")
    dataframe = dataframe.reindex(idx, fill_value=0)

    try:
        forecaster = ExponentialSmoothing(
            dataframe, seasonal_periods=12, trend="add", seasonal="add"
        ).fit(use_boxcox=True)
    except Exception as e:
        log.error(f"Issue forecasting incidents: {e}")
        return {
            "categories": [],
            "series": [{"name": "Predicted", "data": []}],
        }

    forecast = forecaster.forecast(12)
    forecast_df = pd.DataFrame({"ds": forecast.index.astype("str"), "yhat": forecast.values})

    forecast_data = forecast_df.to_dict("series")

    # drop day data
    categories = [d[:-3] for d in forecast_data["ds"]]

    incident_counts = get_incident_counts(db_session=db_session)

    return {
        "categories": categories,
        "series": [
            {
                "name": "Predicted",
                "data": [max(math.ceil(x), 0) for x in list(forecast_data["yhat"])],
            },
            {"name": "Actual", "data": incident_counts},
        ],
    }
