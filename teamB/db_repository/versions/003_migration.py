from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
campaign = Table('campaign', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('creator_id', SmallInteger),
    Column('name', String(length=64)),
    Column('funnel_ids', String(length=500)),
)

funnel = Table('funnel', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('campaign_id', SmallInteger),
    Column('name', String(length=64)),
    Column('product', String(length=120)),
    Column('content_ids', String(length=500)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['campaign'].create()
    post_meta.tables['funnel'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['campaign'].drop()
    post_meta.tables['funnel'].drop()
