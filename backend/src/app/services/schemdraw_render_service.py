from __future__ import annotations

import ast
import html
from collections.abc import Mapping
from time import perf_counter
from typing import Protocol
from xml.etree import ElementTree

from src.app.domain.circuit_definitions import CircuitDefinitionRecord
from src.app.domain.schemdraw_render import (
    SchemdrawCursorPosition,
    SchemdrawDiagnostic,
    SchemdrawLinkedSchema,
    SchemdrawPreviewMetadata,
    SchemdrawProbePoint,
    SchemdrawRenderRequest,
    SchemdrawRenderResult,
)
from src.app.domain.session import SessionState
from src.app.services.service_errors import service_error


class SchemdrawDefinitionRepository(Protocol):
    def get_circuit_definition(self, definition_id: int) -> CircuitDefinitionRecord | None: ...


class SchemdrawSessionRepository(Protocol):
    def get_session_state(self) -> SessionState: ...


class SchemdrawRenderService:
    def __init__(
        self,
        *,
        definition_repository: SchemdrawDefinitionRepository,
        session_repository: SchemdrawSessionRepository,
    ) -> None:
        self._definition_repository = definition_repository
        self._session_repository = session_repository

    def render(self, request: SchemdrawRenderRequest) -> SchemdrawRenderResult:
        started_at = perf_counter()
        linked_schema = self._resolve_linked_schema(request.linked_schema)

        relation_diagnostics = _validate_relation_config(request.relation_config)
        if any(diagnostic.blocking for diagnostic in relation_diagnostics):
            return self._build_blocked_result(
                request=request,
                diagnostics=relation_diagnostics,
                render_time_ms=_elapsed_ms(started_at),
            )

        syntax_diagnostics, syntax_tree = _validate_python_source(request.source_text)
        if syntax_tree is None:
            return SchemdrawRenderResult(
                request_id=request.request_id,
                document_version=request.document_version,
                status="syntax_error",
                svg=None,
                diagnostics=syntax_diagnostics,
                cursor_position=_extract_cursor_position(request.relation_config),
                probe_points=_extract_probe_points(request.relation_config),
                render_time_ms=_elapsed_ms(started_at),
                preview_metadata=None,
            )

        runtime_diagnostics = _validate_render_entrypoint(syntax_tree)
        if any(diagnostic.blocking for diagnostic in runtime_diagnostics):
            return self._build_blocked_result(
                request=request,
                diagnostics=relation_diagnostics + runtime_diagnostics,
                render_time_ms=_elapsed_ms(started_at),
            )

        svg = _render_structural_svg(
            source_text=request.source_text,
            relation_config=request.relation_config,
            linked_schema=linked_schema,
        )
        preview_metadata = _extract_preview_metadata(
            svg,
            source_line_count=len(request.source_text.splitlines()),
            linked_definition_id=None if linked_schema is None else linked_schema.definition_id,
        )
        diagnostics = relation_diagnostics + runtime_diagnostics
        return SchemdrawRenderResult(
            request_id=request.request_id,
            document_version=request.document_version,
            status="rendered",
            svg=svg,
            diagnostics=diagnostics,
            cursor_position=_extract_cursor_position(request.relation_config),
            probe_points=_extract_probe_points(request.relation_config),
            render_time_ms=_elapsed_ms(started_at),
            preview_metadata=preview_metadata,
        )

    def _build_blocked_result(
        self,
        *,
        request: SchemdrawRenderRequest,
        diagnostics: tuple[SchemdrawDiagnostic, ...],
        render_time_ms: float,
    ) -> SchemdrawRenderResult:
        return SchemdrawRenderResult(
            request_id=request.request_id,
            document_version=request.document_version,
            status="blocked",
            svg=None,
            diagnostics=diagnostics,
            cursor_position=_extract_cursor_position(request.relation_config),
            probe_points=_extract_probe_points(request.relation_config),
            render_time_ms=render_time_ms,
            preview_metadata=None,
        )

    def _resolve_linked_schema(
        self,
        linked_schema: SchemdrawLinkedSchema | None,
    ) -> CircuitDefinitionRecord | None:
        if linked_schema is None:
            return None
        session = self._session_repository.get_session_state()
        definition = self._definition_repository.get_circuit_definition(linked_schema.definition_id)
        if definition is None:
            raise service_error(
                404,
                code="definition_not_found",
                category="not_found",
                message=f"Definition {linked_schema.definition_id} was not found.",
            )
        if definition.workspace_id != session.workspace_id or (
            definition.visibility_scope == "private"
            and definition.owner_user_id != _session_user_id(session)
        ):
            raise service_error(
                403,
                code="schemdraw_linked_schema_not_visible",
                category="permission_denied",
                message="The linked schema is not visible in the active workspace.",
            )
        return definition


def _validate_relation_config(
    relation_config: Mapping[str, object],
) -> tuple[SchemdrawDiagnostic, ...]:
    diagnostics: list[SchemdrawDiagnostic] = []
    labels = relation_config.get("labels")
    if labels is not None:
        if not isinstance(labels, Mapping) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in labels.items()
        ):
            diagnostics.append(
                SchemdrawDiagnostic(
                    severity="error",
                    code="schemdraw_relation_invalid",
                    message="relation_config.labels must be a mapping of string to string.",
                    source="relation_config",
                    blocking=True,
                )
            )
    probe_points = relation_config.get("probe_points")
    if probe_points is not None and not isinstance(probe_points, list):
        diagnostics.append(
            SchemdrawDiagnostic(
                severity="error",
                code="schemdraw_relation_invalid",
                message="relation_config.probe_points must be a list when provided.",
                source="relation_config",
                blocking=True,
            )
        )
    return tuple(diagnostics)


