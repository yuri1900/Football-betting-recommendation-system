#!/usr/bin/python
# coding:utf-8
import requests
from bs4 import BeautifulSoup
import re #正则表达式库
import traceback #为了调试方便
import pymysql
import json
import csv

def getHTMLText(url): #获得url页面的函数
#url ="http://info.sporttery.cn/football/match_result.php?page=1&search_league=0&start_date=2019-01-31&end_date=2019-02-02&dan=0"
#http://info.sporttery.cn/football/match_result.php
#url= "http://info.sporttery.cn/football/match_result.php?page=2&search_league=0&start_date=2019-01-31&end_date=2019-02-02&dan=0"
#http://info.sporttery.cn/football/match_result.php?page=2&search_league=0&start_date=2019-01-31&end_date=2019-02-02&dan=0
#http://info.sporttery.cn/football/match_result.php?page=3&search_league=0&start_date=2019-01-31&end_date=2019-02-02&dan=0
    try:
        kv = {'user-agent': 'Mozilla/5.0'} #构造一个键值对，重新定义user-agent的内容
        r= requests.get(url, headers =kv, timeout =30)
        r.raise_for_status()  #返回状态码信息
        r.encoding = r.apparent_encoding #更改编码为我们可阅读的编码
        return r.text
        print(r.status_code)   #200表示返回信息正确
        print(r.request.headers)
        #print(r.text[:1000])   #查看返回内容是否正确
    except:
        return ""
        print("爬取失败")


def parsePage(ilt, html): #对于每一个获得的页面进行解析,关键列表信息 ilt information list
    #soup = BeautifulSoup(html, "html.parser") #解析每一个页面
    #print(soup.prettify())  # 在每一个标签后加了一个换行符\
    #for tag in soup.find_all(True):
    # print(tag.name)
    try:
        dlt = re.findall('<td width="101">(.*?)</td>',html)   #列表类型#获取赛事日期
        wlt = re.findall('<td width="104">(.*?)</td>',html)   #获取赛事编号
        tylt = re.findall('<td width="112".*?>(.*?)</td>',html)  #获取联赛
        mtelt = re.findall('<td width="300".*?><a href=.*?"><span class="zhu".*?">(.*?)</span>',html)   #获取主队队名
        stelt = re.findall('<td width="300".*?><a href=".*">(.*?)</span>',html)   #获取客队队名
        slt = re.findall('<td width="60">.*?13px;">(.*?)</span></td>',html)  #获取全场比分
        pattern = re.compile('<tr>.*?<td width="55"><span.*?>(.*?)</span>.*?</tr>', re.S)
        olt1 = re.findall(pattern, html)  #获取赔率
        pattern = re.compile('<tr>.*?<td width="55"><span.*?</span>.*?<td width="55"><span.*?>(.*?)</span>.*?</tr>', re.S)
        olt2 = re.findall(pattern, html)  # 获取赔率
        pattern = re.compile('<tr>.*?<td width="55"><span.*?</span>.*?<td width="55"><span.*?</span>.*?<td width="55"><span.*?>(.*?)</span>.*?</tr>', re.S)
        olt3 = re.findall(pattern, html)  # 获取赔率
        flt = re.findall('<td width="86">(.*?)</td>',html)  #获取比赛完成情况
        for i in range(len(dlt)):     #i表示循环计数，range(N)产生0到N-1的整数序列
            date = dlt[i]   #获取赛事日期
            week = wlt[i]   #获取赛事编号
            type = tylt[i]  #获取联赛
            mteam = mtelt[i]  # 获取主队队名
            steam = stelt[i]  # 获取客队队名
            scroe = slt[i]  #获取比赛结果
            odds1 = olt1[i]   #获取胜赔率
            odds2 = olt2[i]  # 获取平赔率
            odds3 = olt3[i]  # 获取负赔率
            finish = flt[i]  # 获取比赛完成情况
            ilt.append([date,week,type,mteam,steam,scroe,odds1,odds2,odds3,finish])
            #存储到列表ilt中


    except:
        traceback.print_exc()  #获得其中的错误信息
        print("")


