import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SessionTracker:
    """Tracks database session lifecycle events."""

    _sessions: dict[str, dict[str, Any]] = {}

    @classmethod
    def track_session(cls, session: Session, context: str | None = None) -> str:
        """Tracks a new database session."""
        session_id = str(uuid.uuid4())
        cls._sessions[session_id] = {
            "session": session,
            "context": context,
            "created_at": datetime.now().timestamp(),
        }
        logger.info(
            "Database session created",
            extra={
                "session_id": session_id,
                "context": context,
                "total_active_sessions": len(cls._sessions),
            },
        )
        return session_id

    @classmethod
    def untrack_session(cls, session_id: str) -> None:
        """Untracks a database session."""
        if session_id in cls._sessions:
            session_info = cls._sessions.pop(session_id)
            duration = datetime.now().timestamp() - session_info["created_at"]
            logger.info(
                "Database session closed",
                extra={
                    "session_id": session_id,
                    "context": session_info["context"],
                    "duration_seconds": duration,
                    "total_active_sessions": len(cls._sessions),
                },
            )

    @classmethod
    def get_active_sessions(cls) -> list[dict[str, Any]]:
        """Returns information about all active sessions."""
        current_time = datetime.now().timestamp()
        return [
            {
                "session_id": session_id,
                "context": info["context"],
                "age_seconds": current_time - info["created_at"],
            }
            for session_id, info in cls._sessions.items()
        ]
