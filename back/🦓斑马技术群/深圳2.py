'''
先抓到所有的属于深圳政府官网内容的博文
'链接','标题','日期','来源','内容','状态'
'''
import requests
import pymysql.cursors
import pandas as pd
import time
from pymysql.converters import escape_string
from bs4 import BeautifulSoup

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }

all_url_old = []  # 存储所有的url
title_all_old = []  # 存储所有的文章标题
date_all_old = []  # 存储所欲文章的日期
connection = pymysql.connect(host='rm-2zeak2a8i17c83416bo.mysql.rds.aliyuncs.com',
                             port=3306,
                             user='zkys_dev',
                             password='preWKBX&5m1a^sXSQSwV',
                             db='zkys_data_dev',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

# 从数据库查询未被更新的数据 得到一个当前数据库中所有链接地址的列表
def get_allData():
    with connection.cursor() as cursor:
        url_list_inmysql = []  # 在数据库中的链接地址列表

        sql = "SELECT url FROM `db_policy_library_gkx` "  # 查询所有地址
        cursor.execute(sql, ())
        for i in cursor.fetchall():
            url_list_inmysql.append(i['url'])
        return url_list_inmysql


# 抓取深圳法院的内容 返回法院正文内容 无来源
def get_szcourt_gov(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    content = soup.find('div', class_='news-detail-content-article-bottom').text  # 法院正文
    string_content = content

    print(string_content[:-4600])
    return_content = string_content[:-4600]  # 去掉一些css代码
    return return_content


# 请求政策的来源和内容并返回到之前的函数中去
def get_one_page_html(url):

    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    laiyuan = soup.find('div', class_='laiyuan').find('span', class_='ly').text.replace('来源：', '')  # 来源
    content = soup.find('div', class_='content col-xs-12 col-sm-12 col-md-12 col-lg-12').text  # 内容
    print(laiyuan)
    return laiyuan, content


# 主逻辑函数
def get_all_url():

    # 7页 当你运行的时候注意看一下有多少页，然后修改后面的即可
    # 注意 他说的有6页 其实只有5页
    for i in range(1, 6):
        # People's Daily
        # 如果是第一页的话请求方式不一样
        if (i == 1):
            # 对全部6页进行请求，请求所有的url，添加到请求链接列表中去
            response = requests.get('http://fgw.sz.gov.cn/ztzl/qtztzl/szyshj/zcwj/index.html', verify=False)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            div = soup.find('div', class_='zyzp')  # 定位到包含所有链接的部分
            all_a = div.find_all('a')

            for j in all_a:
                url = j.get('href')
                title = j.find('span', class_='zyzp-text').text  # 标题
                date_one = j.find('span', class_='zyzp-time').text  # 日期
                all_url_old.append(url)
                title_all_old.append(title)
                date_all_old.append(date_one)
        else:
            #  后面的页面需要按照数字进行修改页数

            # 对全部6页进行请求，请求所有的url，添加到请求链接列表中去
            url_list = 'http://fgw.sz.gov.cn/ztzl/qtztzl/szyshj/zcwj/index_{}.html'.format(i)
            print(url_list)
            response = requests.get(url_list, verify=False)

            soup = BeautifulSoup(response.text, 'lxml')
            div = soup.find('div', class_='zyzp')  # 定位到包含所有链接的部分
            all_a = div.find_all('a')

            for j in all_a:
                url = j.get('href')
                title = j.find('span', class_='zyzp-text').text  # 标题
                date_one = j.find('span', class_='zyzp-time').text  # 日期
                all_url_old.append(url)
                title_all_old.append(title)
                date_all_old.append(date_one)

    # 在这里调用数据库的当前所有数据链接进行判断，如果当前链接已经存在库中了 则去掉不添加其链接、标题、日期到新的三个列表中去
    all_url = []  # 存储所有的url新列表
    title_all = []  # 存储所有的文章标题新列表
    date_all = []  # 存储所欲文章的日期新列表
    url_inmysql_data = get_allData()  # 获取数据库当前所有链接地址列表
    for chakan_url_num in range(len(all_url_old)):
        chakan_url = all_url_old[chakan_url_num]  # 当前进行查询的链接地址
        if chakan_url in url_inmysql_data:
            print("当前链接已存在 不再进行抓取")
        else:
            # 如果不存在 则将链接、标题、日期都添加到三个列表中去方便下面进行查询插入到数据库中
            all_url.append(chakan_url)
            title_all.append(title_all_old[chakan_url_num])
            date_all.append(date_all_old[chakan_url_num])

    print("当前页面有 " + str(len(date_all)) + " 条数据正在等待被抓取。")

    # 遍历当前的所有文章链接 对该链接进行判断，看是否是深圳官网的
    # 如果是 则进一步判断是否是pdf
    # 如果是 pdf 则记录为 pdf 并且不请求
    # 如果不是pdf 则请求具体的页面内容
    # 如果不是 则不请求
    for url_one_page_num in range(len(all_url)):
        url_this_page = all_url[url_one_page_num]
        print(url_this_page)
        if ('fgw.sz.gov.cn' in url_this_page):
            # print(" 该链接属于官网内容 ")
            if ('pdf' in url_this_page):
                # print("该链接的内容是 PDF")
                with connection.cursor() as cursor:
                    sql = "INSERT INTO `db_policy_library_gkx` (`url`,`title`,`release_time`, `content_type`) VALUES (%s,%s,%s,%s)"
                    try:
                        # 直接定位然后提取文本即可
                        cursor.execute(sql,
                                       (url_this_page, title_all[url_one_page_num], date_all[url_one_page_num], 'PDF'))
                    except Exception as e:
                        print(str(e))
                connection.commit()
            else:
                # print("正在请求该页面的内容")
                # 调用请求页面内容的函数 获取到页面内容和文章来源
                laiyuan, content = get_one_page_html(url_this_page)
                with connection.cursor() as cursor:
                    sql = "INSERT INTO `db_policy_library_gkx` (`url`,`title`,`content`,`source`,`release_time`, `content_type`) VALUES (%s,%s,%s,%s,%s,%s)"
                    try:
                        # 直接定位然后提取文本即可
                        cursor.execute(sql, (
                        url_this_page, title_all[url_one_page_num], escape_string(content), laiyuan,
                        date_all[url_one_page_num], '存在正文'))
                    except Exception as e:
                        print(str(e))
                connection.commit()
        else:
            # pass
            # print("该链接不属于官网")
            # 如果属于法院的网站 就对其进行抓取
            if ('szcourt.gov.cn' in url_this_page):
                content = get_szcourt_gov(url_this_page)
                # 如果没有抓到内容也要写入进去
                if (content == ''):
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `db_policy_library_gkx` (`url`,`title`,`release_time`, `content_type`) VALUES (%s,%s,%s,%s)"
                        try:
                            # 直接定位然后提取文本即可
                            cursor.execute(sql, (
                            url_this_page, title_all[url_one_page_num], date_all[url_one_page_num], '其他网站 但是没有抓到内容'))
                        except Exception as e:
                            print(str(e))
                else:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `db_policy_library_gkx` (`url`,`title`,`content`,`release_time`, `content_type`) VALUES (%s,%s,%s,%s,%s)"
                        try:
                            # 直接定位然后提取文本即可
                            cursor.execute(sql, (url_this_page, title_all[url_one_page_num], escape_string(content),
                                                 date_all[url_one_page_num], '其他网站'))
                        except Exception as e:
                            print(str(e))
                connection.commit()


# 主函数
get_all_url()
# 测试能不能抓到深圳法院内容
# get_szcourt_gov('https://www.szcourt.gov.cn/article/30002487')
