# Copyright (c) 2018 奥特虾
import requests
import json
import time
import urllib
import hashlib
import datetime
import pymysql
from lxml import etree

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) Appl\
eWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'}

infoList = ['982403','1126614','1073349','991654','1171801','1098909','1099793','1094709','1074591','1537414','1078928','998668','1300069','1101691','1634657','1475249','1283623','1086367','1081356','1067786','1366509','994820','1408932','986515','1491910','990982','1531083','985715']
infoDict = {'982403': '林思意', '1126614': '段艺璇', '1073349': '吴哲晗', '991654': '万丽娜', '1171801': '刘增艳', '1098909': '孙珍妮', '1099793': '姜杉', '1094709': '苏杉杉', '1074591': '许杨玉琢', '1537414': '张怡', '1078928': '宋昕冉', '998668': '杨冰怡', '1300069': '汪束', '1101691': '谢蕾蕾', '1634657': '刘力菲', '1475249': '郑丹妮', '1283623': '唐莉佳', '1086367': '孙芮', '1081356': '钱蓓婷', '1067786': '陈珂', '1366509': '易嘉爱', '994820': '张雨鑫', '1408932': '刘炅然', '986515': '孔肖吟', '1491910': '费沁源', '990982': '刘力菲', '1531083': '陈珂', '985715': '易嘉爱'}

def write(msg):      #记录日志文件的函数
    with open('/var/log/FCC/monitor.log','a+') as f:
        f.write(msg)

def connect_database():    #连接到服务器数据库
    mysql_conn = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': password,
            'db': dbname,
            'charset': 'utf8'
        }
    db = pymysql.connect(**mysql_conn)
    cursor = db.cursor()
    return db

def time_format_conversion(dt):    #将时间转化为时间戳的函数
    timeStamp = time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S"))
    return timeStamp

def getSign(ret):      #生成签名的函数
    tuple = sorted(ret.items(), key=lambda e: e[0], reverse=False)
    md5_string = urllib.parse.urlencode(tuple).encode(encoding='utf_8', errors='strict')
    md5_string += b'&p=das41aq6'
    sign = hashlib.md5(md5_string).hexdigest()[5: 21]
    return sign

def get_taskList():       #从数据库查询已有任务列表
    taskList = []
    db = connect_database()
    cursor = db.cursor()
    cursor.execute("SELECT pro_id FROM monitor_proid")
    results = cursor.fetchall()
    for pro_id in results:
        pro_id = pro_id[0]
        taskList.append(pro_id)
    return taskList

def check_task(user_id):           #从摩点用户主页获取已经开始的任务列表
    proidList = []
    url = 'https://me.modian.com/user?type=index&id='
    url = url + str(user_id)
    html = requests.get(url).content
    selector = etree.HTML(html)
    infos = selector.xpath('//*[@class="prothumb"]/a[1]')
    for info in infos:
        projectUrl = info.xpath('@href')[0].split('.html')[0]
        proid = projectUrl[34:]
        proidList.append(proid)
    return proidList

def add_task(pro_id,idol_name,user_id):             #自动添加任务至数据库
    db = connect_database()
    cursor = db.cursor()
    for pro_id in check_task(user_id):
        if pro_id not in get_taskList():
            response = get_response(pro_id)
            status = 0
            pro_name = response['data'][0]['pro_name']
            already_raised = response['data'][0]['already_raised']
            cursor.execute("insert into monitor_proid values (%s,%s)",(idol_name,pro_id))
            cursor.execute("insert into monitor values (%s,%s,%s,%s,%s)",(idol_name,pro_id,pro_name,already_raised,status))
            db.commit()
            msg = str(time.strftime("%a %b %d %H:%M:%S", time.localtime())) + '  '+ \
        '[WARNING] '+ pro_name + ' ' + pro_id + ' 已上线\n'
            write(msg)

def get_response(pro_id):      #从rankings接口获取数据
    db = connect_database()
    cursor = db.cursor()
    url = 'https://wds.modian.com/api/project/detail'
    form = {
        'pro_id': pro_id
    }
    sign = getSign(form)
    form['sign'] = sign
    response = requests.post(url, form, headers=header).json()
    return response

def querry_database():         #从数据库查询正在进行中的任务
    db = connect_database()
    cursor = db.cursor()
    cursor.execute("SELECT pro_id FROM monitor WHERE status = 0")
    results = cursor.fetchall()
    msg = str(time.strftime("%a %b %d %H:%M:%S", time.localtime())) + '  '+ \
        '[INFO] 数据更新完成\n'
    write(msg)
    for pro_id in results:
        pro_id = pro_id[0]
        check_data(pro_id)

def check_data(pro_id):         #更新各竞争对手集资总额数据
    db = connect_database()
    cursor = db.cursor()
    response = get_response(pro_id)
    pro_name = response['data'][0]['pro_name']
    already_raised = response['data'][0]['already_raised']
    endtime = time_format_conversion(response['data'][0]['end_time'])
    if float(endtime) > float(time.time()):
        status = 0
    else:
        cursor.execute("update monitor set status = 1 where pro_id = (%s)", (pro_id))
        msg = str(time.strftime("%a %b %d %H:%M:%S", time.localtime())) + '  '+ \
        '[WARNING] '+ pro_name + ' ' + pro_id +' 已结束\n'
        write(msg)
    cursor.execute("update monitor set already_raised = (%s) where pro_id = (%s)", (already_raised,pro_id))
    db.commit()
    db.close()

def add_task_start():    #自动添加任务的主函数
    for user_id in infoList:
        idol_name = infoDict[user_id]
        for pro_id in check_task(user_id):
            add_task(pro_id,idol_name,user_id)

def main():      #主程序函数
    querry_database()
    add_task_start()


if __name__ == '__main__':
    main()


