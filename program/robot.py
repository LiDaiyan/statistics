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
    
    info = request.values.get("clock").replace('\n', '').replace('\r', '')
    # info = "打卡：4：学习英语和物理：zhangjie"
    list = re.split(':|：', info)
    if len(list) != 4:
        return "打卡失败，冒号使用不规范"
    
    name = list[3]
    content = list[2]
    val = list[1]

    array = ["1", "2", "3", "4", "5"]
    if(val not in array):
        return "打卡失败，数值错误"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    time_format = "%Y-%m-%d"
    # number = datetime.datetime.now().weekday()

    # today = datetime.date.today()
    # yesterday = today - datetime.timedelta(days=1)
    # day_befor_yesterday = today - datetime.timedelta(days=2)

    # today_str = today.strftime(time_format)
    # yesterday_str = yesterday.strftime(time_format)
    # day_before_yesterday_str = day_befor_yesterday.strftime(time_format)

    # # 判断今天是不是周日
    # if(number == 6):
    #     # 判断周六即昨天有没有打卡，如果没打卡就把周五当作昨天
    #    select_sql = "select * from clock where name = \"{0}\" and date = \"{1}\"".format(name, yesterday_str)
    #    query_result = cursor.execute(select_sql).rowcount
    #    if(query_result == 0):
    #        yesterday = today - datetime.timedelta(days=2)
    #        yesterday_str = yesterday.strftime(time_format)

    # # 判断今天是不是周一
    # elif(number == 0):
    #     # 判断周六周日有没有打卡，如果没打卡就把周五当作昨天，如果打了卡就把最后一次打卡那天当作昨天
    #     select_sql = "select * from clock where name = \"{0}\" and (date = \"{1}\" or date = \"{2}\")".format(name, yesterday_str, day_before_yesterday_str)
    #     query_result = cursor.execute(select_sql).fetchall()
    #     if(len(query_result) == 0):
    #         yesterday = today - datetime.timedelta(days=3)
    #         yesterday_str = yesterday.strftime(time_format)
    #     else:
    #         yesterday_str = query_result[-1][-1]

    # #判断今天该成员是否已打卡
    # select_sql = "select * from clock where name = \"{0}\" and date = \"{1}\"".format(name, today_str)
    # query_result = cursor.execute(select_sql).rowcount

    # if(query_result != 0):
    #     delete_sql = "delete from clock where name = \"{0}\" and date = \"{1}\"".format(name, today_str)
    #     cursor.execute(delete_sql)

    # # 更新今天计划完成情况
    # update_sql = "update clock set val = {0} where name = \"{1}\" and date = \"{2}\"".format(val, name, yesterday_str)
    # cursor.execute(update_sql)

    # # 插入明天学习计划
    # sql = "insert into clock values(\"{0}\", \"{1}\", null, \"{2}\")".format(name, content, today_str)
    # cursor.execute(sql)


    today = datetime.date.today()
    today_str = today.strftime(time_format)
    # today_str = "2021-06-27"
    #判断今天该成员是否已打卡
    select_sql = "select * from clock where name = \"{0}\" and date = \"{1}\"".format(name, today_str)
    query_result = cursor.execute(select_sql).rowcount

    if(query_result != 0):
        delete_sql = "delete from clock where name = \"{0}\" and date = \"{1}\"".format(name, today_str)
        cursor.execute(delete_sql)
    # 插入今日学习情况
    sql = "insert into clock values(\"{0}\", \"{1}\", {2}, \"{3}\")".format(name, content, val, today_str)
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
