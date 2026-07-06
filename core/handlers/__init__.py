from .storage import (
    handle_latest_note,
    handle_storage_status,
    handle_backup_count,
)
from .tasks import (
    handle_pending_tasks,
    handle_complete_task,
    handle_complete_task_by_id,
    handle_add_task
)
from .notes import (
    handle_search_notes,
    handle_add_note
)
from .events import (
    handle_upcoming_events,
    handle_add_event
)
from .backups import (
    handle_create_backup
)
from .chat import (
    handle_general_chat
)