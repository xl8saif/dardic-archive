"""Google Drive access (read-only) for the sync pipeline.

First run opens a browser for OAuth consent; the token is cached in
sync/token.json (gitignored). The pipeline never writes to Drive.
"""
from __future__ import annotations

from pathlib import Path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import io

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_PATH = Path(__file__).resolve().parent / "token.json"
SECRET_PATH = Path(__file__).resolve().parent / "client_secret.json"


def get_service():
    """Authorize and return a Drive v3 service object."""
    creds: Credentials | None = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not SECRET_PATH.exists():
            raise SystemExit(
                "Google Drive credentials missing.\n"
                "  1. Create a project at https://console.cloud.google.com/\n"
                "  2. Enable the Google Drive API\n"
                "  3. Create an OAuth client ID (type: Desktop app)\n"
                f"  4. Download it as {SECRET_PATH}"
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(SECRET_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return build("drive", "v3", credentials=creds)


def find_folder_by_name(service, name: str, parent_id: str | None = None) -> str | None:
    """Return the folder id for the first folder with this exact name."""
    q = ["mimeType='application/vnd.google-apps.folder'",
         f"name = '{name}'", "trashed = false"]
    if parent_id:
        q.append(f"'{parent_id}' in parents")
    res = service.files().list(
        q=" and ".join(q), fields="files(id, name)", pageSize=5).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def list_children(service, folder_id: str) -> list[dict]:
    """All live files/folders directly inside folder_id."""
    out: list[dict] = []
    page_token = None
    while True:
        res = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            pageSize=100, pageToken=page_token,
        ).execute()
        out.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            return out


def export_google_doc(service, file_id: str, mime: str = "text/html") -> bytes:
    """Export a native Google Doc to the given MIME type."""
    return service.files().export(fileId=file_id, mimeType=mime).execute()


def download_file(service, file_id: str) -> bytes:
    """Download a regular (binary) file's content."""
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, service.files().get_media(fileId=file_id))
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


def load_cache() -> dict:
    cache_path = Path(__file__).resolve().parent / ".cache.yaml"
    if cache_path.exists():
        import yaml
        return yaml.safe_load(cache_path) or {}
    return {}


def save_cache(cache: dict) -> None:
    import yaml
    cache_path = Path(__file__).resolve().parent / ".cache.yaml"
    cache_path.write_text(
        yaml.safe_dump(cache, allow_unicode=True, sort_keys=True), encoding="utf-8")
