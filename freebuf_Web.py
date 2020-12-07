import redis
import hashlib
from faker import Faker
import time
import requests
from retrying import retry
from lxml import html
etree = html.etree

#从代理池随机获取一个代理
def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()

#将不能用的代理从代理池中删除
def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

#构建request可识别的代理
def pinjie_proxy():
    proxy = get_proxy().get("proxy")
    proxies = {
        "https": "https://{}".format(proxy)
    }
    return proxies

#将获取的url转换为md5使其后面去重速度更快
def get_md5(val):
    md5 = hashlib.md5()
    md5.update(val.encode('utf-8'))
    return md5.hexdigest()

#利用redis的不能存入重复数据的特性去重
def add_url(url):
    red = redis.Redis(host='127.0.0.1', password='123456789', port=6379, db=0)
    res = red.sadd('TEST:urlset', get_md5(url))  # 注意是 保存set的方式
    if res == 0:  # 若返回0,说明插入不成功，表示有重复
        return False
    else:
        return True


@retry#出现错误重试,有很多免费代理会出现错误
def get_articles_list():#爬取页面
    proxy = pinjie_proxy()
    # #使用Faker库随机生成虚假header
    fake = Faker()
    headers = {'User-Agent': fake.user_agent()}
    page = requests.get(
        'https://www.freebuf.com/articles/web', headers=headers, proxies=proxy)
    if page.status_code == 200:
        page_text = page.text
        return page_text
    else:
        delete_proxy(proxy)
        print('删除代理'+proxy)


def analysis(group_id):#分析页面,提取需要的资料
    page_text = get_articles_list()
    tree = etree.HTML(page_text)
    link_list = tree.xpath(
        '//div[@class="title-left"]//a/@href[contains(string(), "/articles")]')  # 文章链接
    articles_title = tree.xpath(
        '//span[@class="title text-line-1"]/text()')#文章标题
    articles_date = tree.xpath(
        '//p[@class="bottom-right"]/span/text()')#文章时间
    for link, date, title in zip(link_list, articles_date, articles_title):
        link = 'https://www.freebuf.com'+link
        print("-------正在查重-------")
        if add_url(link):
            time.sleep(300)
            date = time.strptime(date[0:10], '%Y-%m-%d')
            message = "freebuf更新啦!!!!!文章时间:{}文章标题:{}文章链接{}"#构建qq机器人消息内容
            message = message.format(date, title, link)#字符串变量拼接
            send_qq(group_id=group_id, message=message)#调用qq机器人函数
        else:
            print("有重复不需要分享了！！！！！")


def send_qq(group_id, message):#机器人发送消息函数
    print("-------正在发布到指定QQ群-------")
    url = "http://127.0.0.1:5701/send_group_msg?group_id={}&message={}"
    new_url = url.format(group_id, message)
    r = requests.get(url=new_url)
    if r.status_code == 200:
        print("-------发送成功-------")
    else:
        print("-------发送失败,请检查QQ机器人状态-------")


if __name__ == "__main__":
    group_id = 642975216  # 群号
    while True:#死循环保证可以实时监测
        analysis(group_id)
        time.sleep(3600)#暂停1小时
