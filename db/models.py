from tortoise.models import Model
from tortoise import fields
from tortoise import Tortoise, run_async
from config import DATABASE
import click


class File(Model):
    id = fields.IntField(pk=True)
    filename = fields.TextField()
    bucket = fields.CharField(max_length=100)
    file_key = fields.TextField()
    torrent_key = fields.TextField()

    class Meta:
        unique_together=(('bucket', 'filename'), )



async def initdb():
    await Tortoise.init(db_url=DATABASE, modules = {'db.models':['__main__']})
    await Tortoise.generate_schemas()

if __name__ == "__main__":
    run_async(initdb())

