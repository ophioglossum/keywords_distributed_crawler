from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BIGINT,VARCHAR,REAL
from sqlalchemy.dialects.mysql import TIMESTAMP
Base = declarative_base()
#搜索关键词表
class search(Base):
    __tablename__ = 'search'

    # 指定id映射到id字段; id字段为整型，为主键
    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR(128), nullable=False)
    phone = Column(VARCHAR(16), nullable=False)
    platform=Column(VARCHAR(16), nullable=False)
    source_url=Column(VARCHAR(1024), nullable=False)
    create_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
