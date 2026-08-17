"""
Account Model for SARATHI.

Represents a user account connected to a plugin.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Account:

    account_id: str

    plugin_id: str

    display_name: str

    identifier: str | None = None

    status: str = "connected"

    metadata: dict = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=datetime.now
    )

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    def is_connected(self):

        return self.status == "connected"

    def disconnect(self):

        self.status = "disconnected"

        self.updated_at = datetime.now()

    def connect(self):

        self.status = "connected"

        self.updated_at = datetime.now()