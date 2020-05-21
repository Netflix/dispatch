from enum import Enum


class ReportTypes(str, Enum):
    status_report = "Status Report"
    incident_report = "Incident Report"
