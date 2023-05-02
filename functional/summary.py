import os
import openai
import json
import streamlit as st
from newspaper import Article
from newspaper import Config

class SummaryContent(object):
    def __init__(self, 
                 news, engine=None):
        USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
        self.config = Config()
        self.config.browser_user_agent = USER_AGENT
        self.config.request_timeout = 10
        self.related_articles = []
        self.related_articles_meta = []
        self.related_src = []
        self.related_src_url = []
        self.title = None
        self.summary = None
        self.image = None
        self.authors = None
        self.media = None
        self.keywords = None
        self.date = None
        self.article = None
        article = self._transform_article(news)
        if article is not None:
            self._save_to_attr(article, date=news['datetime'], media=news['media'])
        self.us_search_engine = engine#GoogleNews(lang="en", region="US", encode="utf-8")

        self.prompt = '''
            Please help me gather data from various media sources above and analyze it across multiple articles to recognize similarities and differences. 
            For instance, if several articles report on the launch of a new Tesla car, one source might state the retail price as $10, while another mentions it as $15. 
            The similarities between the articles would be that they all cover the new car launch, while the differences would be the varying retail prices reported. 
            The final output should include a summary paragraph followed by a list of similarities and differences, 
            where the differences are presented in the format of source A reporting a price of $10, while source B reports a price of $15.
            response should be formed organized and neat.
        '''
        openai.api_key = st.session_state["OPENAI_API_KEY"]
        
    def _save_to_attr(self, article, date=None, media=""):
        self.title = article.title
        self.article = article.text
        self.summary = article.summary
        self.image = article.top_image
        self.authors = article.authors
        self.keywords = article.keywords
        self.media = media
        self.date = date#.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.related_articles.append(self.article)
        self.related_src.append(self.media)
        self.related_src_url.append(article.url)
        self.related_articles_meta.append(article.meta_data)

    def _transform_article(self, data):
        try:
            article = Article(data["link"], config=self.config)
            article.download()
            article.parse()
            # article.nlp()
        except:
            return None
        return article

    def _trasform_related(self, nums=5):
        self.us_search_engine.clear()
        related_articles = self.us_search_engine.search(keys=", ".join(self.title), nums=10)
        for related in related_articles[1:nums+1]:
            article = self._transform_article(related)
            if article is None:
                continue
            self.related_src.append(related["media"])
            cur_url = article.url if article.url is not None else related['link']
            self.related_src_url.append(cur_url)
            self.related_articles.append(f"source media: {related['media']}, content: {article.text}")
            self.related_articles_meta.append(article.meta_data)

    def summarize(self, prompt="", nums=5):
        self._trasform_related(nums=nums)
        answer, err_list = self._ask(prompt=prompt)
        return answer, err_list
    
    def _ask(self, prompt="Summarize the above article in few sentences, and preserve all the important information such as people, location, time, number, event, etc."):
        summary_list = []
        error_list = []
        for idx, r in enumerate(self.related_articles):
            messages=[
                    {"role": "system", "content": "You are a very professional news artlce summization and analysis agent."},
                    {"role": "user", "content": r + " " + prompt},
                ]
            try:
                response = openai.ChatCompletion.create(
                                                    model="gpt-3.5-turbo",
                                                    messages=messages,
                                                )
                answer = response["choices"][0]["message"]["content"].strip()
                summary_list.append(answer)
                error_list.append("")
                st.success(f"success process {idx} article")
            except Exception as e:
                st.error(f"success process {idx} article")
                error_list.append(e)
        
        summary_list = ".".join(summary_list) + " " + self.prompt
        messages = [
                    {"role": "system", "content": "You are a very professional news artlce summization and analysis agent."},
                    {"role": "user", "content": summary_list},
                ]
        try:
            response = openai.ChatCompletion.create(
                                                model="gpt-3.5-turbo",
                                                messages=messages,
                                            )
            answer = response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            answer = e

        return answer, error_list