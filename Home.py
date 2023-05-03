import os
import time
import json
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from functional import SearchEngine, SummaryContent
from utils import search, form_summarycontent, clear
import hashlib

st.set_page_config(
    page_title="NewsGPT",
    page_icon="👋",
    layout="wide"
)

if "OPENAI_API_KEY" not in st.session_state:
    st.session_state.update({"OPENAI_API_KEY": "unknown"})

if "current_search" not in st.session_state:
    st.session_state["current_search"] = ""

if "search_history" not in st.session_state:
    st.session_state["search_history"] = {}

st.session_state["search_engine"] = SearchEngine(lang='en', region='US')

c1, c2, c3 = st.columns([2,2,2])

with st.sidebar:
    if st.session_state["OPENAI_API_KEY"] == "unknown":
        password = st.text_input(
            "Enter OpenAI-APIKEY 👇",
            label_visibility="visible",
            disabled=False,
            placeholder="OpenAI-APIKEY",
            type="password",
        )
        is_login = st.button("SUBMIT")
        if is_login:
            st.session_state["OPENAI_API_KEY"] = password
            st.success("Set up successfully!")
            time.sleep(1)
            switch_page("home")
    else:
        st.info("OpenAI-APIKEY is Set Up!")
        is_logout = st.button("LOGOUT")
        if is_logout:
            st.session_state["OPENAI_API_KEY"] = "unknown"
            st.success("Logout Successfully!")
            time.sleep(1)
            switch_page("home")

c2.markdown("<h1 style='text-align:center;padding: 0px 0px;color:grey;font-size:300%;'>NewsGPT</h1><br>", unsafe_allow_html=True)

with c2:
    if st.session_state["current_search"] == "":
        st.markdown(f"<br></br>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;padding: 0px 0px;color:grey;font-size:200%;'>SEARCH</h3><br>", unsafe_allow_html=True)
        search_form = st.form(key="search_form")
        search_text = search_form.text_input('Search News Topic')
        is_submit = search_form.form_submit_button('Start Search')
        if is_submit:
            if "OPENAI_API_KEY" not in st.session_state:
                st.session_state.update({"OPENAI_API_KEY": "unknown"})
            if st.session_state["OPENAI_API_KEY"] == "unknown":
                st.warning("Set the openai key from the sidebar before you start searching...")
                time.sleep(2)
                switch_page("home")
            st.session_state["current_search"] = search_text
            switch_page("home")
    else:
        st.markdown("<h3 style='text-align:center;padding: 0px 0px;color:grey;font-size:200%;'>RESULT</h3><br>", unsafe_allow_html=True)
        st.markdown(f"<br></br>", unsafe_allow_html=True)
        # st.session_state["contents"] = search(keys=st.session_state["current_search"], news_num=10)
        # st.session_state["contents"] = json.loads(st.session_state["contents"])["results"]
        form_summarycontent()
        if "contents" in st.session_state:
            if st.session_state["contents"] is None or len(st.session_state["contents"]) == 0:
                st.warning("No Result")
            else:
                with c2:
                    current_content_len = len(st.session_state["contents"])
                    for content in st.session_state["contents"]:
                        if content.title is None:
                            current_content_len -= 1
                            continue
                        hash_object = hashlib.sha256(content.title.encode())
                        hex_dig = hash_object.hexdigest()
                        if hex_dig in st.session_state["search_history"].keys():
                            continue
                        st.markdown(f'''<h3>{content.title}</h3>''', unsafe_allow_html=True)
                        st.markdown(f'''<strong>{content.media}  |  {content.date}</strong>''', unsafe_allow_html=True)
                        bt_c1, bt_c2 = st.columns([0.2, 0.5])
                        is_summarize = bt_c1.button("Summarize", key=hex_dig+"_summarize")
                        back_to_search = bt_c2.button("Back", key=hex_dig+"_goback")
                        if is_summarize:
                            with st.spinner("Summarizing ..."):
                                if st.session_state["OPENAI_API_KEY"] != "unknown":
                                    if hex_dig not in st.session_state["search_history"].keys():
                                        response, err_list = content.summarize(nums=3, openai_key=st.session_state["OPENAI_API_KEY"])
                                        st.session_state["search_history"][hex_dig] = {"content": content, "response": response}
                                    with st.expander("Summary of 3 Similar Topics"):
                                        st.markdown("### GPT Summary:")
                                        st.image(content.image)
                                        list_tmp = "<li><a href={}>{}</a></li>"
                                        urls = ""
                                        for src, src_url in zip(content.related_src, content.related_src_url):
                                            urls += list_tmp.format(src_url, src)
                                        st.markdown(f"<ul>{urls}</ul>", unsafe_allow_html=True)
                                        if st.session_state["search_history"][hex_dig]["response"] is not None:
                                            st.markdown(st.session_state["search_history"][hex_dig]["response"], unsafe_allow_html=True)
                                        else:
                                            st.error("Could be the following error: openai.error.RateLimitError: That model is currently overloaded with other requests. ")
                                        st.write("error list when processing each article")
                                        st.write(err_list)
                                else:
                                    st.error("something wrong with the api-key, go set it again")
                                    st.session_state.update({"OPENAI_API_KEY": "unknown"})
                        st.divider()

                        if back_to_search:
                            clear()
                            switch_page("home")
                    if current_content_len == 0:
                        st.error("Can't find any topics or the websites block the access for analysis")
                        st.write(st.session_state["raw_contents"])
                        no_content_back = st.button("Back", key="no_content_back")
                        if no_content_back:
                            clear()
                            switch_page("home")