import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


def hide_header():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


def extract_colors(urls):

    for url in urls:
        # Download image from URL
        #url = "https://images.unsplash.com/photo-1593642532857-b24f09b835e5?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
        # Open image using PIL
        col1, col2 = st.columns(2)

        col1.image(url)

        try:
            img = Image.open(requests.get(url, stream=True).raw)

            # Get all the colors in the image
            colors = img.getcolors(img.size[0] * img.size[1])

            # Extract the RGB values from the color tuples
            rgb_colors = [[color[1][i] for i in range(3)] for color in colors]

            # Apply k-means clustering
            kmeans = KMeans(n_clusters=5, random_state=0).fit(rgb_colors)
            colors = kmeans.cluster_centers_

            col2.empty()
            col2.markdown("<div style='display:flex; justify-content: center; align-items: center;'>",
                        unsafe_allow_html=True)
            for color in colors:
                col2.markdown(
                    f'<div style="background-color: rgba({color[0]}, {color[1]}, {color[2]},1); width:10%; height:50px;"></div>',
                    unsafe_allow_html=True)
            col2.markdown("</div>", unsafe_allow_html=True)



            #for color in colors:
            #    col2.markdown(
            #        f'<span style="background-color: rgba({color[0]}, {color[1]}, {color[2]},1);">&nbsp;&nbsp;&nbsp;&nbsp;</span>', unsafe_allow_html=True)
        except:
            col2.info('Failed to extract colors')



def analyse_images():
    first_images = st.session_state['data']['first_image']
    images = st.session_state['data']['images']

    extract_colors(first_images)
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
