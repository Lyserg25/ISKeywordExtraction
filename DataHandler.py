import requests
import pymysql
from KeywordExtraction import KeywordExtraction

# db = pymysql.connect('localhost', 'root', 'PASSWORD', 'reportsdb', charset='utf8')
db = pymysql.connect('db.f4.htw-berlin.de', 's0539720', 'PASSWORD', '_s0539720__reports', charset='utf8')
dbc = db.cursor()
dbc.execute("DROP TABLE IF EXISTS reports")
sql = """CREATE TABLE reports (
    id INT UNSIGNED NOT NULL,
    schlagworte TEXT,
    zusammenfassung TEXT,
    PRIMARY KEY (id) )"""
dbc.execute(sql)

r = requests.get('http://cmts1.f4.htw-berlin.de/web/index_dev.php/getMissions/10/0')
content = r.json()
keywordextaction = KeywordExtraction()

for item in content:
    keywords = keywordextaction.extract_keywords(item['inhalt'])
    summary = keywordextaction.extract_sentences(item['inhalt'])
    sql = """INSERT INTO reports VALUES (%s, %s, %s)"""
    try:
        dbc.execute(sql, (item['id'], keywords, summary))
        db.commit()
        print('Inserted report ' + item['id'])
    except:
        db.rollback()
        print('Insert failed for report ' + item['id'])

db.close()