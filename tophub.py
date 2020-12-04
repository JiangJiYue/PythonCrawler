import redis
import hashlib
from faker import Faker
import time
import requests
from lxml import html
etree = html.etree


def get_md5(val):
    md5 = hashlib.md5()
    md5.update(val.encode('utf-8'))
    return md5.hexdigest()


def add_url(url):
    red = redis.Redis(host='xxx.xxx.xxx.xxx', password='123456789', port=6379, db=0)
    res = red.sadd('TEST:urlset', get_md5(url))  # 注意是 保存set的方式
    if res == 0:  # 若返回0,说明插入不成功，表示有重复
        return False
    else:
        return True


def get_articles_list():
    # #使用Faker库随机生成虚假header
    fake = Faker()
    headers = {'User-Agent': fake.user_agent()}
    print("-----请求网页中-----")
    page_text = requests.get('https://tophub.today/', headers=headers).text
    return page_text


def analysis(group_id):
    page_text = get_articles_list()
    tree = etree.HTML(page_text)
    type_title = ['node-68', 'node-89', 'node-100',
                  'node-132', 'node-312', 'node-327']
    blog_name = ['吾爱破解', '看雪论坛', '掘金', '开发者头条', '先知社区', '安全客']
    for type_t, blog_name in zip(type_title, blog_name):
        print("正在分析"+blog_name+"的头条")
        link_xpath = '//div[@id="'+type_t+'"]/div/div[2]/div/a/@href'
        link_list = tree.xpath(link_xpath)  # 头条链接
        title_xpath = '//div[@id="'+type_t + \
            '"]/div/div[2]/div/a/div/span[2]/text()'
        title_list = tree.xpath(title_xpath)  # 头条标题
        for link, title in zip(link_list, title_list):
            if add_url(link):
                time.sleep(300)
                message = "{}更新啦!!!!!        文章标题:{}     文章链接{}"
                message = message.format(blog_name,title,link)
                send_qq(group_id=group_id, message=message)
            else:
                print("有重复不需要分享了！！！！！")


def send_qq(group_id, message):
    print("-------正在发布到指定QQ群-------")
    url = "http://xxx.xxx.xxx.xxx:xxxx/send_group_msg?group_id={}&message={}"
    new_url = url.format(group_id, message)
    r = requests.get(url=new_url)
    if r.status_code == 200:
        print("-------发送成功-------")
    else:
        print("-------发送失败,请检查QQ机器人状态-------")


if __name__ == "__main__":
    group_id = xxxxx# 群号
    while True:
        analysis(group_id)
