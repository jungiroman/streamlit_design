import streamlit as st
import mysql.connector
import pandas as pd
from textblob import TextBlob
from gensim.parsing.preprocessing import remove_stopwords
import re


@st.experimental_memo(ttl=3600)
def read_from_db(query):
    db = mysql.connector.connect(**st.secrets["design"])
    cursor = db.cursor()
    cursor.execute(query)
    fetched = cursor.fetchall()
    return fetched


def process_text(text):
    text = text.lower()
    text = re.sub(r'[.,"\'-?:!;’‘]', '', text)
    text = remove_stopwords(text)
    text = " ".join([word.lemmatize() for word in TextBlob(text).words])
    return text


if __name__ == "__main__":
    st.set_page_config(page_title="design feed", page_icon="random", layout="wide")
    st.title('design feed')
    if 'page' not in st.session_state:
        st.session_state['page'] = 0

    start = st.session_state['page'] * 10
    categories = list(x[0] for x in read_from_db("SELECT DISTINCT category FROM articles"))

    query = "SELECT * FROM articles ORDER BY published DESC LIMIT "+str(start)+",10"
    with st.sidebar:
        with st.form('filter'):
            selected_categories = st.multiselect('Categories', categories)
            text_search = st.text_input('Search term')
            set_filter = st.form_submit_button('Filter')

        if set_filter:
            where_clause = []
            if selected_categories:
                s_cat = "('" + "', '".join(selected_categories) + "')"
                where_clause.append("category IN " + s_cat)

            if text_search:
                term = process_text(text_search)
                where_clause.append("search_text LIKE '%" + term + "%'")

            if where_clause:
                clause = " WHERE " + " AND ".join(where_clause)
            else:
                clause = ""

            query = "SELECT * FROM articles" + clause + " ORDER BY published DESC LIMIT "+str(start)+",10"

            st.write(query)
        if st.button("Clear cache"):
            st.experimental_memo.clear()

    data = pd.DataFrame(read_from_db(query))

    if not data.empty:
        column_query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'articles' AND TABLE_SCHEMA = '" + \
                        st.secrets['design']['database'] + "'"
        data.columns = (x[0] for x in read_from_db(column_query))

        for ind, article in data.iterrows():
            url = article.link
            title = article.title

            first_image = article.first_image
            images = article.images.split(';')

            col1, col2 = st.columns(2)
            with col1:
                st.write("### " + title)
                published = article.published
                authors = article.authors
                st.write(str(published) + "  /  " + authors)
                summary = article.summary
                st.markdown(summary, unsafe_allow_html=True)

            with col2:
                st.markdown(f'''
                                    <a href="{url}">
                                        <img src="{first_image}" style="width:100%" alt="{url}" />
                                    </a>''',
                            unsafe_allow_html=True
                            )
                with st.expander('More images', expanded=False):
                    for img in images:
                        st.image(img)

            st.write('---')

    else:
        st.info('Query returned no data.')

    col1, col2, col3, col4 = st.columns(4)
    if st.session_state['page'] > 0:
        if col1.button('First page'):
            st.session_state['page'] = 0
            st.experimental_rerun()
    if st.session_state['page'] > 1:
        if col2.button('Previous page'):
            st.session_state['page'] = st.session_state['page'] - 1
            st.experimental_rerun()
    col3.write("Page: " + str(st.session_state['page'] + 1))

    if not data.empty:
        if col4.button('Next page'):
            st.session_state['page'] = st.session_state['page'] + 1
            st.experimental_rerun()
