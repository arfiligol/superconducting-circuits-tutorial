"""Repository for AuditLogRecord operations."""

from __future__ import annotations

from typing import Any

from sqlalchemy import desc
from sqlmodel import Session, col, select

from core.shared.persistence.models import AuditLogRecord


class AuditLogRepository:
    """Repository for actor-scoped audit log rows."""

    def __init__(self, session: Session):
        self._session = session

    def append_log(
        self,
        *,
        actor_id: int | None,
        action_kind: str,
        resource_kind: str,
        resource_id: str | int,
        summary: str,
        payload: dict[str, Any] | None = None,
    ) -> AuditLogRecord:
        """Append and flush one audit log row."""
        log = AuditLogRecord(
            actor_id=actor_id,
            action_kind=action_kind,
            resource_kind=resource_kind,
            resource_id=str(resource_id),
            summary=summary,
            payload=dict(payload or {}),
        )
        self._session.add(log)
        self._session.flush()
        return log

    def list_logs(self) -> list[AuditLogRecord]:
        """List audit logs newest first."""
        statement = select(AuditLogRecord).order_by(
            desc(col(AuditLogRecord.created_at)),
            desc(col(AuditLogRecord.id)),
        )
        return list(self._session.exec(statement).all())

    def list_logs_by_actor(self, actor_id: int) -> list[AuditLogRecord]:
        """List audit logs for one actor, newest first."""
        statement = (
            select(AuditLogRecord)
            .where(col(AuditLogRecord.actor_id) == actor_id)
            .order_by(
                desc(col(AuditLogRecord.created_at)),
                desc(col(AuditLogRecord.id)),
            )
        )
        return list(self._session.exec(statement).all())
