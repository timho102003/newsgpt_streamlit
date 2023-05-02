import datetime
from GoogleNews import GoogleNews

class SearchEngine(object):
    def __init__(self, lang, region) -> None:
        # __user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
        # __user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        # config = Config()
        # # config.browser_user_agent = __user_agent
        # HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
        #    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        # config.headers = HEADERS
        self.__lang = lang
        self.__region = region
        self.__get_page = 0
        self.engine = GoogleNews(lang=self.lang, region=region, encode="utf-8")
        
    @property
    def lang(self):
        return self.__lang
    
    @property
    def region(self):
        return self.__region
    
    def set_period(self, period):
        self.engine.set_period(period=period)
    
    def clear(self):
        self.engine.clear()

    def search(self, keys="", nums=5):
        self.engine.clear()
        self.engine.search(key=keys)
        self.engine.get_page(self.__get_page)
        results = self.engine.results()
        out_result = []
        i = 0
        while len(out_result) < nums and i < len(results):
            if results[i]["media"].lower() != "youtube":
                if not isinstance(results[i]["datetime"], datetime.datetime):
                    results[i]["datetime"] = "unknown"
                else:
                    results[i]["datetime"] = results[i]["datetime"].strftime('%Y-%m-%d %H:%M:%S.%f')
                out_result.append(results[i])
            i += 1
        return out_result
