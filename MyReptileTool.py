import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

#国内版块评论请求格式字符串,将格式化字符串设为国内模版:channel=gn
commentsUrl='http://comment5.news.sina.com.cn/page/info?version=1&format=json&\
channel=gn&newsid=comos-{}&group=undefined&compress=0&ie=utf-8&oe=utf-8&\
page=1&page_size=3&t_size=3&h_size=3&thread=1&callback=jsonp_1531554557168&_=1531554557168'
newsUrl='http://news.sina.com.cn/c/2018-07-14/doc-ihfhfwmv6168912.shtml'
def getCommentCounts(newsUrl): #评论参与人数抽取函数
    m=re.search('doc-i(.*).shtml',newsUrl)
    newsid=m.group(1)
    comments=requests.get(commentsUrl.format(newsid))
    jsonStr=comments.text
    #print(jsonStr)
    jsonStr=jsonStr[jsonStr.find('(') + 1:-1]  #截取到有效json字串，从开头到一个左括号后及最后一个右括号前的部份是要的
    jd = json.loads(jsonStr)  #将jsonStr解析出来，并存入jd变量，jd变量为字典型
    return jd['result']['count']['total']  #按照数据的结构层级，取得评论参与总人数

def getNewsDetail(newsUrl): #新闻正文信息抽取函数
    result={}
    res=requests.get(newsUrl)
    res.encoding='utf-8'
    soup=BeautifulSoup(res.text,'html.parser')
    result['title']=soup.select('.main-title')[0].text
    result['newssource']=soup.select('.date-source a')[0].text
    timesource=soup.select('.date-source .date')[0].text
    result['dt']=datetime.strptime(timesource,'%Y年%m月%d日 %H:%M')
    result['article']=' '.join([p.text.strip() for p in soup.select('#article_content p')[:-5]])
    result['editor']=soup.select('.show_author')[0].text.strip().lstrip('责任编辑：')
    result['comments']=getCommentCounts(newsUrl)
    return result

def parseListLinks(url): #抽取指定新闻列表页内新闻链接并获取新闻正文信息函数
    newsdetails=[]
    res=requests.get(url)
    jd=json.loads(res.text.lstrip('  newsloadercallback(').rstrip(');')) #用lstrip,rstrip方法去掉json数据左右的函数包裹
    for ent in jd['result']['data']:
        newsdetails.append(getNewsDetail(ent['url'])) #获取列表页内每条新闻的链接后直接用刚才定义getNewsDetail方法获取
                                       #每条新闻正文相关信息字典，并将其加入到newsdetails列表中保存
    return newsdetails

