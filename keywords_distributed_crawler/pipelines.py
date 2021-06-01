# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker,scoped_session
from keywords_distributed_crawler.models.keywords import search
import logging
class KeywordsDistributedCrawlerPipeline:
    def process_item(self, item, spider):
        return item

class BaiduDbPipeline:
    def __init__(self,db_connect,db_debug):
        self.db_connect = db_connect
        self.db_debug = db_debug


    @classmethod
    def from_crawler(cls, crawler):
       return cls(
           db_connect=crawler.settings.get('DB_CONNECT'),
           db_debug=crawler.settings.get('DB_DEBUG')
       )

    def open_spider(self,spider):
        self.engine = create_engine(
            self.db_connect,
            echo=self.db_debug
        )
        # engine是2.2中创建的连接
        DBSession = sessionmaker(bind=self.engine)
        self.session = scoped_session(DBSession)

    def process_item(self, item, spider):
        res_check = self.session.query(search).filter(search.name == item['name']).filter(search.phone == item['phone']).filter(search.platform == item['platform']).first()
        if not res_check:
            self.session.add(search(name=item['name'],phone=item['phone'],platform=item['platform'],source_url=item['source_url'],create_at=func.now(),updated_at=func.now()))
        else:
            logging.debug(f"修改数据,手机号为:{res_check.phone}")
            res_check.source_url = item['source_url']
            res_check.updated_at = func.now()
        self.session.commit()
        return item

    def close_spider(self,spider):
        self.session.remove()
        self.engine.dispose()
