from fastapi import FastAPI, File, UploadFile, Request, Response
from fastapi.responses import StreamingResponse
import aioboto3
import botocore.exceptions
import os
from config import BUCKET, aws_kwargs, CDN_PATH, DATA_DIR
import logging

log = logging.getLogger(__name__)
app = FastAPI()

blob_s3_key="original/{}"

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    async with aioboto3.client("s3", **aws_kwargs) as s3:
        key = blob_s3_key.format(file.filename)
        try:
            await s3.upload_fileobj(file, BUCKET, key)
        except Exception as e:
            log.error("failed to upload to s3", exc_info=True)
    return "ok"

@app.get("/download/{filename}")
async def download(filename: str, response: Response, request: Request):
    filepath = os.path.join(DATA_DIR, filename)
    key = blob_s3_key.format(filename)
    if os.path.exists(filepath):
        response.headres["X-Accel-Redirect"] = f"{CDN_PATH}{filename}"
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
            return StreamingResponse(resp["Body"])
    return "yuju!!"

@app.get("/")
async def root():
    return {}
