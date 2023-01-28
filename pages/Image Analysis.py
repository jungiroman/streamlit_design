import streamlit as st


def hide_header():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


def analyse_images():
    first_images = st.session_state['data']['first_image']
    images = st.session_state['data']['images']
    st.write(first_images)
    st.write('---')
    st.write(images)


if __name__ == "__main__":
    st.set_page_config(page_title="design feed", page_icon="🤖", layout="wide")
    hide_header()
    st.title('design feed - image analysis')
    if 'data' in st.session_state:
        analyse_images()
    else:
        st.warning('No data. Go to feed page first')
