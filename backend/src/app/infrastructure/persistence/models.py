from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, Index, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class RewriteMetadataBase(DeclarativeBase):
    pass


class RewriteStorageRecord(RewriteMetadataBase):
    __tablename__ = "rewrite_storage_records"
    __table_args__ = (
        Index("ix_rewrite_storage_records_record_type", "record_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_type: Mapped[str] = mapped_column(String(32), nullable=False)
    record_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.current_timestamp(),
    )


class RewriteTracePayloadRecord(RewriteMetadataBase):
    __tablename__ = "rewrite_trace_payloads"
    __table_args__ = (
        Index("ix_rewrite_trace_payloads_payload_role", "payload_role"),
        Index("ix_rewrite_trace_payloads_store_key", "store_key", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_record_id: Mapped[int] = mapped_column(
        ForeignKey("rewrite_storage_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    contract_version: Mapped[str] = mapped_column(String(32), nullable=False)
    backend: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_role: Mapped[str] = mapped_column(String(32), nullable=False)
    store_key: Mapped[str] = mapped_column(String(255), nullable=False)
    store_uri: Mapped[str | None] = mapped_column(String(255))
    group_path: Mapped[str] = mapped_column(String(255), nullable=False)
    array_path: Mapped[str] = mapped_column(String(255), nullable=False)
    dtype: Mapped[str] = mapped_column(String(32), nullable=False)
    shape: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    chunk_shape: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    writer_version: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.current_timestamp(),
    )


class RewriteResultHandleRecord(RewriteMetadataBase):
    __tablename__ = "rewrite_result_handles"
    __table_args__ = (
        Index("ix_rewrite_result_handles_kind", "kind"),
        Index("ix_rewrite_result_handles_handle_id", "handle_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    metadata_record_id: Mapped[int] = mapped_column(
        ForeignKey("rewrite_storage_records.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    handle_id: Mapped[str] = mapped_column(String(128), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(32), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_backend: Mapped[str | None] = mapped_column(String(64))
    payload_format: Mapped[str | None] = mapped_column(String(32))
    payload_role: Mapped[str | None] = mapped_column(String(32))
    payload_locator: Mapped[str | None] = mapped_column(String(255))
    provenance_task_id: Mapped[int | None]
    source_dataset_id: Mapped[str | None] = mapped_column(String(128))
    source_task_id: Mapped[int | None]
    trace_batch_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("rewrite_storage_records.id", ondelete="SET NULL"),
    )
    analysis_run_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("rewrite_storage_records.id", ondelete="SET NULL"),
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.current_timestamp(),
    )


class RewriteTaskRecord(RewriteMetadataBase):
    __tablename__ = "rewrite_task_records"
    __table_args__ = (
        Index("ix_rewrite_task_records_task_id", "task_id", unique=True),
        Index("ix_rewrite_task_records_workspace_id", "workspace_id"),
        Index("ix_rewrite_task_records_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    lane: Mapped[str] = mapped_column(String(32), nullable=False)
    execution_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    submitted_at: Mapped[str] = mapped_column(String(32), nullable=False)
    owner_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    owner_display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    workspace_id: Mapped[str] = mapped_column(String(64), nullable=False)
    workspace_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    visibility_scope: Mapped[str] = mapped_column(String(32), nullable=False)
    dataset_id: Mapped[str | None] = mapped_column(String(128))
    definition_id: Mapped[int | None]
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    queue_backend: Mapped[str] = mapped_column(String(64), nullable=False)
    worker_task_name: Mapped[str] = mapped_column(String(64), nullable=False)
    request_ready: Mapped[bool] = mapped_column(nullable=False, default=False)
    submitted_from_active_dataset: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )
    progress_phase: Mapped[str] = mapped_column(String(32), nullable=False)
    progress_percent_complete: Mapped[int] = mapped_column(nullable=False)
    progress_summary: Mapped[str] = mapped_column(String(255), nullable=False)
    progress_updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.current_timestamp(),
    )


class RewriteTaskDispatchRecord(RewriteMetadataBase):
    __tablename__ = "rewrite_task_dispatch_records"
    __table_args__ = (
        Index("ix_rewrite_task_dispatch_records_task_id", "task_id", unique=True),
        Index("ix_rewrite_task_dispatch_records_dispatch_key", "dispatch_key", unique=True),
        Index("ix_rewrite_task_dispatch_records_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("rewrite_task_records.task_id", ondelete="CASCADE"),
        nullable=False,
    )
    dispatch_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    submission_source: Mapped[str] = mapped_column(String(32), nullable=False)
    accepted_at: Mapped[str] = mapped_column(String(32), nullable=False)
    last_updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.current_timestamp(),
    )
