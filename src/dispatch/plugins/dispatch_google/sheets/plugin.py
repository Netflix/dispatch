"""
.. module: dispatch.plugins.dispatch_google_sheets.plugin
    :platform: Unix
    :copyright: (c) 2022 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import json
from typing import Optional
from pydantic import Field
from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import SignalConsumerPlugin
from dispatch.plugins.dispatch_google import sheets as google_sheets_plugin
from dispatch.plugins.dispatch_google.common import get_service
from dispatch.plugins.dispatch_google.config import GoogleConfiguration


class GoogleSheetSignalConfiguration(GoogleConfiguration):
    spreadsheet_id: str = Field(
        title="Spreadsheet ID",
        description="Spreadsheet to fetch signals from.",
    )
    worksheet_name: str = Field(
        title="Worksheet Name",
        description="The name of the worksheet within the spreadsheet to fetch signals from.",
    )
    worksheet_range: str = Field(
        title="Worksheet Range", description="The worksheet range to consume.", default="A1:ZZ"
    )
    name_column: Optional[str] = Field(
        title="Name Column", description="Column name that will be used as the signal name."
    )
    filters: str = Field(
        title="Filters",
        description="Filters to apply before a signal is gathered. Format: {'columnName': ['allowValue1', 'allowedValue2']}",
    )


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class GoogleSheetsSignalConsumerPlugin(SignalConsumerPlugin):
    title = "Google Sheet Plugin - Signal Consumer"
    slug = "google-sheets-signal-consumer"
    description = "Uses Google sheets as a source for new signals."
    version = google_sheets_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = GoogleSheetSignalConfiguration
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
        ]

    def consume(self, **kwargs):
        """Fetches a google sheet and gathers signals."""
        kwargs = {"{{" + k + "}}": v for k, v in kwargs.items()}
        client = get_service(self.configuration, "sheets", "v4", self.scopes).spreadsheets()
        result = (
            client.values()
            .get(
                spreadsheetId=self.configuration.spreadsheet_id,
                range=f"{self.configuration.worksheet_name}!{self.configuration.worksheet_range}",
            )
            .execute()
        )
        filters = json.loads(self.configuration.filters)

        values = result.get("values", [])
        headers = values[0]
        rows = values[1:]

        signals = []
        for row in rows:
            row_dict = {}
            for key, row_value in zip(headers, row):
                row_dict[key] = row_value

            for k, v in filters.items():
                if row_dict.get(k) in v:
                    signals.append(
                        {
                            "name": row_dict.get(self.configuration.name_column),
                            "external_url": f"https://docs.google.com/spreadsheets/d/{self.configuration.spreadsheet_id}/edit",
                            "external_id": self.configuration.spreadsheet_id,
                            "raw": row_dict,
                        }
                    )
        return signals
