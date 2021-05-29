import databases
import orm
import sqlalchemy
import click
from config import DATABASE

database = databases.Database(DATABASE)
metadata = sqlalchemy.MetaData()

## Models

class File(orm.Model):
    __tablename__ = "files"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    filename = orm.Text(unique=True)

engine = sqlalchemy.create_engine(str(database.url))


## commands

@click.group()
def cli():
    pass


@cli.command()
def initdb():
    metadata.create_all(engine)
    click.echo("db created")

if __name__ == "__main__":
    cli()
