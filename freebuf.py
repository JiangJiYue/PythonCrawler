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
    red = redis.Redis(host='127.0.0.1', password='xxxxx', port=6379, db=0)
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
    tree = etree.HTML(page_text)
    lists= []
    link_list=tree.xpath('//div[@class="title-left"]//a/@href[contains(string(), "/articles")]')#文章连接   
    link_list+=tree.xpath('//div[@class="title-left"]//a/@href[contains(string(), "/sectool")]')#文章连接 
    for link in link_list:
        link = 'https://www.freebuf.com'+link
        print("-------正在解析文章链接-------")
        if add_url(link):
            articles_content = requests.get(url=link,headers=headers).text
            articles_tree = etree.HTML(articles_content)
            articles_title= articles_tree.xpath('//span[@class="title-span"]/text()')
            articles_date = articles_tree.xpath('//*[@id="artical-detail-page"]/div[3]/div[2]/div[1]/div[1]/div[2]/span[1]/text()')
            for date in articles_date:
                print("-------正在获取文章更新时间-------")
                for title in articles_title:
                    print("-------正在将获取到的内容添加到列表-------")
                    date = time.strptime(date[0:10],'%Y-%m-%d')
                    lists.append({
                        'title':title,
                        'link':link,
                        'date':date
                    })
        else:
            print("有重复不需要分享了！！！！！")
        time.sleep(30)
    return lists
    
if __name__ == "__main__":
    group_id=xxxxxxx#群号
    while True:
        articles_list = get_articles_list()
        for test in articles_list:
            year = test['date'][0]#文章时间:年
            month = test['date'][1]#文章时间:月
            day = test['date'][2]#文章时间:日
            message = "freebuf更新啦!!!!!文章时间:{}文章标题:{}文章链接{}请陛下慢慢享用!!!!"
            article_time = "{}-{}-{}"
            article_time = article_time.format(year,month,day)
            message = message.format(article_time,test['title'],test['link'])
            print("-------正在发布到指定QQ群-------")
            url="http://127.0.0.1:5701/send_group_msg?group_id={}&message={}"
            new_url=url.format(group_id,message)
            r = requests.get(url=new_url)
            if r.status_code==200:
                print("-------发送成功-------")
            else:
                print("-------发送失败,请检查QQ机器人状态-------")            
        time.sleep(10800)
        