def printDataList(ilt):  #将信息输出到屏幕上
    tplt = "{:4}\t{:8}\t{:8}\t{:16}\t{:20}\t{:16}\t{:16}\t{:16}\t{:16}\t{:16}\t{:8}"
    print(tplt.format("序号","赛事日期","赛事编号","联赛","主队队名","客队队名","全场比分","赔率胜","赔率平","赔率负","完成情况"))
    # 打印输出信息的表头
    count = 0  #表明输出信息的计数器序号
    for g in ilt:
        count = count +1
        print(tplt.format(count,g[0],g[1],g[2],g[3],g[4],g[5],g[6],g[7],g[8],g[9]))
    print("")

def getMatchInfo(ilt, fpath):  #获取每场比赛信息，并存到一个数据结构。
#包含三个参数，1.所有比赛的信息列表，2要把信息存到文件的文件路径
    count = 0  # 表明输出信息的计数器序号
    for h in ilt:
        try:
            with open(fpath, 'w',encoding='utf-8')as file_object:  #以附加模式打开文件
                file_object.write(str(ilt)+'\n')  #写入列表的信息
                count = count + 1
                print('\r当前速度: {:.2f}%'.format(count * 100 / len(ilt)), end='')  # 动态显示进度条
        except:
            traceback.print_exc()

def mysql_create():
    try:
        # 创建数据库连接
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='youlei1990717', database='python-01',
                             charset='utf8')  # 要连哪个服务器，就写哪个IP地址
        print('数据库成功连接！')
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS FootBallMatch")
        sql = 'CREATE TABLE FootBallMatch(id int, match_date CHAR(20),week CHAR(20), match_type CHAR(20),master_team CHAR(20), ' \
              'slave_team CHAR(20),scroe CHAR(10),odds1 CHAR(20),odds2 CHAR(20),odds3 CHAR(20), finish CHAR(20))'
        # "序号id","赛事日期match_date","赛事编号week","联赛match_type","主队队名mteam","客队队名steam","全场比分scroe","赔率胜odds1","赔率平odds2","赔率负odds3","完成情况finish"
        cursor.execute(sql)   #使用execute()方法执行SQL
        print("表格创建成功！")
    except pymysql.Error as e:
        print("数据库连接失败：" + str(e))
        print("表格创建失败：" + str(e))

def mysql_insert(ilt):
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='youlei1990717', database='python-01',
                         charset='utf8')  # 要连哪个服务器，就写哪个IP地址
        cursor = conn.cursor()
        print("mysql connect succes")  # 测试语句，这在程序执行时非常有效的理解程序是否执行到这一
        try:
            count = 0  # 表明输出信息的计数器序号
            for item in ilt:
                count = count + 1
                insert_infor = 'insert into FootBallMatch(id,match_date,week,match_type,master_team,slave_team,scroe,odds1,odds2,odds3,finish)VALUE(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                # data_infor = ('0', '2019-02-02','周六147','葡超' ,'沙维什(-1)', '马里迪莫','1:0' ,'1.85 ' ,'3.05' ,'3.85' ,'已完成 ' )
                data_infor = (count,item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8],item[9])
                cursor.execute(insert_infor,data_infor)
            print('insert success!')#测试语句
        except Exception as e:
            print('Insert error:', e)
            conn.rollback()
        else:
            conn.commit()
        cursor.fetchone()  # 使用fetchone()方法获取单条数据,获取cursor执行sql之后第一行结果
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print(result)

def main():  #定义主函数，记录整个程序运行相关过程
    mysql_create()
    output_file = 'D:/MatchInfo.txt'  #文件保存地址
    depth = 20  #爬取页面深度
    start_url= "http://info.sporttery.cn/football/match_result.php"         #给出爬取相关信息的url
    infoList = []        #对整个输出结果定义一个列表
    for j in range(depth):   #对每一个页面进行单独的访问并处理
        try:  #使用try except 对解析过程进行异常判断
            url = start_url + '?page=' + str(j+1) + 'search_league=0&start_date=2017-01-31&end_date=2019-02-02&dan=0'
            #print (url)  #调试输出
            match_html = getHTMLText(url)  #获取页面
            parsePage(infoList, match_html) #
            #getMatchInfo(infoList, output_file)
        except:
            continue
    mysql_insert(infoList)
    printDataList(infoList)

main()  #调用main函数使整个程序执行起来