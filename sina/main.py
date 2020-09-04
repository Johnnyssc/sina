from scrapy import cmdline

cmdline.execute('scrapy crawl sina1 -a page=10 -a flag=0'.split())