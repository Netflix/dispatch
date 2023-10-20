import os
from datetime import datetime
import pandas as pd
from slack_sdk import WebClient
from collections import defaultdict
from typing import Optional

# from dispatch.plugin_event.dispatch_slack.plugin import get_slack_history
from .models import (
    IncidentCostModelActivity,
    IncidentCostModelActivityCreate,
    IncidentCostModelActivityUpdate,
    IncidentCostModelActivityRead,
)


def get_by_id(*, db_session, incident_cost_model_activity_id: int) -> IncidentCostModelActivity:
    """Returns an incident cost model based on the given incident cost model id."""
    return (
        db_session.query(IncidentCostModelActivity)
        .filter(IncidentCostModelActivity.id == incident_cost_model_activity_id)
        .one()
    )


def delete(*, db_session, incident_cost_model_activity_id: int):
    """Deletes an incident cost model activity."""
    incident_cost_model_activity = get_by_id(
        db_session=db_session, incident_cost_model_activity_id=incident_cost_model_activity_id
    )
    db_session.delete(incident_cost_model_activity)
    db_session.commit()


def update(*, db_session, incident_cost_model_activity_in: IncidentCostModelActivityUpdate):
    """Updates an incident cost model activity."""
    incident_cost_model_activity = IncidentCostModelActivity(
        response_time_seconds=incident_cost_model_activity_in.response_time_seconds,
        enabled=incident_cost_model_activity_in.enabled,
        event_id=incident_cost_model_activity_in.event.id,
    )

    incident_cost_model_activity.response_time_seconds = (
        incident_cost_model_activity_in.response_time_seconds
    )
    incident_cost_model_activity.enabled = incident_cost_model_activity_in.enabled
    incident_cost_model_activity.event_id = incident_cost_model_activity_in.event.id

    db_session.commit()
    return incident_cost_model_activity


def create_cost_model_activity(
    *, db_session, incident_cost_model_activity_in: IncidentCostModelActivityCreate
) -> IncidentCostModelActivity:
    incident_cost_model_activity = IncidentCostModelActivity(
        response_time_seconds=incident_cost_model_activity_in.response_time_seconds,
        enabled=incident_cost_model_activity_in.enabled,
        event_id=incident_cost_model_activity_in.event.id,
    )

    db_session.add(incident_cost_model_activity)
    db_session.commit()
    return incident_cost_model_activity


# do we move this to the cost model?
# TODO(averyl): make timestamps a list of IncidentUserActivityRead... we cannot due to circular dependency with particpant (project)...
# We can probably fix this by moving it to incident_cost?
def calculate_timestamps(activity: IncidentCostModelActivityRead, user_activities: list) -> float:
    response_time_seconds = activity.response_time_seconds
    total_time = 0
    last_timestamp = 0
    for user_activity in user_activities:
        # init
        if last_timestamp == 0:
            last_timestamp = user_activity
        # more than five minutes has elapsed since the last message. add 5 minutes to the total time and start anew.
        elif user_activity - last_timestamp > response_time_seconds:
            total_time += response_time_seconds
        # continuous activity
        else:
            total_time += user_activity - last_timestamp  # aggregate the total hours spent
        # update the timestamp
        last_timestamp = user_activity

    total_time += response_time_seconds

    # return in minutes for legibility
    return round(total_time / 60, 2)


# TODO(averyl): move the setup activity to plugin_event/dispatch_slack?
# we could also abstract this out.
# input: last_update
# return: make dispatch_slack return a list of (user, started_at, ended_at=started_at, plugin_event)
# actually, i think this needs to move to incident_cost. we'll need to update ended_up timestamps during our next poll.
# def analyze_slack_activity():
#     # initial setup
#     channel = "C05UCN2QBRT"  # inc-3438
#     client = WebClient(token=SLACK_BOT_TOKEN)

#     if not client:
#         print("error initializing slack client")
#         return

#     # {user_id: list(message_timestamps)}
#     user_activity = defaultdict(list)
#     get_slack_history(client, channel, user_activity)
#     result = defaultdict(list)

#     # aggregate the user info
#     for user in user_activity:
#         # TODO(averyl): collect the user_id?
#         user_activity[user] = sorted(user_activity[user])
#         response = client.users_profile_get(user=user)
#         if response["ok"] and "profile" in response:
#             # filter out bots
#             if "bot_id" in response["profile"]:
#                 continue
#             # for legibility
#             real_name = (
#                 response["profile"]["real_name"] if "real_name" in response["profile"] else user
#             )
#             result["Name"] += [real_name]
#         else:
#             print(f"Error retrieving profile for user: {user}")
#             result["Name"] += [user]

#         result["Engagement Time (min)"] += [calculate_timestamps(user_activity[user])]

#     df = pd.DataFrame(result)
#     print(str(df))
#     df.to_csv("/Users/averyl/Desktop/inc3438_engagement.csv")
#     print(f"Total time spent: {df['Engagement Time (min)'].sum()} minutes")
#     return df
