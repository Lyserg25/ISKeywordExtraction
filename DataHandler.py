import pymysql
import requests

from KeywordExtraction import KeywordExtraction


def handle_reports(db):
    dbc = db.cursor()
    # dbc.execute("DROP TABLE IF EXISTS reports")
    # sql = """CREATE TABLE reports (
    #     id VARCHAR(36) NOT NULL,
    #     schlagworte TEXT,
    #     zusammenfassung TEXT,
    #     PRIMARY KEY (id) )"""
    # dbc.execute(sql)

    reports = requests.get('http://cmts3.f4.htw-berlin.de:8000/reports?page=1').json()
    keywordextaction = KeywordExtraction()
    i = -1

    # bug = requests.get('http://extractor.f4.htw-berlin.de/report_id/30162c5b-1e11-4fec-9987-3affca6257e6').json()
    # keywords = keywordextaction.extract_keywords(bug['inhalt'], bug['fachbegriffe'])

    for report in reports:
        # for i in range(33, 1000):
        # report = reports[i]
        keywords = ''
        summary = ''
        i += 1

        try:
            r = requests.get('http://extractor.f4.htw-berlin.de/report_id/' + report['id']).json()
            terms = r['fachbegriffe']
        except:
            terms = {}
            print('Calculation of terms failed for report ' + report['id'])

        try:
            keywords = keywordextaction.extract_keywords(report['inhalt'], terms)
        except:
            print('Keyword extraction failed for report ' + str(i) + 'id: ' + report['id'])

        try:
            summary = keywordextaction.extract_sentences(report['inhalt'], terms)
        except:
            print('Sentence extraction failed for report ' + str(i) + 'id: ' + report['id'])

        sql = """INSERT INTO reports VALUES (%s, %s, %s)"""

        try:
            dbc.execute(sql, (report['id'], keywords, summary))
            db.commit()
            # print('Inserted report ' + report['id'])
        except:
            db.rollback()
            print('Insert failed for report ' + report['id'])


def handle_articles(db):
    dbc = db.cursor()

    # dbc.execute("DROP TABLE IF EXISTS articles")
    # sql = """CREATE TABLE articles (
    #     id VARCHAR(36) NOT NULL,
    #     schlagworte TEXT,
    #     zusammenfassung TEXT,
    #     PRIMARY KEY (id) )"""
    # dbc.execute(sql)

    articles = requests.get('http://cmts3.f4.htw-berlin.de:8000/articles?page=1').json()
    keywordextaction = KeywordExtraction()
    i = -1

    for article in articles:
    #for i in range(14, 1000):
     #   article = articles[i]
        keywords = ''
        summary = ''
        i += 1
        try:
            keywords = keywordextaction.extract_keywords(article['inhalt'])
        except:
            print('Keyword extraction failed for article ' + str(i) + 'id: ' + article['id'])

        try:
            summary = keywordextaction.extract_sentences(article['inhalt'])
        except:
            print('Sentence extraction failed for article ' + str(i) + ' id: ' + article['id'])

        sql = """INSERT INTO articles VALUES (%s, %s, %s)"""
        try:
            dbc.execute(sql, (article['id'], keywords, summary))
            db.commit()
            # print('Inserted article ' + article['id'])
        except:
            db.rollback()
            print('Insert failed for article ' + article['id'])


db = pymysql.connect('db.f4.htw-berlin.de', 's0539720', 'Start123#', '_s0539720__reports', charset='utf8')
# handle_articles(db)
handle_reports(db)
db.close()
