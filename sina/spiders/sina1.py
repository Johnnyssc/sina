import scrapy
from  scrapy.http import Request
from scrapy.selector import Selector
from  selenium import webdriver
from sina.items import DataItem
import datetime
import re
import datetime



class Sina1Spider(scrapy.Spider):
    name = 'sina1'
    allowed_domains = ['sina.com.cn']


    #初始化函数，添加一些参数
    def __init__(self,page=None,flag=None,*args,**kwargs):

        #一些参数初始化
        super(Sina1Spider,self).__init__(*args,**kwargs)
        self.page = int(page)         #爬多少页,代码里写不科学，作为函数参数传进来
        self.flag = int(flag)          #具体数值在哪里写入呢？在main.py文件的命令里写入

        self.start_urls = ['https://news.sina.com.cn/china/',
                           'https://ent.sina.com.cn/film/',
                           'https://ent.sina.com.cn/zongyi/',
                           'https://ent.sina.com.cn/star/',
                           'http://eladies.sina.com.cn/']

        self.option = webdriver.ChromeOptions()

        self.option.add_argument('headless')                                #不打开浏览器
        self.option.add_argument('no-sandbox')                              #不打开沙盒
        self.option.add_argument('--blink-setting=imagesEnabled=false')     #不要图片


    def start_requests(self):
        """
        从初始化方法的start_url中解析出单个url
        并通过yield关键字产生Request对象，通过callback参数回调给parse方法
        """
        for url in self.start_urls:
            yield Request(url=url,callback=self.parse)


    def parse(self, response):
        """
        解析内容
        :param response:
        :return:
        """
        driver = webdriver.Chrome(chrome_options=self.option)
        driver.set_page_load_timeout(30)
        driver.get(response.url)
        #以上是webdriver，打开浏览器的一些设置，知道打开哪个网页

        # 【核心操作】 双重for循环：
        #           第一个for循环次数为page的页数：
        #               每一页不会一下子全部加载出来，有一个向下滑动加载更多的效果
        #           第二个for循环次数为每页中小新闻标题的个数：
        #               每次生成一个针对这个小新闻标题的Request对象，通过callnack参数传给下一个函数parse_namedetail

        for i in range(self.page):
            while not driver.find_element_by_xpath("//div[@class='feed-card-page']").text:      #直到翻页的按钮出现
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")         #滚动条往下滑动网页
            title = driver.find_elements_by_xpath("//h2[@class='undefined']/a[@target='_blank']")
            time = driver.find_elements_by_xpath("//h2[@class='undefined']/../div[@class='feed-card-a feed-card-clearfix']/div[@class='feed-card-time']")

            #不再细分，直接用DataItem
            for i in range(len(title)):
                eachtitle = title[i].text
                eachtime = time[i].text
                item = DataItem()
                if response.url == "https://ent.sina.com.cn/zongyi/":
                    item['type'] = 'zongyi'
                elif response.url == "https://news.sina.com.cn/china/":
                    item['type'] = 'news'
                elif response.url == "https://ent.sina.com.cn/film/":
                    item['type'] = 'film'
                elif response.url == "https://ent.sina.com.cn/star/":
                    item['type'] = 'star'
                elif response.url == "http://eladies.sina.com.cn/":
                    item['type'] = 'nvxing'

                item['title'] = eachtitle
                item['desc']  = ''
                href = title[i].get_attribute('href')
                today = datetime.datetime.now()
                eachtime = eachtime.replace('今天',str(today.month)+'月'+str(today.day)+'日')       #把'今天xx:xx'格式转换成年月日的标准形式

                #在首页对日期进行处理，日期的显示有不同情况，分类讨论
                if '分钟前' in eachtime:
                    minute = int(eachtime.split('分钟前')[0])
                    t = datetime.datetime.now() - datetime.timedelta(minutes=minute)
                    t2 = datetime.datetime(year=t.year,month=t.month,day=t.day,hour=t.hour,minute=t.minute)

                elif '年' not in eachtime:
                    eachtime = str(today.year) + '年' + eachtime
                    t1 = re.split(r'[日月年:]',eachtime)
                    t2 = datetime.datetime(year=int(t1[0]),month=int(t1[1]),day=int(t1[2]),
                                           hour=int(t1[3]),minute=int(t1[4]))

                item['times'] = t2

                #判断跑全量还是跑增量，1为增量，0为全量
                if self.flag == 1:
                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
                    if item['times'].strftime("%Y-%m-%d")  < yesterday:            #昨天之前的内容不要
                        driver.close()
                        break
                    elif yesterday <= item['times'].strftime("%Y-%m-%d") < today:
                        yield Request(response.urljoin(href),meta={'name':item},callback=self.parse_namedetail)
                else:
                    yield Request(response.urljoin(href),meta={'name':item},callback=self.parse_namedetail)
                    # 生成了一个Request对象，通过参数callback回调给parse_namedetail函数

            #点击下一页
            try:
                driver.find_element_by_xpath("//div[@class='feed-card-page']/span[@class='pagebox_next']/a").click()
            except:
                break


    def parse_namedetail(self, response):
        """
        从每一个单独的新闻页面中解析出time、desc、item
        :param response:
        :return:
        """
        #css selector选取元素
        selector = Selector(response)
        item = response.meta['name']
        desc = selector.xpath("//div[@class='article']/p/text()").extract()

        #处理desc
        desc = list(map(str.strip,desc))
        item['desc'] = ''.join(desc)

        yield item

        # # css selector选取元素
        # selector = Selector(response)
        # item = response.meta['name']
        # times = selector.xpath("//div[@class='date-source']/span[@class='date']/text()").extract()
        # desc = selector.xpath("//div[@class='article']/p/text()").extract()
        #
        # # 处理desc
        # desc = list(map(str.strip, desc))  # map(func(),Iterator) 将迭代器中每一个元素作为输入放到方法中，方法的输出作为新的结果，返回的是新的迭代器
        # item['desc'] = ''.join(desc)
        #
        # #把time处理成一个标准时间
        # t = times[0]
        # t1 = re.split(r'[年月日:]',t+":00")
        # t2 = datetime.datetime(year=int(t1[0]),month=int(t1[1]),day=int(t1[2]),hour=int(t1[3]),
        #                        minute=int(t1[4]),second=int(t1[5]))
        # item['times'] = t2
        #
        # if self.flag == 1:          #flag为1，就爬取前一天的数据；flag为0爬取全部数据
        #     now = datetime.datetime.now().strftime("%Y-%m-%d")
        #     yesterday = (datetime.datetime.now() + datetime.timedelta(-1)).strftime("%Y-%m-%d")
        #     if t2.strftime("%Y-%m-%d") < yesterday:             #判断当前这条消息的日期是否早于昨天
        #         self.crawler.engine.close_spider(self,"超出时间范围")
        #     if yesterday <= t2.strftime("%Y-%m-%d") < now:      #昨天发生的就提交上
        #         new = response.meta['new']
        #         new.title = item['title']
        #         new.times = item['times']
        #         new.content = item['desc']
        #
        #         session = self.DBSession()
        #         session.add(new)
        #         session.commit()
        #         yield item
        #
        # else:
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




