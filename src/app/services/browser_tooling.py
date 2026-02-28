"""Shared browser-side helpers for interactive schematic previews and formatting."""

from __future__ import annotations

import json

_PANZOOM_CDN_URL = "https://cdn.jsdelivr.net/npm/@panzoom/panzoom@4.6.0/dist/panzoom.min.js"
_RUFF_WASM_WEB_URL = "https://unpkg.com/@astral-sh/ruff-wasm-web@0.15.4/ruff_wasm.js"


def shared_frontend_tooling_head_html() -> str:
    """Return shared <head> HTML for Panzoom and Ruff WASM helpers."""
    return f"""
    <script src="{_PANZOOM_CDN_URL}"></script>
    <script>
    (() => {{
      if (window.scCircuitPreview) return;

      const previewStates = new Map();
      const MIN_SCALE = 0.4;
      const MAX_SCALE = 4.0;

      const clampScale = (value) => Math.min(MAX_SCALE, Math.max(MIN_SCALE, Number(value) || 1));
      const zoomText = (value) => `${{Math.round(clampScale(value) * 100)}}%`;

      function updateZoomLabel(state) {{
        if (!state || !state.labelId) return;
        const label = document.getElementById(state.labelId);
        if (label) label.textContent = zoomText(state.scale);
      }}

      function syncState(state) {{
        if (!state) return;
        if (state.panzoom) {{
          state.scale = clampScale(state.panzoom.getScale());
          const pan = state.panzoom.getPan();
          state.x = Math.round((pan?.x ?? 0) * 100) / 100;
          state.y = Math.round((pan?.y ?? 0) * 100) / 100;
        }} else {{
          state.scale = 1;
          state.x = 0;
          state.y = 0;
        }}
        updateZoomLabel(state);
      }}

      function ensureState(rootId, labelId) {{
        const root = document.getElementById(rootId);
        if (!root) return null;

        let state = previewStates.get(rootId);
        if (state && state.root !== root) {{
          previewStates.delete(rootId);
          state = null;
        }}

        if (!state) {{
          root.innerHTML = `
            <div class="schematic-panzoom-viewport" tabindex="0">
              <div class="schematic-panzoom-stage">
                <div class="schematic-panzoom-host"></div>
              </div>
            </div>
          `;

          const viewport = root.querySelector(".schematic-panzoom-viewport");
          const stage = root.querySelector(".schematic-panzoom-stage");
          const host = root.querySelector(".schematic-panzoom-host");
          const panzoom =
            typeof window.Panzoom === "function"
              ? window.Panzoom(stage, {{
                  minScale: MIN_SCALE,
                  maxScale: MAX_SCALE,
                  step: 0.2,
                  contain: "outside",
                  cursor: "grab",
                }})
              : null;

          state = {{
            root,
            viewport,
            stage,
            host,
            panzoom,
            labelId: labelId || "",
            schemaKey: "",
            scale: 1,
            x: 0,
            y: 0,
          }};

          if (panzoom) {{
            stage.addEventListener("panzoompan", () => syncState(state));
            stage.addEventListener("panzoomzoom", () => syncState(state));
            stage.addEventListener("panzoomreset", () => syncState(state));

            viewport.addEventListener(
              "wheel",
              (event) => {{
                if (!event.ctrlKey) return;
                event.preventDefault();
                panzoom.zoomWithWheel(event);
                syncState(state);
              }},
              {{ passive: false }}
            );

            viewport.addEventListener("pointerdown", () => {{
              viewport.focus();
            }});

            viewport.addEventListener("keydown", (event) => {{
              if (!(event.ctrlKey || event.metaKey)) return;
              const key = event.key;
              if (key === "0") {{
                event.preventDefault();
                panzoom.reset({{ animate: false, force: true }});
                syncState(state);
                return;
              }}
              if (key === "+" || key === "=") {{
                event.preventDefault();
                panzoom.zoomIn({{ animate: false }});
                syncState(state);
                return;
              }}
              if (key === "-") {{
                event.preventDefault();
                panzoom.zoomOut({{ animate: false }});
                syncState(state);
              }}
            }});
          }}

          previewStates.set(rootId, state);
        }}

        if (labelId) {{
          state.labelId = labelId;
        }}

        syncState(state);
        return state;
      }}

      function resetPreview(state) {{
        if (!state) return false;
        if (state.panzoom) {{
          state.panzoom.reset({{ animate: false, force: true }});
        }}
        state.scale = 1;
        state.x = 0;
        state.y = 0;
        syncState(state);
        return true;
      }}

      window.scCircuitPreview = {{
        render(payload) {{
          const state = ensureState(payload.rootId, payload.labelId);
          if (!state) return false;

          const nextSchemaKey = String(payload.schemaKey || "");
          const schemaChanged = state.schemaKey !== nextSchemaKey;
          state.host.innerHTML =
            payload.svgContent || "<div class='text-muted text-sm'>No preview</div>";
          state.schemaKey = nextSchemaKey;

          if (schemaChanged) {{
            resetPreview(state);
          }} else {{
            syncState(state);
          }}
          return true;
        }},
        zoomIn(rootId) {{
          const state = ensureState(rootId, "");
          if (!state || !state.panzoom) return false;
          state.panzoom.zoomIn({{ animate: false }});
          syncState(state);
          return true;
        }},
        zoomOut(rootId) {{
          const state = ensureState(rootId, "");
          if (!state || !state.panzoom) return false;
          state.panzoom.zoomOut({{ animate: false }});
          syncState(state);
          return true;
        }},
        reset(rootId) {{
          const state = ensureState(rootId, "");
          return resetPreview(state);
        }},
      }};
    }})();

    (() => {{
      if (window.scSchemaFormatter) return;

      const ruffModuleUrl = {json.dumps(_RUFF_WASM_WEB_URL)};
      let ruffModulePromise = null;

      async function loadRuff() {{
        if (!ruffModulePromise) {{
          ruffModulePromise = import(ruffModuleUrl).then(async (mod) => {{
            await mod.default();
            return mod;
          }});
        }}
        return ruffModulePromise;
      }}

      window.scSchemaFormatter = {{
        async format(sourceText) {{
          let workspace = null;
          try {{
            const mod = await loadRuff();
            workspace = new mod.Workspace(
              {{
                "line-length": 88,
                "indent-width": 4,
                format: {{
                  "indent-style": "space",
                  "quote-style": "double",
                }},
              }},
              mod.PositionEncoding.Utf16
            );
            const formatted = workspace.format(String(sourceText || ""));
            return {{ ok: true, text: formatted }};
          }} catch (error) {{
            return {{
              ok: false,
              error: String(error && error.message ? error.message : error),
            }};
          }} finally {{
            if (workspace && typeof workspace.free === "function") {{
              workspace.free();
            }}
          }}
        }},
        attachHotkey(buttonId, scopeId) {{
          const scope = document.getElementById(scopeId);
          if (!scope || scope.dataset.schemaHotkeyBound === "1") return false;

          scope.dataset.schemaHotkeyBound = "1";
          scope.addEventListener("keydown", (event) => {{
            const wantsFormat =
              (event.ctrlKey || event.metaKey) &&
              event.shiftKey &&
              !event.altKey &&
              event.key.toLowerCase() === "f";
            if (!wantsFormat) return;

            const button = document.getElementById(buttonId);
            if (!button) return;

            event.preventDefault();
            button.click();
          }});
          return true;
        }},
      }};
    }})();
    </script>
    """


def build_schematic_preview_render_js(
    *, root_id: str, label_id: str, svg_content: str, schema_key: str
) -> str:
    """Build client-side render call for a schematic preview."""
    payload = {
        "rootId": root_id,
        "labelId": label_id,
        "svgContent": svg_content,
        "schemaKey": schema_key,
    }
    return f"window.scCircuitPreview?.render({json.dumps(payload)});"


def build_schematic_preview_action_js(*, action: str, root_id: str) -> str:
    """Build client-side preview action call."""
    if action not in {"zoomIn", "zoomOut", "reset"}:
        raise ValueError(f"Unsupported preview action: {action}")
    return f"window.scCircuitPreview?.{action}({json.dumps(root_id)});"


def build_schema_formatter_js(source_text: str) -> str:
    """Build client-side Ruff WASM format call."""
    return f"return await window.scSchemaFormatter?.format({json.dumps(source_text)});"


def build_schema_formatter_hotkey_js(*, button_id: str, scope_id: str) -> str:
    """Build client-side hotkey binding call for the schema formatter."""
    return (
        "window.scSchemaFormatter?.attachHotkey("
        f"{json.dumps(button_id)}, {json.dumps(scope_id)});"
    )
