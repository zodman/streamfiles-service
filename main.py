from fastapi import FastAPI, File, UploadFile, Request, Response
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import aioboto3
import botocore.exceptions
from torf import Torrent, Magnet
import datetime
from config import BUCKET, aws_kwargs, CDN_PATH, WS_SERVER
from config import CACHE_DIR, CACHE_EXPIRE_DAYS, blob_s3_key, torrentblob_s3_key
from asyncdiskcache import AsyncCache
import logging
import aiofiles
import os
from tortoise.contrib.fastapi import register_tortoise
from db import models as db
import tempfile

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
app = FastAPI()

register_tortoise(app, db_url=db.DATABASE,
                  modules={'db.models': ['db.models']},
                  add_exception_handlers=True)
app.mount("/static", StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    # create torrent
    async with aiofiles.tempfile.TemporaryDirectory() as directory:
        filepath = os.path.join(directory, file.filename)
        torrent_path = f"{filepath}.torrent"
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(await file.read())
        tor = Torrent(path=filepath)
        assert tor.generate()
        tor.write(torrent_path)
        async with aioboto3.client("s3", **aws_kwargs) as s3:
            # # upload file
            key = blob_s3_key.format(file.filename)
            try:
                await s3.upload_file(filepath, BUCKET, key)
            except Exception:
                log.error("failed to upload to s3", exc_info=True)
                return "fooo file", 404
            # upload torrent
            torrent_key = torrentblob_s3_key.format(file.filename) + ".torrent"
            try:
                await s3.upload_file(torrent_path,
                                     BUCKET, torrent_key)
            except Exception:
                log.error("failed to upload to s3", exc_info=True)
                return "fooo", 404
            await db.File.create(filename=file.filename, bucket=BUCKET,
                                             torrent_key = torrent_key, file_key=key)
            try: pass
            except Exception as e :
                log.exception(e)
                return "404 dbcreation", 404

    return "ok"


@app.get("/torrent/{filename}")
async def torrent(filename:str):
    fileobj = await db.File.get(filename=filename)
    async with aioboto3.client("s3", **aws_kwargs) as s3:
        torrent_file = await s3.get_object(Bucket=fileobj.bucket,
                                           Key=fileobj.torrent_key)
        with tempfile.TemporaryFile() as f:
            f.write(await torrent_file["Body"].read())
            f.seek(0)
            tor = Torrent.read_stream(f)
            return Response(content=tor.dump(), media_type="application/octet-stream")


@app.get("/download/{filename}")
async def download(filename: str, response: Response, request: Request):
    key = blob_s3_key.format(filename)
    bytes_ = request.headers.get("range")
    if not bytes_:
        return Response(content="meme nani?", status_code=200)
    kwargs = dict(Bucket=BUCKET, Key=key)
    kwargs.update({'Range': bytes_})
    cache = AsyncCache()
    await cache.initialize(directory=f"{CACHE_DIR}/{key}")
    bytes_cached = await cache.get(bytes_)
    if bytes_cached is not None:
        log.info("x-cached: HIT")
        return Response(content=bytes_cached, headers ={'X-Cached': 'HIT'},
                        media_type="application/octet-stream", status_code=206)
    async with aioboto3.client("s3", **aws_kwargs) as s3:
        try:
            await s3.head_object(**kwargs)
        except botocore.exceptions.ClientError:
            return "nani?"
        resp = await s3.get_object(**kwargs)
        data = await resp["Body"].read()
        expire = datetime.timedelta(days=CACHE_EXPIRE_DAYS).total_seconds()
        await cache.set(bytes_, data, expire=expire)
        log.info("x-cached: MISS")
        headers = {
            'Content-Range': resp["ContentRange"],
            'Content-Length': str(resp["ContentLength"]),
            'Content-Type': resp["ContentType"],
            'X-Cached': 'MISS',
        }
        return Response(content=data, headers=headers, status_code=206)


@app.get("/{filename}")
async def root(request: Request, filename: str):
    ws_server = WS_SERVER
    return templates.TemplateResponse("index.html", {'request': request, 'filename':filename, 'WS_SERVER':ws_server})