def _validate_python_source(
    source_text: str,
) -> tuple[tuple[SchemdrawDiagnostic, ...], ast.Module | None]:
    try:
        return (), ast.parse(source_text)
    except SyntaxError as exc:
        return (
            (
                SchemdrawDiagnostic(
                    severity="error",
                    code="schemdraw_syntax_error",
                    message="The Schemdraw source cannot be parsed.",
                    source="python_syntax",
                    blocking=True,
                    line=exc.lineno,
                    column=exc.offset,
                ),
            ),
            None,
        )


def _validate_render_entrypoint(
    syntax_tree: ast.Module,
) -> tuple[SchemdrawDiagnostic, ...]:
    allowed_imports = {"schemdraw", "schemdraw.elements"}
    diagnostics: list[SchemdrawDiagnostic] = []
    build_drawing_found = False

    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in allowed_imports:
                    diagnostics.append(
                        SchemdrawDiagnostic(
                            severity="error",
                            code="schemdraw_runtime_error",
                            message=f"Import '{alias.name}' is not allowed in Schemdraw preview.",
                            source="render_runtime",
                            blocking=True,
                            line=node.lineno,
                            column=node.col_offset,
                        )
                    )
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module not in allowed_imports:
                diagnostics.append(
                    SchemdrawDiagnostic(
                        severity="error",
                        code="schemdraw_runtime_error",
                        message=f"Import from '{module}' is not allowed in Schemdraw preview.",
                        source="render_runtime",
                        blocking=True,
                        line=node.lineno,
                        column=node.col_offset,
                    )
                )
        if isinstance(node, ast.FunctionDef) and node.name == "build_drawing":
            build_drawing_found = True

    if not build_drawing_found:
        diagnostics.append(
            SchemdrawDiagnostic(
                severity="error",
                code="schemdraw_runtime_error",
                message="Schemdraw source must define build_drawing(relation).",
                source="render_runtime",
                blocking=True,
            )
        )
    return tuple(diagnostics)


def _render_structural_svg(
    *,
    source_text: str,
    relation_config: Mapping[str, object],
    linked_schema: CircuitDefinitionRecord | None,
) -> str:
    tag = relation_config.get("tag")
    labels = relation_config.get("labels")
    label_lines: list[str] = []
    if isinstance(labels, Mapping):
        label_lines = [f"{key}: {value}" for key, value in labels.items()]
    text_lines = [
        "Schemdraw Structural Preview",
        f"Source lines: {len(source_text.splitlines())}",
        f"Relation tag: {tag if isinstance(tag, str) and len(tag) > 0 else 'n/a'}",
    ]
    if linked_schema is not None:
        text_lines.append(f"Linked definition: {linked_schema.name}")
        text_lines.append(f"Visibility: {linked_schema.visibility_scope}")
    text_lines.extend(label_lines[:4])

    width = 960
    line_height = 32
    height = 140 + (len(text_lines) * line_height)
    text_y = 60
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#f7f4ea" />',
        '<rect x="32" y="28" width="896" height="84" rx="18" fill="#1f3a2d" />',
        '<text x="64" y="82" font-size="30" font-family="Georgia, serif" fill="#f9f4e8">Schemdraw Render</text>',
        '<rect x="32" y="132" width="896" height="1" fill="#c9bda5" />',
    ]
    for line in text_lines:
        svg_lines.append(
            "<text "
            f'x="64" y="{text_y + 120}" font-size="20" '
            'font-family="Menlo, monospace" fill="#2b2a27">'
            f"{html.escape(line)}</text>"
        )
        text_y += line_height
    svg_lines.append("</svg>")
    return "".join(svg_lines)


def _extract_preview_metadata(
    svg: str,
    *,
    source_line_count: int,
    linked_definition_id: int | None,
) -> SchemdrawPreviewMetadata:
    root = ElementTree.fromstring(svg)
    width = int(float(root.attrib.get("width", "0")))
    height = int(float(root.attrib.get("height", "0")))
    view_box = root.attrib.get("viewBox", "")
    return SchemdrawPreviewMetadata(
        width=width,
        height=height,
        view_box=view_box,
        source_line_count=source_line_count,
        linked_definition_id=linked_definition_id,
    )


def _extract_cursor_position(
    relation_config: Mapping[str, object],
) -> SchemdrawCursorPosition | None:
    raw_value = relation_config.get("cursor_position")
    if not isinstance(raw_value, Mapping):
        return None
    x = raw_value.get("x")
    y = raw_value.get("y")
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return None
    return SchemdrawCursorPosition(x=float(x), y=float(y))


def _extract_probe_points(
    relation_config: Mapping[str, object],
) -> tuple[SchemdrawProbePoint, ...]:
    raw_value = relation_config.get("probe_points")
    if not isinstance(raw_value, list):
        return ()
    probe_points: list[SchemdrawProbePoint] = []
    for item in raw_value:
        if not isinstance(item, Mapping):
            continue
        name = item.get("name")
        x = item.get("x")
        y = item.get("y")
        if isinstance(name, str) and isinstance(x, (int, float)) and isinstance(y, (int, float)):
            probe_points.append(SchemdrawProbePoint(name=name, x=float(x), y=float(y)))
    return tuple(probe_points)


def _session_user_id(session: SessionState) -> str:
    return session.user.user_id if session.user is not None else "anonymous"


def _elapsed_ms(started_at: float) -> float:
    return round((perf_counter() - started_at) * 1000, 2)
