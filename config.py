import easyconf
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

config = easyconf.Config(os.path.join(BASE_DIR, "settings.yml"))

BUCKET = config.BUCKET(initial="animeesp")

DATABASE = config.DATABASE(initial='sqlite:///db.sqlite3')

AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID(default=None)
AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY(default=None)
AWS_REGION = config.AWS_REGION(default=None)
AWS_ENDPOINT_URL = config.AWS_ENDPOINT_URL(default=None)

aws_kwargs = {
    "aws_access_key_id": AWS_ACCESS_KEY_ID,
    "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
    "region_name": AWS_REGION,
    "endpoint_url": AWS_ENDPOINT_URL
}
CDN_PATH = config.CDN_PATH(initial="/cdn/")
DATA_DIR = config.DATA_DIR(initial=os.path.join(BASE_DIR, "data/"))
