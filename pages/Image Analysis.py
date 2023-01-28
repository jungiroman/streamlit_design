import streamlit as st


def hide_header():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(page_title="design feed", page_icon="🤖", layout="wide")
    hide_header()
    st.title('design feed - image analysis')
