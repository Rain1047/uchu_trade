from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FnInstance(Base):
    __tablename__ = 'financial_news'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    source = Column(String(255), comment='来源')
    author = Column(String(255), comment='作者')
    url = Column(String(255), comment='网页链接')
    summary = Column(Text, comment='摘要')
    content = Column(Text, comment='内容')
    content_trans = Column(Text, comment='内容翻译')
    content_analysis = Column(Text, comment='内容分析')
    gmt_create = Column(DateTime, nullable=False, comment='新建时间', server_default='CURRENT_TIMESTAMP')
    gmt_modified = Column(DateTime, nullable=False, comment='更新时间', server_default='CURRENT_TIMESTAMP')


# 如果需要添加索引，可以在类外定义
idx_source = Index('idx_source', FnInstance.source)
idx_author = Index('idx_author', FnInstance.author)
