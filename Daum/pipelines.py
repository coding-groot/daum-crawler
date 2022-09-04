# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
import pandas as pd

class DaumPipeline:
    def __init__(self):
        self.con = sqlite3.connect("C:/Users/qwe/Desktop/sibeom/newstext.db")
        self.cur = self.con.cursor()

    def process_item(self, item, spider):
        keyword = item['keyword']
        df_article = item['article']
        df_reply = item['reply']
        df_rereply = item['rereply']

        create_article_table = '''CREATE TABLE IF NOT EXISTS "{}_article_daum"(
                                    "articleId" TEXT,
                                    "articleTitle" TEXT,
                                    "articleDate" TIMESTAMP)'''.format(keyword)

        print("create article table")

        create_reply_table = '''CREATE TABLE IF NOT EXISTS "{}_reply_daum"(
                                    "articleId" TEXT references {}_article(articleId),
                                    "replyId" TEXT,
                                    "replyContent" TEXT,
                                    "replyUser" TEXT,
                                    "replyDate" TIMESTAMP)'''.format(keyword,keyword)

        print("create reply table")

        create_rereply_table = '''CREATE TABLE IF NOT EXISTS "{}_rereply_daum"(
                                    "articleId" TEXT references {}_article(articleId),
                                    "replyId" TEXT references {}_reply(replyId),
                                    "rereplyId" TEXT,
                                    "rereplyContent" TEXT,
                                    "rereplyUser" TEXT,
                                    "rereplyDate" TIMESTAMP)'''.format(keyword,keyword,keyword)

        print("create rereply table")
        
        self.cur.execute(create_article_table)
        self.cur.execute(create_reply_table)
        self.cur.execute(create_rereply_table)


        df_article.to_sql('{}_article'.format(keyword),self.con,index=False,if_exists='append')
        df_reply.to_sql('{}_reply'.format(keyword),self.con,index=False,if_exists='append')
        df_rereply.to_sql('{}_rereply'.format(keyword),self.con,index=False,if_exists='append')
        
        
        
        
        return item
