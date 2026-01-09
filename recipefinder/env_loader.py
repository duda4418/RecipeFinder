import os
from pathlib import Path
from dotenv import load_dotenv 


def load_dotenv_if_present() -> None:
    """Load environment variables from a local .env file if present.
    """

    env_path = Path(__file__).with_name(".env")
    project_env = Path(__file__).resolve().parent.parent / ".env"
    candidates = [env_path, project_env]

    target = next((path for path in candidates if path.exists()), None)
    if target is None:
        return

    try:
        load_dotenv(dotenv_path=target)
        return
    except Exception:
        pass

    try:
        for raw_line in target.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception as exc:
        print(f"Failed to read .env: {exc}")
