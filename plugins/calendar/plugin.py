"""
Google Calendar Plugin for SARATHI.
"""

from core.plugins.base import Plugin
from plugins.google.client import google_client


class CalendarPlugin(Plugin):

    id = "calendar"

    name = "Calendar Plugin"

    version = "1.0.0"

    description = (
        "Provides Google Calendar operations "
        "through Google APIs."
    )

    permissions = [
        "internet"
    ]

    def execute(self, request):

        account_id = request.parameters.get(
            "account_id",
            "google_personal"
        )

        calendar = google_client.service(
            "calendar",
            "v3",
            account_id
        )

        if request.action == "list_events":

            max_results = request.parameters.get(
                "max_results",
                10
            )

            response = (
                calendar.events()
                .list(
                    calendarId="primary",
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime"
                )
                .execute()
            )

            events = response.get(
                "items",
                []
            )

            results = []

            for event in events:

                results.append(
                    {
                        "id": event.get("id"),
                        "summary": event.get(
                            "summary",
                            "No title"
                        ),
                        "start": event.get(
                            "start",
                            {}
                        ),
                        "end": event.get(
                            "end",
                            {}
                        ),
                        "status": event.get(
                            "status"
                        )
                    }
                )

            return results

        if request.action == "create_event":

            summary = request.parameters.get(
                "summary"
            )

            start = request.parameters.get(
                "start"
            )

            end = request.parameters.get(
                "end"
            )

            if not summary:

                raise ValueError(
                    "summary is required."
                )

            if not start:

                raise ValueError(
                    "start is required."
                )

            if not end:

                raise ValueError(
                    "end is required."
                )

            event = {
                "summary": summary,
                "start": start,
                "end": end
            }

            created_event = (
                calendar.events()
                .insert(
                    calendarId="primary",
                    body=event
                )
                .execute()
            )

            return created_event

        raise ValueError(
            f"Unknown Calendar action: {request.action}"
        )