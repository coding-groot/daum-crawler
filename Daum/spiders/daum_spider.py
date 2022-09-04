from ast import Global
from http.client import RESET_CONTENT
from traceback import print_tb
from psutil import users
import scrapy
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
from bs4 import BeautifulSoup
import requests
import json
from urllib.parse import urlparse, parse_qs
import time
import random
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from Daum.items import DaumItem
import datetime as dt
from tqdm.notebook import tqdm
import pandas as pd

class DaumSpider(scrapy.Spider):
    name = "daum"

    def start_requests(self):
        
        print("-------------STARTCRAWL---------------")
        
        self.keyword = "박근혜"###########
        key_words=urllib.parse.quote(self.keyword)
        searchtext=re.compile('https?:\/\/news\.v\.daum.net\/v\/')
        new_link_2=[]
        start_date = '20220724'###########
        end_date = '20220724'###########
        #url추출
        k=1
        while k!=2:###########
            print(k)
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            
            url = 'https://search.daum.net/search?w=news&DA=STC&enc=utf8&q={}&sort=recency&p={}&period=u&sd={}000000&ed={}235959'.format(key_words,k,start_date,end_date)
            driver = webdriver.Chrome('C:/Users/qwe/Desktop/chromedriver_win32/chromedriver.exe',options=options)
            driver.implicitly_wait(3)
            driver.get(url)

            data = driver.page_source

            soup = BeautifulSoup(data, 'html.parser')

            anchor_set=soup.find_all("a",{'class':['f_nb']})
            # print("A-------------------------: ",anchor_set)
        
            for i in anchor_set:
                try :
                    if searchtext.match(str(i['href'])) != str(i['href']).startswith('http://v.media.daum.net/v/'):
                        new_link_2.append(str(i['href']))
                except :
                    pass
            k+=1


        for url in new_link_2:
            try:
                yield scrapy.Request(url=url, callback=self.parse)
            except:
                pass

    def parse(self, response):
        
        daum_item = DaumItem()
#기사제목
        articleTitle = response.css('div.head_view > h3::text').get()
  
#기사작성시간
        articleDate = dt.datetime.strptime(response.css('span.num_date::text').get(),"%Y. %m. %d. %H:%M")
        #2022-07-24 19:33:26 [scrapy.core.scraper] ERROR: Spider error processing <GET https://news.v.daum.net/v/20220721192554547> (referer: None)Traceback (most recent call last):

#댓글 test
        org = str(response)[5:-1]
        articleId = org.split("/")[-1] # ex.20211125234942863
        print("articleid",articleId)
        req = requests.get(org)
        soup = BeautifulSoup(req.content)
        data_client_id = soup.find('div',{'class':'alex-area'}).get('data-client-id')

        header = {
            'authority' : 'comment.daum.net',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0',
            'accept' : "*/*",
            'accept-encoding' : 'gzip, deflate, br',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer' : "",
        }

        # authorization 값 반환
        header['referer'] = org # referer 값을 꼭 추가해주자
        token_url = "https://alex.daum.net/oauth/token?grant_type=alex_credentials&client_id={}".format(data_client_id)
        req = requests.get(token_url, headers=header)
        access_token = json.loads(req.content)['access_token']
        authorization = 'Bearer '+access_token

        header['authorization'] = authorization # authorization 값을 꼭 추가
        post_url = """https://comment.daum.net/apis/v1/ui/single/main/@{}""".format(articleId)
        req = requests.get(post_url, headers = header)
        soup = BeautifulSoup(req.content,'html.parser')
        post_id = json.loads(soup.text)['post']['id'] # 드디어 드러나는 post id 의 값
        print("post_id",post_id)
        offset = 0
        request_url = """
        https://comment.daum.net/apis/v1/posts/{}/comments?parentId=0&offset={}&limit=100&sort=RECOMMEND&isInitial=false&hasNext=true
        """.format(post_id, offset)

        req = requests.get(request_url, headers=header)
        soup = BeautifulSoup(req.content,'html.parser')
        temp_json_list = json.loads(soup.text)

        replyId = []
        replyUser = []
        replyContent = []
        replyDate = []

        for comment in temp_json_list:
            replyId.append(comment['id'])            
            replyUser.append(comment['userId'])
            replyContent.append(comment['content'])
            replyDate.append(comment['createdAt'])
        
        print("replyid",replyId)
        re_replyId = []
        rereplyId =[]
        rereplyUser = []
        rereplyContent = []
        rereplyDate = []

        for Id in replyId:
            re_comment_url = "https://comment.daum.net/apis/v1/comments/{}/children?offset=0&limit=100&sort=CHRONOLOGICAL&hasNext=true".format(Id)
            re_req = requests.get(re_comment_url, headers=header)
            re_soup = BeautifulSoup(re_req.content,'html.parser')
            re_temp_json_list = json.loads(re_soup.text)

            re_replyId.append(re_temp_json_list[0]['parentId'])

            rereplyId.append(re_temp_json_list[0]['id'])
            rereplyUser.append(re_temp_json_list[0]['user']['displayName'])
            rereplyContent.append(re_temp_json_list[0]['content'])
            rereplyDate.append(re_temp_json_list[0]['post']['createdAt'])

        
        daum_item['keyword'] = self.keyword
        daum_item['article'] = pd.DataFrame({'articleId':[articleId],'articleTitle':[articleTitle],'articleDate':[articleDate]})
        daum_item['reply'] = pd.DataFrame({'articleId':[articleId]*len(replyContent),'replyId':replyId,'replyContent':replyContent,
            'replyUser':replyUser,'replyDate':replyDate})
        daum_item['rereply'] = pd.DataFrame({'articleId':[articleId]*(len(rereplyContent)),'replyId': re_replyId,'rereplyId':rereplyId,
            'rereplyContent':rereplyContent,'rereplyUser':rereplyUser,'rereplyDate':rereplyDate})
        
        print(daum_item['article'])
        print(daum_item['reply'])
        print(daum_item['rereply'])

        yield daum_item
            