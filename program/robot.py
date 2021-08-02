from flask import Flask, request
import datetime
from datetime import timedelta
import sqlite3
import re
from pathlib import Path

app = Flask(__name__)
db_path = Path(__file__).parent.parent / "data" / "clock.db"
text_path = Path(__file__).parent.parent / "data" / "text_data"
week_sum_path = Path(__file__).parent.parent / "data" / "week_sum"
month_sum_path = Path(__file__).parent.parent / "data" / "month_sum"

time_format = "%Y-%m-%d"

dic = {1:"一", 2:"二", 3:"三", 4:"四", 5:"五", 6:"六", 7:"七", 8:"八", 9:"九", 10:"十", 11:"十一", 12:"十二"}

@app.route('/')
def index():
    
    info = request.values.get("clock").replace('\n', '').replace('\r', '').replace(' ', '')
    date = request.values.get("date")
    # info = "打卡：4：学习英语和物理：zhangjie"
    list = re.split(':|：', info)
    if len(list) != 4:
        return "打卡失败，冒号使用不规范"
    
    name = list[3]
    content = list[2]
    val = list[1]

    try:
        float(val)
    except ValueError:
        return "打卡失败，数值错误"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
    # 参数中有日期则使用参数日期
    if date:
        today_str = date
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

@app.route('/week')
def week_sum():
    return sum(1)

@app.route('/month')
def month_sum():
    return sum(2)

def sum(type):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    today = datetime.date.today()
    # 统计周数据
    if(type == 1):
        date_begin = (today -timedelta(days=today.weekday() + 7)).strftime(time_format)
        date_end = (today - timedelta(days=today.weekday() + 1)).strftime(time_format)
        file_name = date_begin[-5:] + " - " + date_end[-5:] + " 打卡统计"
        path = week_sum_path / (file_name + ".md")
    # 统计月数据
    else:
        last_day_last_month = datetime.datetime(today.year, today.month, 1) - timedelta(days=1)
        first_day_last_month = datetime.datetime(last_day_last_month.year, last_day_last_month.month, 1)
        date_begin = first_day_last_month.strftime(time_format)
        date_end =  last_day_last_month.strftime(time_format)
        file_name = dic[first_day_last_month.month] + "月打卡统计"
        path = month_sum_path / (file_name + ".md")


    select_sum = "select name, count(val), round(avg(val), 2) as val_avg from clock where date >=  \"{0}\" and date <=  \"{1}\" group by name".format(date_begin, date_end)
    result = cursor.execute(select_sum)

    text = "**{0}**\n\n| 打卡人     | 打卡次数 | 自我评价 | 计划完成情况   |\n| ---------- | -------- | -------- | -------------- |\n".format(file_name)
    for i in result:
        text = text+ "|" + str(i[0]) + "|" + str(i[1]) + "|" + str(i[2]) + "|" + get_evaluate(i[2]) + "|\n"
    
    f = open(path, 'w', encoding="utf-8")
    f.write(text + "\n\n")

    return file_name + "已打印"

def print_today(info, today_str):
    path = text_path / (today_str + ".txt")
    f = open(path, 'a', encoding="utf-8")
    print(path)
    f.write(info + "\n\n")

def get_evaluate(num):
    if(num >= 0 and num <= 1.5):
        return "毫无进展"
    elif(num > 1.5 and num <= 2.5):
        return "进展缓慢"
    elif(num > 2.5 and num <= 3.5):
        return "完成大部分计划"
    elif(num > 3.5 and num <= 4.6):
        return "完成计划"
    
    return "超额完成"


app.run(host='0.0.0.0', port=5000)
