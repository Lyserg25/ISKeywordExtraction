import hug
import pymysql

@hug.get()
def reports(id=None):
    if id is None:
        sql = "SELECT * FROM reports"
    elif isinstance(id, int):
        sql = "SELECT * FROM reports WHERE id=" + str(id)
    else:
        return []
    # db = pymysql.connect('localhost', 'root', 'PASSWORD', 'reportsdb', charset='utf8')
    db = pymysql.connect('db.f4.htw-berlin.de', 's0539720', 'PASSWORD', '_s0539720__reports', charset='utf8')
    dbc = db.cursor()
    try:
        dbc.execute(sql)
        results = dbc.fetchall()
    except:
        print("Error: unable to fetch data")

    db.close()
    return [{'id': report[0], 'schlagworte': report[1], 'zusammenfassung': report[2]} for report in results]

