import csv
import tempfile
from enum import Enum
from typing import List, Any

from dispatch.database import resolve_attr


class ExportTypes(str, Enum):
    csv = "csv"


def export_items(
    items: List[Any], export_type: str = ExportTypes.csv, export_fields: List[str] = ["id"]
):
    """Pulls fields from items and then exports them according to type."""
    filtered_items = []
    for i in items:
        filtered_items.append([resolve_attr(i, x) for x in export_fields])

    export_file = tempfile.TemporaryFile()
    if export_type == ExportTypes.csv:
        writer = csv.writer(export_file)
        for i in filtered_items:
            writer.writerow(i)
    return export_file
