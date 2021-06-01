from scrapy.cmdline import execute
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy','crawl','baidu','-a','keywords=火锅店,铝合金','-a','totalpage=3'])