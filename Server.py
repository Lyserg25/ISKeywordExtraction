import re

import hug
import pymysql

ID_PATTERN = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
REPORTS = "reports"
ARTICLES = "articles"


@hug.get()
def reports(id: str = None):
    return get_from_db(REPORTS, id)


@hug.get()
def articles(id: str = None):
    return get_from_db(ARTICLES, id)


def get_from_db(type, id):
    if id is None:
        sql = "SELECT * FROM " + type
    elif not ID_PATTERN.match(id):
        return []
    else:
        sql = "SELECT * FROM " + type + " WHERE id='" + id + "'"

    try:
        db = pymysql.connect('db.f4.htw-berlin.de', 's0539720', 'Start123#', '_s0539720__reports', charset='utf8')
        dbc = db.cursor()
        dbc.execute(sql)
        results = dbc.fetchall()
        db.close()
        return [{'id': report[0], 'schlagworte': report[1], 'zusammenfassung': report[2]} for report in results]
    except Exception as e:
        print(e)
    return []
