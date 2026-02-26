import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleRequest

app = FastAPI()

class CopyReq(BaseModel):
    fileId: str
    fileName: str

def get_drive_access_token():
    creds = service_account.Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
            "private_key": os.environ["GOOGLE_PRIVATE_KEY"].replace("\\n", "\n"),
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    creds.refresh(GoogleRequest())
    return creds.token

@app.post("/copy")
def copy_drive_to_bunny(req: CopyReq):

    token = get_drive_access_token()

    drive_url = f"https://www.googleapis.com/drive/v3/files/{req.fileId}?alt=media"

    r = requests.get(
        drive_url,
        headers={"Authorization": f"Bearer {token}"},
        stream=True
    )

    bunny_url = f"https://storage.bunnycdn.com/{os.environ['BUNNY_STORAGE_ZONE']}/{req.fileName}"

    upload = requests.put(
        bunny_url,
        headers={
            "AccessKey": os.environ["BUNNY_STORAGE_PASSWORD"],
            "Content-Type": "application/octet-stream"
        },
        data=r.iter_content(chunk_size=8*1024*1024)
    )

    return {
        "public_url": f"https://{os.environ['BUNNY_CDN_HOST']}/{req.fileName}"
    }
