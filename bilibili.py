import requests
import json
import os
import fnmatch

# 获取哔哩哔哩视频的每集的标题


def getjson():
    page_text = requests.get(
        'https://api.bilibili.com/x/web-interface/view/detail?bvid=BV15741177Eh&aid=89760569')
    data = page_text.json()
    shuzi = list(range(1, 233))
    data = data['data']['View']['pages']
    newname = []
    for shuzi, item in zip(shuzi, data):
        part = item['part']
        mingzi = str(shuzi)+part[3:len(part)]+".mp4"
        newname.append(mingzi)
    return newname

# 截取需要查找的字符串


def findName(fileList):
    findname = []
    for fn in fileList:
        fname = fn[7:len(fn)-12]
        findname.append(fname)
    return findname

# 查找需要更改的需要更改的文件名字以及新名字


def comparison(fileList, path):
    oa = []  # 定义需要更改的文件名字的列表
    newa = []  # 定义新名字的列表
    findname = findName(fileList)  # 获取查找字符串的列表
    newname = getjson()  # 获取哔哩哔哩新名字的列表
    for fn, oldname in zip(findname, fileList):  # 循环遍历查找字符串和需要更改的文件名字
        for na in newname:  # 循环新名字保证每一个查找字符串可以和每一个新名字以及每一个需要更改的文件名字可以对比
            # 使用模糊查询,找出对应的新名字以及需要更改的文件名字,
            if fn in oldname and fn in na and oldname.endswith('.mp4'):
                # fn 查找字符串,oldname需要更改的文件名字,na新名字
                oa.append(oldname)
                newa.append(na)
    rename(oa, newa, path)

# 进行批量重命名


def rename(oldname, newname, path):
    path = path  # 文件路径
    oldname = oldname  # 需要更改的文件名字
    newname = newname  # 新名字
    # 文件批量重命名
    for oldn, newna in zip(oldname, newname):
        # 捕获异常使其遇到错误也可以正常运行,因为模糊查询的原因避免不了重名的错误,所以只能把准确率控制在90%
        try:
            oldname = path + os.sep + oldn
            newname = path + os.sep + newna
            os.rename(oldname, newname)
            print(oldname, '=======>', newname)
        except Exception as e:
            pass


if __name__ == "__main__":
    path = 'D:\Learning world\personal project\personal project\Python\\test'  # 路径
    fileList = os.listdir(path)  # 列取path下的文件名
    comparison(fileList, path)
