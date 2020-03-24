from itertools import groupby

from datetime import date
from calendar import monthrange

from fbprophet import Prophet
import pandas as pd

from .models import Incident
from dispatch.incident_type.models import IncidentType


def make_forecast(
    db_session, incident_type: str = None, periods: int = 24, grouping: str = "month"
):
    """Makes an incident forecast."""
    # filter out all simulations, exclude current month

    query = db_session.query(Incident).join(IncidentType)

    # exclude simulations
    query = query.filter(IncidentType.name != "Simulation")

    if incident_type:
        query = query.filter(IncidentType.name == incident_type)

    incidents = query.all()

    def grouper(item):
        key = date(
            item.reported_at.year,
            item.reported_at.month,
            monthrange(item.reported_at.year, item.reported_at.month)[-1],
        )
        return key

    incidents_sorted = sorted(incidents, key=grouper)

    dataframe_dict = {"ds": [], "y": []}
    for (last_day, items) in groupby(incidents_sorted, grouper):
        dataframe_dict["ds"].append(last_day)
        dataframe_dict["y"].append(len(list(items)))

    dataframe = pd.DataFrame.from_dict(dataframe_dict)

    forecaster = Prophet()
    forecaster.fit(dataframe, algorithm="LBFGS")

    future = forecaster.make_future_dataframe(periods=2, freq="M")

    forecast = forecaster.predict(future)

    return forecast
