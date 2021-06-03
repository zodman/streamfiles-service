from fastapi import FastAPI, File, UploadFile, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import aioboto3
import botocore.exceptions
import os
from torf import Torrent
from config import BUCKET, aws_kwargs, CDN_PATH, DATA_DIR
import logging

log = logging.getLogger(__name__)
app = FastAPI()

blob_s3_key = "original/{}"

app.mount("/static", StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    async with aioboto3.client("s3", **aws_kwargs) as s3:
        key = blob_s3_key.format(file.filename)
        try:
            await s3.upload_fileobj(file, BUCKET, key)
        except Exception:
            log.error("failed to upload to s3", exc_info=True)
    return "ok"


@app.get("/torrent/")
async def torrent():
    tor = Torrent.read("otome-1.mp4.torrent")
    return Response(content=tor.dump(), media_type="application/octet-stream")


@app.get("/download/{filename}")
async def download(filename: str, response: Response, request: Request):
    filepath = os.path.join(DATA_DIR, filename)
    key = blob_s3_key.format(filename)
    if os.path.exists(filepath):
        response.headers["X-Accel-Redirect"] = f"{CDN_PATH}{filename}"
    else:
        bytes_ = request.headers.get("range")
        kwargs = dict(Bucket=BUCKET, Key=key)
        if bytes_:
            kwargs.update({'Range': bytes_})
        async with aioboto3.client("s3", **aws_kwargs) as s3:
            try:
                await s3.head_object(**kwargs)
            except botocore.exceptions.ClientError:
                return "nani?"
            resp = await s3.get_object(**kwargs)
            data = await resp["Body"].read()
            headers = {
                'Content-Range':resp["ContentRange"],
                'Content-Length':str(resp["ContentLength"]),
                'Content-Type': resp["ContentType"],
            }
            return Response(content=data, headers=headers, status_code=206)
    return "yuju!!"


@app.get("/iframe")
async def iframe():
    return {}


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})
