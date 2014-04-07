from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
landing_page = Table('landing_page', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('page_name', String(length=64)),
    Column('page_type', String(length=120)),
    Column('product', String(length=120)),
    Column('visibility', SmallInteger),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['landing_page'].columns['visibility'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['landing_page'].columns['visibility'].drop()
