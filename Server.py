import hug
import pymysql
import json

@hug.get()
def reports(id: int = None):
    if id is None:
        sql = "SELECT * FROM reports"
    else:
        sql = "SELECT * FROM reports WHERE id=" + str(id)
    # db = pymysql.connect('localhost', 'root', 'PASSWORD', 'reportsdb', charset='utf8')
    db = pymysql.connect('db.f4.htw-berlin.de', 's0539720', 'PASSWORD', '_s0539720__reports', charset='utf8')
    dbc = db.cursor()
    try:
        dbc.execute(sql)
        results = dbc.fetchall()
    except:
        print("Error: unable to fetch data")

    db.close()
    result = [{'id': report[0], 'schlagworte': report[1], 'zusammenfassung': report[2]} for report in results]
    return result

