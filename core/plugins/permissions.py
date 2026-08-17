"""
Plugin Permissions for SARATHI.
"""

from enum import Enum


class Permission(Enum):

    INTERNET = "internet"

    FILESYSTEM = "filesystem"

    EMAIL = "email"

    CALENDAR = "calendar"

    LOCATION = "location"

    MICROPHONE = "microphone"

    CAMERA = "camera"

    AUDIO = "audio"

    NOTIFICATIONS = "notifications"

    CONTACTS = "contacts"