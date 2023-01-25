import streamlit as st
import mysql.connector
import pandas as pd
from bs4 import BeautifulSoup


@st.experimental_memo(ttl=3600)
def read_from_db():
    db = mysql.connector.connect(**st.secrets["design"])
    cursor = db.cursor()
    table = 'articles'
    columns = "*"
    query = "SELECT " + columns + " FROM " + table #+ condition
    cursor.execute(query)
    f = cursor.fetchall()
    df = pd.DataFrame(f)
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '" + table + "' AND TABLE_SCHEMA = 'u831348299_rj_design'")
    xs = cursor.fetchall()
    df.columns = (x[0] for x in xs)
    return df


if __name__ == "__main__":
    st.set_page_config(page_title="Design", page_icon=":newspaper:", layout="wide")
    st.title('designboom')
    data = read_from_db()
    data = data.sort_values(by=['published'], ascending=False)
    data.reset_index(inplace=True, drop=True)

    st.write(data)


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
            #if st.button('Load images', key="btn"+str(ind)):
            with st.expander('More images', expanded=False):
                for img in images:
                    st.image(img)

        with col2:
            st.markdown(f'''
                                <a href="{url}">
                                    <img src="{first_image}" style="width:100%" alt="{url}" />
                                </a>''',
                        unsafe_allow_html=True
                        )

        st.write('---')


        #st.write(article[7])




