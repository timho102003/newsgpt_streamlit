import json
import streamlit as st
from functional import SummaryContent, SearchEngine

@st.cache_data
def search(keys="", period='1d', news_num=1):
    st.session_state["search_engine"].clear()
    st.session_state["search_engine"].set_period(period)
    results = st.session_state["search_engine"].search(keys=keys, nums=news_num)
    # results = [SummaryContent(news=r, engine=st.session_state["search_engine"]) for r in results]
    return json.dumps({"results": results})

@st.cache_data
def form_summarycontent():
    st.session_state["raw_contents"] = search(keys=st.session_state["current_search"], news_num=10)
    st.session_state["raw_contents"] = json.loads(st.session_state["raw_contents"])["results"]
    st.session_state["contents"] = [SummaryContent(news=r, engine=SearchEngine(lang="en", region="US")) for r in st.session_state["raw_contents"]]


def clear():
    st.session_state["current_search"] = ""
    st.session_state["raw_contents"] = []
    st.session_state["contents"] = []
    search.clear()
    form_summarycontent.clear()