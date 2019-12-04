# parse
import os
import xml.etree.cElementTree as et
from urllib.request import urlopen
from xml.etree.ElementTree import parse

# gen plot
import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

# gen wordcloud
import pandas as pd
from nltk import sent_tokenize, pos_tag
from nltk.stem import PorterStemmer
from wordcloud import WordCloud
# gen html
from yattag import Doc

# keyword gen
from project_p2_ex3 import run


class Helper:
    @staticmethod
    def printDict(d):
        for item in d:
            print(item, "-> ", d[item])


def getXML(url):
    open_url = urlopen(url)
    xml = parse(open_url)
    return xml


def formatDocuments(xml):
    documents = dict()

    for item in xml.iterfind('channel/item'):
        title = item.findtext('title')
        description = item.findtext('description')
        documents[title] = description

    return documents


def plotKeyphrases(csvFile):
    df = pd.read_csv(csvFile)

    plt.figure(figsize=(15, 10))
    df.groupby("word").max().sort_values(by="weight", ascending=False)["weight"].plot.bar()
    plt.xticks(rotation=50)
    plt.xlabel("Word")
    plt.ylabel("Weight")
    # plt.show()
    # plt.savefig('books_read.png') #save to file


def generateWordCloud(documents):
    counter = 1
    for title in documents:
        wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(documents[title])
        path = "img/" + str(counter) + ".png"
        wordcloud.to_file(path)
        counter += 1


def generateHTML(documents):
    doc, tag, text = Doc().tagtext()

    with tag('html'):
        with tag('body'):
            counter = 1
            for title in documents:
                with tag('div', id='news', align='center'):
                    with tag('h1'):
                        text("Title:")

                    text(title)

                    with tag('h1'):
                        text("Description:")

                    text(documents[title])

                    with tag('h1'):
                        text("Wordcloud:")

                    with tag('div', id='photo-container'):
                        path = "img/" + str(counter) + ".png"
                        doc.stag('img', src=path, klass="photo")

                    counter += 1

                with tag('br'):
                    pass

    return doc.getvalue()


def createNewsFiles(documents, category: str):
    porter = PorterStemmer()

    for i, title in enumerate(documents):
        sentenceCounter = 1
        wordCounter = 1

        root = et.Element("root")
        document = et.SubElement(root, "document")
        sentences = et.SubElement(document, "sentences")
        for sent in sent_tokenize(documents[title]):
            sentence = et.SubElement(sentences, "sentence")
            sentence.set("id", str(sentenceCounter))
            tokens = et.SubElement(sentence, "tokens")

            print(sent)
            tags = pos_tag(' '.join(sent.split()).split(" "))
            print(tags)
            for word in tags:
                token = et.SubElement(tokens, "token")
                token.set("id", str(wordCounter))
                et.SubElement(token, "lemma").text = porter.stem(word[0])
                et.SubElement(token, "POS").text = word[1]

                wordCounter += 1

            sentenceCounter += 1

        tree = et.ElementTree(root)
       # tree.write("news/" + title.replace(" ", "_") + ".xml")

        path = f'news/{category}/'

        if not os.path.exists(path):
            os.makedirs(path)

        tree.write(path + str(i) + ".xml")

def fetchCategory(category: str):
    BASE_URL = 'https://rss.nytimes.com/services/xml/rss/nyt/'
    xml = getXML(f'{BASE_URL + category}.xml')
    documents = formatDocuments(xml)
    createNewsFiles(documents, category)
    keywords = run(f'news/{category}')

def main():
    cats = ['Technology', 'World', 'US', 'HomePage', 'Politics']
    with open("page.html", "w"):
        for category in cats:
            fetchCategory(category)

            # Helper.printDict(keywords)

            # plotKeyphrases("pr.csv")

            # generateWordCloud(documents)

            # text_file = open("page.html", "w")
            # text_file.write(generateHTML(documents))


if __name__ == "__main__":
    main()