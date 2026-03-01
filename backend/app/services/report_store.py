from pathlib import Path
from datetime import datetime

REPORT_DIR = Path(__file__).resolve().parents[2] / "reports"


def save_report(user_id: int, content: bytes) -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"report_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
    path = REPORT_DIR / filename
    path.write_bytes(content)
    return str(path)
