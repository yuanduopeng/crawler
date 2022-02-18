# @Time : 2022/1/27 22:27
# @Author : Yuanduo

import smtplib  # smtplib 用于邮件的发信动作
import urllib.error  # 制定URL, 获取网页数据
import urllib.request
from datetime import datetime  # 打印系统时间
from email.header import Header  # 用于构建邮件头
from email.mime.text import MIMEText  # email 用于构建邮件内容
from threading import Timer  # 固定周期爬虫
from bs4 import BeautifulSoup  # 网页解析，获取数据

AeroadUrl = "https://www.canyon.com/en-de/aeroad-cf-sl-8-disc/50005902.html?utm_source=row-journey&utm_medium=email&utm_campaign=row_back_in_stock&src=03awtk"

# 定时执行的内容
def crawler_mail(inc):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # 1.爬取商品名称和状态
    print("Searching Aeroad stock status ... ")
    (Aer_size, Aer_sts) = getData(AeroadUrl)
    bike_name = Aer_size
    bike_stock = Aer_sts
    # 2.发送邮件
    # 2.1 确认是否要发送邮件
    send_email_or_not = 0
    if len(bike_name) > 0 and len(bike_stock) > 0:
        if bike_name[4] == "M" and bike_stock[4].find("stock") != -1:
            send_email_or_not = 1
    # 2.2 拼接邮件消息内容
    if len(bike_name) > 0 and len(bike_stock) > 0:
        massage_content = "Aeroad CF SL8 Blue, size " + bike_name[4] + ": " + bike_stock[4].lstrip()
        print("massage content: ", massage_content)
    # 2.3 发出邮件
    if send_email_or_not == 1:
        print("Bike is available, so E-mail will be sent.")
        sendEmail(massage_content)
    else:
        print("Bike is unavailable \n")
    t = Timer(inc, crawler_mail, (inc,))
    t.start()


# 爬取网页
def getData(baseurl):
    namelist = []
    statuslist = []
    html = askURL(baseurl)
    # 2.逐一解析数据
    soup = BeautifulSoup(html, "html.parser")
    # 查找商品名称 name
    print("Finding bike name ...")

    for name in soup.find_all('div', class_="productConfiguration__variantType"):
        name = str(name)
        name_line = name.split('\n')
        size = name_line[1].lstrip()
        namelist.append(size)
    if len(namelist) > 0:
        print("Bike size was found successfully!")
    else:
        print("No bike")
    # 查找商品库存状态 status
    print("Finding bike stock status ...")
    for status in soup.find_all('div', class_="productConfiguration__availabilityMessage"):
        whole_status = str(status)
        line_status = whole_status.split('\n')
        status = line_status[1]
        statuslist.append(status)
    if len(statuslist) > 0:
        print("Bike status was found successfully!")
    else:
        print("No bike status")
    return namelist, statuslist


# 得到指定一个url的网页内容
def askURL(url):
    head = {  # 模拟浏览器头部信息，像网站服务器发送消息
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 97.0.4692.99 Safari / 537.36"
    }  # 用户代理，表示告诉网站我们是什么类型的机器、浏览器
    request = urllib.request.Request(url, headers=head)
    html = ""
    askurl_error_cnt = 0
    while True:
        try:
            if askurl_error_cnt >= 5:
                print("Already try 5 times, break")
                break
            # 请求打开url地址内容，超时timeout报错
            print("Asking URL ... ")
            response = urllib.request.urlopen(request, timeout=10)
            html = response.read().decode("utf-8")
            print("Asked URL successfully!")
        except:
            askurl_error_cnt += 1
            print("Asked URL failed, try again ...", askurl_error_cnt)
        else:
            break
    return html


def sendEmail(MassageContent):
    # 发信方的信息：发信邮箱，QQ 邮箱授权码
    from_addr = '452372091@qq.com'
    password = 'duixjbrqdzsabjcd'
    # 收信方邮箱
    to_addr = 'yuanduopeng@qq.com'
    # 发信服务器
    smtp_server = 'smtp.qq.com'
    # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
    msg = MIMEText(MassageContent, 'plain', 'utf-8')
    # 邮件头信息
    msg['From'] = Header(from_addr)
    msg['To'] = Header(to_addr)
    msg['Subject'] = Header('CANYON Stock Status')
    print("Email are sending from ", from_addr, "to ", to_addr)
    try:
        # 开启发信服务，这里使用的是加密传输
        server = smtplib.SMTP_SSL(smtp_server)
        server.connect(smtp_server, 465)
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, msg.as_string())
        print("Email are sent successfully!")
        server.quit()
    except smtplib.SMTPException:
        print("Error: Email can't be sent.")


if __name__ == "__main__":  # 当程序执行时,调用函数
    # 执行爬虫，并发送email，设定循环时间
    crawler_mail(120)
