import scrapy,re
from scrapy_splash import SplashRequest
from keywords_distributed_crawler.items import BaiduItem
import logging
class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    # allowed_domains = ['www.baidu.com']
    start_urls = ['https://www.baidu.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
    }

    def __init__(self, keywords=None,totalpage=None, *args, **kwargs):
        super(BaiduSpider, self).__init__(*args, **kwargs)
        self.keywords=keywords
        self.totalpage=totalpage
        # self.keywords="空压机,海底捞"
        # self.totalpage=5

    def start_requests(self):
        lua_source = """
            function main(splash, args)
              splash:set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
              assert(splash:go(args.url))
              assert(splash:wait(1))
              js = string.format("document.querySelector('#kw').value='%s';document.querySelector('#su').click()",args.keyword)
              splash:evaljs(js)
              assert(splash:wait(2))
              return {
                html = splash:html(),
                cookies = splash:get_cookies()
              }
            end
                """;
        for url in self.start_urls:
            keywords_list = self.keywords.strip(',').split(',')
            for keyword in keywords_list:
                yield SplashRequest(url=url, meta={"keyword": keyword,"page":2},callback=self.parse,endpoint='execute',args={'lua_source':lua_source,'keyword':keyword})

    # 获取快照和下一页
    def parse(self, response):
        meta = response.meta
        # 快照获取
        baidu_kz=response.css('div.se_st_footer>a.m::attr(href)').extract()
        for url in baidu_kz:
            yield scrapy.Request(url=url, meta=response.meta,callback=self.kzparse,headers=self.headers,dont_filter=True)

        logging.debug(f"关键词{meta['keyword']},页码为:{meta['page'] - 1}")
        #获取下一页
        if int(meta['page']) <= int(self.totalpage):
            next_url=response.xpath(f"//span[@class='pc' and contains(text(),'{meta['page']}')]/../@href").extract_first()
            if next_url:
                lua_source = """
                    function main(splash, args)
                      splash:set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36')
                      splash:init_cookies(args.cookies)
                      assert(splash:go(args.url))
                      assert(splash:wait(1))
                      return {
                        html = splash:html(),
                        cookies = splash:get_cookies()
                      }
                    end
                        """;
                next_page_url=response.urljoin(next_url)
                yield SplashRequest(url=next_page_url,meta={"keyword": meta['keyword'],"page":int(meta['page'])+1},callback=self.parse,endpoint='execute',args={'lua_source':lua_source,'cookies':response.data['cookies']})
            else:
                logging.debug(f"关键词{meta['keyword']},页码为:{meta['page']}链接页获取失败")

    # 提取手机号
    def kzparse(self,response):
        meta=response.meta
        item=BaiduItem()
        phones=self.getReMatchPhones(response.text)
        for phone in phones:
            item['name']=meta['keyword']
            item['phone'] = phone
            item['platform'] = self.name
            item['source_url'] = response.css('#bd_snap_note>a::attr(href)').extract_first() if response.css('#bd_snap_note>a::attr(href)').extract_first() else response.real_url
            yield item

    # 批量正则规则查询手机号
    def getReMatchPhones(self,html):
        re_list = [
            {'re': '1[3|4|5|6|7|8|9]\d{9}<', 'sub': '<'},
            {'re': '>1[3|4|5|6|7|8|9]\d{9}', 'sub': '>'},
            {'re': '1[3|4|5|6|7|8|9]\d{1}-\d{4}-\d{4}', 'sub': '-'},
            {'re': '1[3|4|5|6|7|8|9]\d{1} \d{4} \d{4}', 'sub': ' '},
            {'re': ' 1[3|4|5|6|7|8|9]\d{9} ', 'sub': ' '},
            {'re': '热线：1[3|4|5|6|7|8|9]\d{9}', 'sub': '热线：'},
            {'re': '热线:1[3|4|5|6|7|8|9]\d{9}', 'sub': '热线:'},
            {'re': '手机：1[3|4|5|6|7|8|9]\d{9}', 'sub': '手机：'},
            {'re': '手机:1[3|4|5|6|7|8|9]\d{9}', 'sub': '手机:'},
            {'re': '电话：1[3|4|5|6|7|8|9]\d{9}', 'sub': '电话：'},
            {'re': '电话:1[3|4|5|6|7|8|9]\d{9}', 'sub': '电话:'},
            {'re': 'TEL：1[3|4|5|6|7|8|9]\d{9}', 'sub': 'TEL：'},
            {'re': 'TEL:1[3|4|5|6|7|8|9]\d{9}', 'sub': 'TEL:'},
            {'re': 'tel：1[3|4|5|6|7|8|9]\d{9}', 'sub': 'tel：'},
            {'re': 'tel:1[3|4|5|6|7|8|9]\d{9}', 'sub': 'tel:'},
        ]
        phones_list = []
        for item in re_list:
            res = self.getPhones(html, item)
            # print(res)
            phones_list = phones_list + res

        # 手机号去重复
        new_phones_list = list(set(phones_list))
        # 维持数据顺序一致
        new_phones_list.sort(key=phones_list.index)
        return new_phones_list

    # 正则规则获取手机号
    def getPhones(self,html, re_match):
        # 手机号正则,"1"代表数字1开头，"[3|4|5|7|8]"代表第2位是3/4/5/7/8中任一个，"\d"代表0~9的数字，"{9}"代表按前面的规则取9次
        pattern_mob = re.compile(re_match['re'])
        # 用正则匹配html文件中的内容，匹配结果放在变量result中，结果是list形式，如果匹配到两个就这样['13699999999', '17399999999']
        result = pattern_mob.findall(html)
        new_result = []
        # 处理替换正则
        if re_match['sub'] != "":
            for item in result:
                new_result.append(re.sub(re_match['sub'], "", item))
        else:
            new_result = result
        # 返回匹配结果
        return new_result