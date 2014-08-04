from peewee import *

database = SqliteDatabase('/Users/dbr/code/webtools/dev.sqlite3', threadlocals=True)


class BaseModel(Model):
    class Meta:
        database = database


class Channel(BaseModel):
    chanid = CharField(max_length=256)
    icon_url = CharField(max_length=1024, null=True)
    last_refresh = DateTimeField(null=True)
    last_update_content = DateTimeField(null=True)
    last_update_meta = DateTimeField(null=True)
    service = CharField(max_length=256, null=True)
    title = CharField(max_length=512, null=True)

    class Meta:
        db_table = 'ytdl_channel'


class Video(BaseModel):
    STATE_NEW = 'NE'
    STATE_QUEUED = 'QU'
    STATE_DOWNLOADING = 'DL'
    STATE_GRABBED = 'GR'
    STATE_GRAB_ERROR = 'GE'
    STATE_IGNORE = 'IG'

    STATES = (
        (STATE_NEW, 'New video'),
        (STATE_QUEUED, 'Queued for download, but not begun yet'),
        (STATE_DOWNLOADING, 'Downloading'),
        (STATE_GRABBED, 'Grabbing video now'),
        (STATE_GRAB_ERROR, 'Error while grabbing video'),
        (STATE_IGNORE, 'Ignored video'),
        )


    _thumbnails = CharField(max_length=1024)
    channel = ForeignKeyField(Channel, related_name="videos")
    description = TextField(null=True)
    publishdate = DateTimeField()
    status = CharField(max_length=2)
    title = CharField(max_length=1024)
    url = CharField(max_length=1024)
    videoid = CharField(max_length=256)

    class Meta:
        db_table = 'ytdl_video'

    def __unicode__(self):
        return "%s (on %s) [%s]" % (self.title, self.channel.chanid, self.status)

    @property
    def img(self):
        return self._thumbnails.split("  ")


chan = Channel.get(id=1)
for k in Video.select().where(Video.status == Video.STATE_GRAB_ERROR):
    print k


"""
from sqlalchemy import Column, Integer, String
from yourapplication.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)
"""
