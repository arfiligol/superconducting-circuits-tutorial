"""Export OpenAPI spec without starting the server."""
import json
from pathlib import Path
from backend.src.app.main import app  # FastAPI app instance

def export_openapi(output: Path = Path("openapi.json")) -> None:
    spec = app.openapi()
    output.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    print(f"OpenAPI spec exported to {output}")

if __name__ == "__main__":
    export_openapi()
