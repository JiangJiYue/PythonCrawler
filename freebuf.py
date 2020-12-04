import requests
from lxml import html
etree = html.etree
import time
from faker import Faker
import hashlib
import redis

def get_md5(val):
    md5 = hashlib.md5()
    md5.update(val.encode('utf-8'))
    return md5.hexdigest()


def add_url(url):
    red = redis.Redis(host='xxx.xxx.xxx.xxx', password='123456789', port=6379, db=0)
    res = red.sadd('TEST:urlset', get_md5(url)) # 注意是 保存set的方式
    if res == 0:  # 若返回0,说明插入不成功，表示有重复
        return False
    else:
        return True

def get_articles_list():
    # #使用Faker库随机生成虚假header
    fake = Faker()
    headers ={'User-Agent':fake.user_agent()}
    page_text = requests.get('https://www.freebuf.com/',headers=headers).text
    return page_text


def analysis(group_id):
    page_text = get_articles_list()
    tree = etree.HTML(page_text)
    link_list=tree.xpath('//div[@class="title-left"]//a/@href[contains(string(), "/articles")]')#文章连接   
    link_list+=tree.xpath('//div[@class="title-left"]//a/@href[contains(string(), "/sectool")]')#文章连接   
    for link in link_list:
        link = 'https://www.freebuf.com'+link
        print("-------正在解析文章链接-------")
        if add_url(link):
            time.sleep(300)
            # #使用Faker库随机生成虚假header
            fake = Faker()
            headers ={'User-Agent':fake.user_agent()}
            articles_content = requests.get(url=link,headers=headers).text
            articles_tree = etree.HTML(articles_content)
            articles_title= articles_tree.xpath('//span[@class="title-span"]/text()')
            articles_date = articles_tree.xpath('//*[@id="artical-detail-page"]/div[3]/div[2]/div[1]/div[1]/div[2]/span[1]/text()')
            for date,title in zip(articles_date,articles_title):
                print("-------正在获取文章更新时间-------")
                date = time.strptime(date[0:10],'%Y-%m-%d')
                message = "freebuf更新啦!!!!!文章时间:{}文章标题:{}文章链接{}"
                message = message.format(date,title,link)
                send_qq(group_id=group_id, message=message)
        else:
            print("有重复不需要分享了！！！！！")
def send_qq(group_id, message):
    print("-------正在发布到指定QQ群-------")
    url = "http://xxx.xxx.xx.xx:xxxx/send_group_msg?group_id={}&message={}"
    new_url = url.format(group_id, message)
    r = requests.get(url=new_url)
    if r.status_code == 200:
        print("-------发送成功-------")
    else:
        print("-------发送失败,请检查QQ机器人状态-------")


if __name__ == "__main__":
    group_id=xxxxxxxx#群号
    while True:
        analysis(group_id)       
        time.sleep(10800)