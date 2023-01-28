import streamlit as st
from wordcloud import WordCloud, STOPWORDS


def hide_header():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(page_title="design feed", page_icon="🤖", layout="wide")
    hide_header()
    st.title('design feed - text analysis')
    text = "\n".join(list(st.session_state['data']['search_text']))
    width = 1200
    height = 600
    wordcloud = WordCloud(width=width, height=height, random_state=1, mode='RGBA',
                          background_color=None, colormap='Pastel1',
                          collocations=False, stopwords=STOPWORDS)

    wordcloud_image = wordcloud.generate(text).to_image()
    st.image(wordcloud_image)
    st.write(wordcloud.process_text(text))
    st.write(text)
