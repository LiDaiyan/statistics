from flask import Flask, request
import datetime
import sqlite3
import re
from pathlib import Path

app = Flask(__name__)
db_path = Path(__file__).parent.parent / "data" / "clock.db"
text_path = Path(__file__).parent.parent / "data" / "text_data"


@app.route('/')
def index():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    info = request.values.get("clock")
    # info = "打卡：4：学习英语和物理：zhangjie"

    list = re.split(':|：', info)

    name = list[3]
    content = list[2]
    val = list[1]

    if len(list) != 4:
        return "打卡失败"

    time_format = "%Y-%m-%d"
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    today_str = today.strftime(time_format)
    yesterday_str = yesterday.strftime(time_format)

    #判断今天该成员是否已打卡
    select_sql = "select * from clock where name = \"{0}\" and date = \"{1}\"".format(name, today_str)
    print(select_sql)
    query_result = cursor.execute(select_sql).rowcount

    if(query_result != 0):
        delete_sql = "delete from clock where name = \"{0}\" and date = \"{1}\"".format(name, today_str)
        cursor.execute(delete_sql)

    
    update_sql = "update clock set val = {0} where name = \"{1}\" and date = \"{2}\"".format(val, name, yesterday_str)
    cursor.execute(update_sql)



    sql = "insert into clock values(\"{0}\", \"{1}\", null, \"{2}\")".format(name, content, today_str)

    print(sql)
    cursor.execute(sql)

    conn.commit()
    conn.close()
    print_today(info, today_str)

    return "打卡成功"

def print_today(info, today_str):
    path = text_path / (today_str + ".txt")
    f = open(path, 'a', encoding="utf-8")
    print(path)
    f.write(info + "\n\n")


app.run(host='0.0.0.0', port=5000)

