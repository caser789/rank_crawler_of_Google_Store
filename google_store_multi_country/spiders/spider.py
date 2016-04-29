import re
import redis
from scrapy import Spider, FormRequest
from ..items import GoogleStoreMultiCountryItem as Item


def get_bundle_ID(s):
    ptn = re.compile(r".*?id=(.*?)$")
    res = ptn.findall(s)
    if res:
        ID = res[0]
    else:
        ID = ''
    return ID


def get_start_URLs():
    server = redis.Redis(host='localhost', port=6379)
    country_redis_name = 'country_code'
    country2code = server.hgetall(country_redis_name)
    country_codes = [ele.lower() for ele in country2code.values()]

    cat_redis_name = 'GoogleStoreCategory'
    cat2value = server.hgetall(cat_redis_name)
    cats = [ele.upper() for ele in cat2value.keys()]
    rank_types = ["topselling_paid", "topselling_free", "topgrossing"]
    host = "https://play.google.com"
    url_stub = ("{host}/store/apps/category/{cat}/colle"
                "ction/{rank_type}?hl=en&gl={gl}")
    urls = []
    for r in rank_types:
        for c in cats:
            for code in country_codes:
                url = url_stub.format(host=host, cat=c, rank_type=r, gl=code)
                urls.append((url, c, code, r))
    return urls


class GoogleStoreSpider(Spider):

    name = "google"
    allowed_domains = ['play.google.com']

    def start_requests(self):
        URLs = get_start_URLs()
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, sdch',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'referer': 'https://play.google.com/store/apps/category/APP_WIDGETS/collection/topselling_paid',
            'origin': 'https://play.google.com',
        }
        for URL, cat, code, rank_type in URLs:
            self.logger.debug("request URL: %s" % URL)

            for i in range(5):
                start = str(0 + i * 60)
                num = str(60)
                data = {
                    'start': start,
                    'num': num,
                    'numChildren': '0',
                    'cllayout': 'NORMAL',
                    'ipf': '1',
                    'xhr': '1',
                }
                yield FormRequest(
                    url=URL,
                    headers=headers,
                    formdata=data,
                    callback=self.parse,
                    meta={'page': i, 'code': code,
                          'rank_type': rank_type,
                          'cat': cat},
                )

    def parse(self, response):
        page_URL = response.url
        self.logger.debug("response URL: %s" % page_URL)
        page = response.meta['page']
        code = response.meta['code']
        cat = response.meta['cat']
        rank_type = response.meta['rank_type']
        name_stub = "{code}.{cat}.{rank_type}"
        rank_list_name = name_stub.format(code=code, cat=cat,
                                          rank_type=rank_type)

        URL_xpath = "//a[@class='title']/@href"
        title_xpath = "//a[@class='title']/@title"
        URLs = response.xpath(URL_xpath).extract()
        titles = response.xpath(title_xpath).extract()
        IDs = [get_bundle_ID(URL) for URL in URLs]
        for i in range(len(IDs)):
            rank = 60 * page + i + 1
            bundle_ID = IDs[i]
            title = titles[i].encode('utf-8')
            temp = "{i}\t{bundle_ID}\t{title}"
            s = temp.format(i=rank, bundle_ID=bundle_ID, title=title)
            self.logger.debug(s)
            item = Item()
            item['rank_list_name'] = rank_list_name
            item['bundle_ID'] = bundle_ID
            item['rank'] = rank
            item['title'] = title
            yield item


