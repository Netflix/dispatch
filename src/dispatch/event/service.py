from typing import Optional
from uuid import uuid4
import datetime
import logging
import json
import pytz

from dispatch.auth import service as auth_service
from dispatch.case import service as case_service
from dispatch.incident import service as incident_service
from dispatch.individual import service as individual_service
from dispatch.enums import EventType
from dispatch.incident.models import Incident
from dispatch.types import Subject

from .models import Event, EventCreate, EventUpdate
from dispatch.document import service as document_service
from dispatch.plugin import service as plugin_service

log = logging.getLogger(__name__)


def get(*, db_session, event_id: int) -> Optional[Event]:
    """Get an event by id."""
    return (
        db_session.query(Event)
        .filter(Event.id == event_id)
        .order_by(Event.started_at)
        .one_or_none()
    )


def get_by_case_id(*, db_session, case_id: int) -> list[Event | None]:
    """Get events by case id."""
    return db_session.query(Event).filter(Event.case_id == case_id)


def get_by_incident_id(*, db_session, incident_id: int) -> list[Event | None]:
    """Get events by incident id."""

    return (
        db_session.query(Event).filter(Event.incident_id == incident_id).order_by(Event.started_at)
    )


def get_by_uuid(*, db_session, uuid: str) -> list[Event | None]:
    """Get events by uuid."""
    return db_session.query(Event).filter(Event.uuid == uuid).one_or_none()


def get_all(*, db_session) -> list[Event | None]:
    """Get all events."""
    return db_session.query(Event)


def create(*, db_session, event_in: EventCreate) -> Event:
    """Create a new event."""
    event = Event(**event_in.dict())
    db_session.add(event)
    db_session.commit()
    return event


def update(*, db_session, event: Event, event_in: EventUpdate) -> Event:
    """Updates an event."""
    event_data = event.dict()
    update_data = event_in.dict(skip_defaults=True)

    for field in event_data:
        if field in update_data:
            setattr(event, field, update_data[field])

    db_session.commit()
    return event


def delete(*, db_session, event_id: int):
    """Deletes an event."""
    event = db_session.query(Event).filter(Event.id == event_id).first()
    db_session.delete(event)
    db_session.commit()


def log_subject_event(subject: Subject, **kwargs) -> Event:
    if isinstance(subject, Incident):
        return log_incident_event(incident_id=subject.id, **kwargs)
    else:
        return log_case_event(case_id=subject.id, **kwargs)


def log_incident_event(
    db_session,
    source: str,
    description: str,
    incident_id: int,
    individual_id: int = None,
    started_at: datetime = None,
    ended_at: datetime = None,
    details: dict = None,
    type: str = EventType.other,
    owner: str = "",
    pinned: bool = False,
) -> Event:
    """Logs an event in the incident timeline."""
    uuid = uuid4()

    if not started_at:
        started_at = datetime.datetime.utcnow()

    if not ended_at:
        ended_at = started_at

    event_in = EventCreate(
        uuid=uuid,
        started_at=started_at,
        ended_at=ended_at,
        source=source,
        description=description,
        details=details,
        type=type,
        owner=owner,
        pinned=pinned,
    )
    event = create(db_session=db_session, event_in=event_in)

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    incident.events.append(event)
    db_session.add(incident)

    if individual_id:
        individual = individual_service.get(
            db_session=db_session, individual_contact_id=individual_id
        )
        individual.events.append(event)
        db_session.add(individual)

    db_session.commit()

    return event


def log_case_event(
    db_session,
    source: str,
    description: str,
    case_id: int,
    dispatch_user_id: int = None,
    started_at: datetime = None,
    ended_at: datetime = None,
    details: dict = None,
    type: str = EventType.other,
) -> Event:
    """Logs an event in the case timeline."""
    uuid = uuid4()

    if not started_at:
        started_at = datetime.datetime.utcnow()

    if not ended_at:
        ended_at = started_at

    event_in = EventCreate(
        uuid=uuid,
        started_at=started_at,
        ended_at=ended_at,
        source=source,
        description=description,
        details=details,
        type=type,
    )
    event = create(db_session=db_session, event_in=event_in)

    case = case_service.get(db_session=db_session, case_id=case_id)
    case.events.append(event)
    db_session.add(case)

    if dispatch_user_id:
        dispatch_user = auth_service.get(db_session=db_session, user_id=dispatch_user_id)
        dispatch_user.events.append(event)
        db_session.add(dispatch_user)

    db_session.commit()

    return event


