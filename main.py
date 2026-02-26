import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CopyReq(BaseModel):
    fileId: str
    fileName: str

@app.post("/copy")
def copy_drive_to_bunny(req: CopyReq):

    drive_url = f"https://drive.google.com/uc?export=download&id={req.fileId}"

    r = requests.get(
        drive_url,
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
