import streamlit as st
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS
import nltk
from nltk import ne_chunk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from gensim.corpora import Dictionary
from gensim.models import LdaModel
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')


def hide_header():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


def analyze_sentiment(titles, summaries, search_texts):
    st.write('### Sentiment analysis')

    def _analyze_sentiment(texts):
        for text in texts:
            sentiment = TextBlob(text).sentiment
            st.write(text + " / Polarity: " + str(sentiment.polarity) + " / Subjectivity: " + str(
                sentiment.subjectivity))
        st.write('---')

    with st.expander('show'):
        _analyze_sentiment(titles)
        _analyze_sentiment(summaries)
        _analyze_sentiment(search_texts)


def analyze_ner(titles, summaries, search_texts):
    st.write('### Named entity recognition')

    def _analyze_ner(texts):
        for text in texts:
            named_entities = ne_chunk(nltk.pos_tag(word_tokenize(text)))
            st.write(text + " / NER: ")
            st.write(named_entities)
        st.write('---')

    with st.expander('show'):
        _analyze_ner(titles)
        _analyze_ner(summaries)
        _analyze_ner(search_texts)


def prep(texts):
    stemmer = PorterStemmer()

    # Get list of stopwords
    stop_words = set(stopwords.words("english"))

    # Preprocess the headlines
    preprocessed_headlines = []
    for headline in texts:
        # Tokenize the headline
        headline_tokens = word_tokenize(headline)

        # Remove stopwords and stem the tokens
        headline_tokens = [stemmer.stem(token) for token in headline_tokens if token not in stop_words]

        # Join the preprocessed tokens back into a single headline
        preprocessed_headline = " ".join(headline_tokens)
        preprocessed_headlines.append(preprocessed_headline)

    # Pass the preprocessed headlines to the LDA model
    return preprocessed_headlines

def model_topic(titles, summaries, search_texts):
    st.write('### Topic modeling')

    def _model_topic(texts):
        texts = prep(texts)
        texts = [headline.split() for headline in texts]
        dictionary = Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        lda = LdaModel(corpus, num_topics=5)
        for topic in lda.print_topics():
            st.write(topic)

    with st.expander('show'):
        st.write('Titles:')
        _model_topic(titles)
        st.write('Summaries:')
        _model_topic(summaries)
        st.write('Search texts:')
        _model_topic(search_texts)


def analyse_text():
    titles = list(st.session_state['data']['title'])
    summaries = list(st.session_state['data']['summary'])
    search_texts = list(st.session_state['data']['search_text'])

    analyze_sentiment(titles, summaries, search_texts)
    analyze_ner(titles, summaries, search_texts)
    model_topic(titles, summaries, search_texts)

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

if __name__ == "__main__":
    st.set_page_config(page_title="design feed", page_icon="🤖", layout="wide")
    hide_header()
    st.title('design feed - text analysis')
    if 'data' in st.session_state:
        analyse_text()
    else:
        st.warning('No data. Go to feed page first')