def update_incident_event(
    db_session,
    event_in: EventUpdate,
) -> Event:
    """Updates an event in the incident timeline."""
    event = get_by_uuid(db_session=db_session, uuid=event_in.uuid)
    event = update(db_session=db_session, event=event, event_in=event_in)

    return event


def delete_incident_event(
    db_session,
    uuid: str,
):
    """Deletes an event."""
    event = get_by_uuid(db_session=db_session, uuid=uuid)

    delete(db_session=db_session, event_id=event.id)


def export_timeline(
    db_session,
    timeline_filters: str,
    incident_id: int,
):
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project_id, plugin_type="document"
    )
    if not plugin:
        log.error("Document not created. No storage plugin enabled.")
        return False

    """gets timeline events for incident"""
    event = get_by_incident_id(db_session=db_session, incident_id=incident_id)
    table_data = []
    dates = set()
    data_inserted = False

    """Filters events based on user filter"""
    for e in event.all():
        time_header = "Time (UTC)"
        event_timestamp = e.started_at.strftime("%Y-%m-%d %H:%M:%S")
        if not e.owner:
            e.owner = "Dispatch"
        if timeline_filters.get("timezone").strip() == "America/Los_Angeles":
            time_header = "Time (PST/PDT)"
            event_timestamp = (
                pytz.utc.localize(e.started_at)
                .astimezone(pytz.timezone(timeline_filters.get("timezone").strip()))
                .replace(tzinfo=None)
                .strftime("%Y-%m-%d %H:%M:%S")
            )
        date, time = str(event_timestamp).split(" ")
        if e.pinned or timeline_filters.get(e.type):
            if date in dates:
                if timeline_filters.get("exportOwner"):
                    table_data.append(
                        {time_header: time, "Description": e.description, "Owner": e.owner}
                    )
                else:
                    table_data.append({time_header: time, "Description": e.description})
            else:
                dates.add(date)
                if timeline_filters.get("exportOwner"):
                    table_data.append({time_header: date, "Description": "\t", "Owner": "\t"})
                    table_data.append(
                        {time_header: time, "Description": e.description, "Owner": e.owner}
                    )
                else:
                    table_data.append({time_header: date, "Description": "\t"})
                    table_data.append({time_header: time, "Description": e.description})

    if table_data:
        table_data = json.loads(json.dumps(table_data))
        num_columns = len(table_data[0].keys() if table_data else [])
        column_headers = table_data[0].keys()

        documents_list = []
        if timeline_filters.get("incidentDocument"):
            documents = document_service.get_by_incident_id_and_resource_type(
                db_session=db_session,
                incident_id=incident_id,
                project_id=incident.project.id,
                resource_type="dispatch-incident-document",
            )
            if documents:
                documents_list.append(documents.resource_id)

        if timeline_filters.get("reviewDocument"):
            documents = document_service.get_by_incident_id_and_resource_type(
                db_session=db_session,
                incident_id=incident_id,
                project_id=incident.project.id,
                resource_type="dispatch-incident-review-document",
            )
            if documents:
                documents_list.append(documents.resource_id)

        for doc_id in documents_list:
            # Checks for existing table in the document
            table_exists, curr_table_start, curr_table_end, _ = plugin.instance.get_table_details(
                document_id=doc_id, header="Timeline"
            )

            # Deletes existing table
            if table_exists:
                delete_table_request = [
                    {
                        "deleteContentRange": {
                            "range": {
                                "segmentId": "",
                                "startIndex": curr_table_start,
                                "endIndex": curr_table_end,
                            }
                        }
                    }
                ]
                if plugin.instance.delete_table(document_id=doc_id, request=delete_table_request):
                    log.debug("Existing table in the doc has been deleted")

            else:
                curr_table_start += 1
            # Insert new table with required rows & columns
            insert_table_request = [
                {
                    "insertTable": {
                        "rows": len(table_data) + 1,
                        "columns": num_columns,
                        "location": {"index": curr_table_start - 1},
                    }
                }
            ]
            if plugin.instance.insert(document_id=doc_id, request=insert_table_request):
                log.debug("Table skeleton inserted successfully")

            else:
                return False

            # Formatting & inserting empty table
            insert_data_request = [
                {
                    "updateTableCellStyle": {
                        "tableCellStyle": {
                            "backgroundColor": {
                                "color": {"rgbColor": {"green": 0.4, "red": 0.4, "blue": 0.4}}
                            }
                        },
                        "fields": "backgroundColor",
                        "tableRange": {
                            "columnSpan": num_columns,
                            "rowSpan": 1,
                            "tableCellLocation": {
                                "columnIndex": 0,
                                "rowIndex": 0,
                                "tableStartLocation": {"index": curr_table_start},
                            },
                        },
                    }
                },
                {
                    "updateTableColumnProperties": {
                        "tableStartLocation": {
                            "index": curr_table_start,
                        },
                        "columnIndices": [0],
                        "tableColumnProperties": {
                            "width": {"magnitude": 90, "unit": "PT"},
                            "widthType": "FIXED_WIDTH",
                        },
                        "fields": "width,widthType",
                    }
                }
            ]

            if timeline_filters.get("exportOwner"):
                insert_data_request.append(
                    {
                        "updateTableColumnProperties": {
                            "tableStartLocation": {
                                "index": curr_table_start,
                            },
                            "columnIndices": [2],
                            "tableColumnProperties": {
                                "width": {"magnitude": 105, "unit": "PT"},
                                "widthType": "FIXED_WIDTH",
                            },
                            "fields": "width,widthType",
                        }
                    }
                )

            if plugin.instance.insert(document_id=doc_id, request=insert_data_request):
                log.debug("Table Formatted successfully")

            else:
                return False

            # Calculating table cell indices
            _, _, _, cell_indices = plugin.instance.get_table_details(
                document_id=doc_id, header="Timeline"
            )

            data_to_insert = list(column_headers) + [
                item for row in table_data for item in row.values()
            ]
            str_len = 0
            row_idx = 0
            insert_data_request = []
            for index, text in zip(cell_indices, data_to_insert, strict=True):
                # Adjusting index based on string length
                new_idx = index + str_len

                insert_data_request.append(
                    {"insertText": {"location": {"index": new_idx}, "text": text}}
                )

                # Header field formatting
                if text in column_headers:
                    insert_data_request.append(
                        {
                            "updateTextStyle": {
                                "range": {"startIndex": new_idx, "endIndex": new_idx + len(text)},
                                "textStyle": {
                                    "bold": True,
                                    "foregroundColor": {
                                        "color": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}
                                    },
                                    "fontSize": {"magnitude": 10, "unit": "PT"},
                                },
                                "fields": "bold,foregroundColor",
                            }
                        }
                    )

                # Formating for date rows
                if text == "\t":
                    insert_data_request.append(
                        {
                            "updateTableCellStyle": {
                                "tableCellStyle": {
                                    "backgroundColor": {
                                        "color": {
                                            "rgbColor": {"green": 0.8, "red": 0.8, "blue": 0.8}
                                        }
                                    }
                                },
                                "fields": "backgroundColor",
                                "tableRange": {
                                    "columnSpan": num_columns,
                                    "rowSpan": 1,
                                    "tableCellLocation": {
                                        "tableStartLocation": {"index": curr_table_start},
                                        "columnIndex": 0,
                                        "rowIndex": row_idx // len(column_headers),
                                    },
                                },
                            }
                        }
                    )

                # Formating for time column
                if row_idx % num_columns == 0:
                    insert_data_request.append(
                        {
                            "updateTextStyle": {
                                "range": {"startIndex": new_idx, "endIndex": new_idx + len(text)},
                                "textStyle": {
                                    "bold": True,
                                },
                                "fields": "bold",
                            }
                        }
                    )

                row_idx += 1
                str_len += len(text) if text else 0

            data_inserted = plugin.instance.insert(document_id=doc_id, request=insert_data_request)
        if not data_inserted:
            return False
    else:
        log.error("No timeline data to export")
        return False
    return True
