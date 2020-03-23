from fbprophet import Prophet
import pandas as pd
import numpy as np

from .service import get_all, get_all_by_incident_type


def make_forecast(
    db_session, incident_type: str = None, periods: int = 24, grouping: str = "month"
):
    """Makes an incident forecast."""

    if not incident_type:
        incidents = get_all(db_session=db_session).all()
    else:
        incidents = get_all_by_incident_type(db_session=db_session, incident_type=incident_type)

    if grouping == "month":
        incident_data = [x.reported_at.month for x in incidents]

    forecaster = Prophet()
    future = forecaster.make_future_dataframe(periods=periods, freq="M")

    regressions = {"content_cost": "", "employee_count": ""}
    for k, v in regressions.items():
        forecaster.add_regressor(k)
        incidents_by_month[k] = v

    forecaster.fit(incidents_by_month, algorithm="LBFGS")
    forecast = forecaster.predict(future)

    return forecast
