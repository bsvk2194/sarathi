"""
Gmail Plugin for SARATHI.
"""

import base64
from email.mime.text import MIMEText

from core.plugins.base import Plugin
from plugins.google.client import google_client


class GmailPlugin(Plugin):

    id = "gmail"

    name = "Gmail Plugin"

    version = "1.0.0"

    description = "Provides Gmail operations through Google APIs."

    permissions = [
        "internet"
    ]

    def execute(self, request):

        account_id = request.parameters.get(
            "account_id",
            "google_personal"
        )

        gmail = google_client.service(
            "gmail",
            "v1",
            account_id
        )

        if request.action == "list_emails":

            max_results = request.parameters.get(
                "max_results",
                10
            )

            response = (
                gmail.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=max_results
                )
                .execute()
            )

            messages = response.get(
                "messages",
                []
            )

            results = []

            for message in messages:

                message_data = (
                    gmail.users()
                    .messages()
                    .get(
                        userId="me",
                        id=message["id"],
                        format="metadata",
                        metadataHeaders=[
                            "From",
                            "To",
                            "Subject",
                            "Date"
                        ]
                    )
                    .execute()
                )

                headers = {
                    header["name"]: header["value"]
                    for header
                    in message_data
                    .get("payload", {})
                    .get("headers", [])
                }

                results.append(
                    {
                        "id": message["id"],
                        "from": headers.get("From"),
                        "to": headers.get("To"),
                        "subject": headers.get("Subject"),
                        "date": headers.get("Date")
                    }
                )

            return results

        if request.action == "read_email":

            message_id = request.parameters.get(
                "message_id"
            )

            if not message_id:

                raise ValueError(
                    "message_id is required."
                )

            message = (
                gmail.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="full"
                )
                .execute()
            )

            return message

        if request.action == "send_email":

            to = request.parameters.get("to")
            subject = request.parameters.get(
                "subject",
                ""
            )
            body = request.parameters.get(
                "body",
                ""
            )

            if not to:

                raise ValueError(
                    "Recipient 'to' is required."
                )

            message = MIMEText(body)

            message["to"] = to
            message["subject"] = subject

            encoded_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode()

            sent_message = (
                gmail.users()
                .messages()
                .send(
                    userId="me",
                    body={
                        "raw": encoded_message
                    }
                )
                .execute()
            )

            return sent_message

        raise ValueError(
            f"Unknown Gmail action: {request.action}"
        )