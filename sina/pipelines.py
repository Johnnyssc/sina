# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,create_engine,Text,DateTime,String,Integer
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Data(Base):
        __tablename__ = 'data'
        id = Column(Integer(), primary_key=True)
        times = Column(DateTime)
        title = Column(Text())
        content = Column(Text())
        type = Column(Text())


class SinaPipeline:
    def __init__(self):
        # 初始化数据库引擎，并将其绑定
        self.engine = create_engine('mysql+pymysql://root:123456@localhost:3306/sina', encoding='utf-8')
        Base.metadata.create_all(self.engine)
        self.DBSession = sessionmaker(bind=self.engine)

    def process_item(self, item, spider):
        new = Data()
        new.title = item['title']
        new.times = item['times']
        new.content = item['desc']
        new.type = item['type']

        session = self.DBSession()
        session.add(new)
        session.commit()
        return item



#     new = response.meta['new']
#     new.title = item['title']
#     new.times = item['times']
#     new.content = item['desc']
#
#
#     #创建一个数据库连接，并将数据通过commit方法提交上去
#     session = self.DBSession()
#     session.add(new)
#     session.commit()
#     yield item








        #写入csv文件的操作
        # if item.__class__ == ZongyiItem:
        #
        #     with open('E://Python//result//Zongyi.csv','a+',encoding='utf-8',newline='') as f:
        #         writer = csv.writer(f)
        #         writer.writerow([item['title'],item['desc'],item['times']])
        #
        # elif item.__class__ == GuoneiItem:
        #
        #     with open('E://Python//result//Guonei.csv','a+',encoding='utf-8',newline='') as f:
        #         writer = csv.writer(f)
        #         writer.writerow([item['title'],item['desc'],item['times']])
        #
        #
        # elif item.__class__ == DianyingItem:
        #
        #     with open('E://Python//result//Dianying.csv','a+',encoding='utf-8',newline='') as f:
        #         writer = csv.writer(f)
        #         writer.writerow([item['title'],item['desc'],item['times']])
        #
        #
        # elif item.__class__ == WorldItem:
        #
        #     with open('E://Python//result//World.csv','a+',encoding='utf-8',newline='') as f:
        #         writer = csv.writer(f)
        #         writer.writerow([item['title'],item['desc'],item['times']])
        #
        # elif item.__class__ == StarItem:
        #
        #     with open('E://Python//result//Star.csv','a+',encoding='utf-8',newline='') as f:
        #         writer = csv.writer(f)
        #         writer.writerow([item['title'],item['desc'],item['times']])
        #
        # elif item.__class__ == NvxingItem:
        #
        #     with open('E://Python//result//Nvxing.csv','a+',encoding='utf-8',newline='') as f:
        #         writer = csv.writer(f)
        #         writer.writerow([item['title'],item['desc'],item['times']])