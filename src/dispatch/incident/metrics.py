import json
import math
import logging
from itertools import groupby

from datetime import date
from dateutil.relativedelta import relativedelta

from calendar import monthrange

from dispatch.config import INCIDENT_METRIC_FORECAST_REGRESSIONS
from dispatch.incident_type.models import IncidentType
from .models import Incident


log = logging.getLogger(__name__)

try:
    from fbprophet import Prophet
    import pandas as pd
except ImportError:
    log.warning("Unable to import fbprophet, some metrics will not be usable.")


def month_grouper(item):
    """Determines the last day of a given month."""
    key = date(
        item.reported_at.year,
        item.reported_at.month,
        monthrange(item.reported_at.year, item.reported_at.month)[-1],
    )
    return key


def make_forecast(
    db_session, incident_type: str = None, periods: int = 24, grouping: str = "month"
):
    """Makes an incident forecast."""
    query = db_session.query(Incident).join(IncidentType)

    # exclude simulations
    query = query.filter(IncidentType.name != "Simulation")

    # exclude current month
    query = query.filter(Incident.reported_at < date.today().replace(day=1))

    if incident_type != "all":
        if incident_type:
            query = query.filter(IncidentType.name == incident_type)

    if grouping == "month":
        grouper = month_grouper
        query.filter(Incident.reported_at > date.today() + relativedelta(months=-periods))

    incidents = query.all()
    incidents_sorted = sorted(incidents, key=grouper)

    # TODO ensure there are no missing periods (e.g. periods with no incidents)
    dataframe_dict = {"ds": [], "y": []}

    regression_keys = []
    if INCIDENT_METRIC_FORECAST_REGRESSIONS:
        # assumes json file with key as column and list of values
        regression_data = json.loads(INCIDENT_METRIC_FORECAST_REGRESSIONS)
        regression_keys = regression_data.keys()
        dataframe_dict.update(regression_data)

    for (last_day, items) in groupby(incidents_sorted, grouper):
        dataframe_dict["ds"].append(str(last_day))
        dataframe_dict["y"].append(len(list(items)))

    dataframe = pd.DataFrame.from_dict(dataframe_dict)

    forecaster = Prophet()

    for r in regression_keys:
        forecaster.add_regressor(r)

    forecaster.fit(dataframe, algorithm="LBFGS")

    # https://facebook.github.io/prophet/docs/quick_start.html#python-api
    future = forecaster.make_future_dataframe(periods=periods, freq="M")
    forecast = forecaster.predict(future)

    forecast_data = forecast.to_dict("series")

    return {
        "categories": list(forecast_data["ds"]),
        "series": [
            {
                "name": "Upper",
                "data": [max(math.ceil(x), 0) for x in list(forecast_data["yhat_upper"])],
            },
            {
                "name": "Predicted",
                "data": [max(math.ceil(x), 0) for x in list(forecast_data["yhat"])],
            },
            {
                "name": "Lower",
                "data": [max(math.ceil(x), 0) for x in list(forecast_data["yhat_lower"])],
            },
        ],
    }
