import pymysql
import requests

from KeywordExtraction import KeywordExtraction


def handle_reports(db, reports):
    dbc = db.cursor()
    # dbc.execute("DROP TABLE IF EXISTS reports")
    # sql = """CREATE TABLE reports (
    #     id VARCHAR(36) NOT NULL,
    #     schlagworte TEXT,
    #     zusammenfassung TEXT,
    #     PRIMARY KEY (id) )"""
    # dbc.execute(sql)


    keywordextaction = KeywordExtraction()
    i = -1

    # bug = requests.get('http://extractor.f4.htw-berlin.de/report_id/30162c5b-1e11-4fec-9987-3affca6257e6').json()
    # keywords = keywordextaction.extract_keywords(bug['inhalt'], bug['fachbegriffe'])

    for report in reports:
    # for i in range(614, 1000):
    #     report = reports[i]
        keywords = ''
        summary = ''
        i += 1

        try:
            r = requests.get('http://extractor.f4.htw-berlin.de/report_id/' + report['id']).json()
            terms = r['fachbegriffe']
        except Exception as e:
            print(e)
            terms = {}
            print('Calculation of terms failed for report ' + report['id'])

        try:
            keywords = keywordextaction.extract_keywords(report['inhalt'], terms)
        except Exception as e:
            print(e)
            print('Keyword extraction failed for report ' + str(i) + 'id: ' + report['id'])

        try:
            summary = keywordextaction.extract_sentences(report['inhalt'], terms)
        except Exception as e:
            print(e)
            print('Sentence extraction failed for report ' + str(i) + 'id: ' + report['id'])

        sql = """INSERT INTO reports VALUES (%s, %s, %s)"""

        try:
            dbc.execute(sql, (report['id'], keywords, summary))
            db.commit()
            # print('Inserted report ' + report['id'])
        except Exception as e:
            print(e)
            db.rollback()
            print('Insert failed for report ' + report['id'])


def handle_articles(db, articles):
    dbc = db.cursor()

    # dbc.execute("DROP TABLE IF EXISTS articles")
    # sql = """CREATE TABLE articles (
    #     id VARCHAR(36) NOT NULL,
    #     schlagworte TEXT,
    #     zusammenfassung TEXT,
    #     PRIMARY KEY (id) )"""
    # dbc.execute(sql)

    # articles = requests.get('http://cmts3.f4.htw-berlin.de:8000/articles?page=3').json()
    keywordextaction = KeywordExtraction()
    i = -1

    for article in articles:
    #for i in range(23, 1000):
        # article = articles[i]
        keywords = ''
        summary = ''
        i += 1
        try:
            keywords = keywordextaction.extract_keywords(article['inhalt'])
        except Exception as e:
            print(e)
            print('Keyword extraction failed for article ' + str(i) + 'id: ' + article['id'])

        try:
            summary = keywordextaction.extract_sentences(article['inhalt'])
        except Exception as e:
            print(e)
            print('Sentence extraction failed for article ' + str(i) + ' id: ' + article['id'])

        sql = """INSERT INTO articles VALUES (%s, %s, %s)"""
        try:
            dbc.execute(sql, (article['id'], keywords, summary))
            db.commit()
            # print('Inserted article ' + article['id'])
        except Exception as e:
            print(e)
            db.rollback()
            print('Insert failed for article ' + article['id'])


db = pymysql.connect('db.f4.htw-berlin.de', 's0539720', 'Start123#', '_s0539720__reports', charset='utf8')

for i in range(4, 24):
    articles = requests.get('http://cmts3.f4.htw-berlin.de:8000/articles?page=' + str(i)).json()
    handle_articles(db, articles)
    print("seite " + i + " fertig")

db.close()
