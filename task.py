# -*- coding:utf-8 -*-
import requests
import configparser  
from bs4 import BeautifulSoup
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from io import BytesIO#操作二进制文件
import logging

config=configparser.ConfigParser()
config.read('./config',encoding='utf-8')

openid = config.get('USERINFO','openid')
username = config.get('USERINFO','username')

s = requests.session()
 
REQ_HEADERS = {
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; PACM00 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3164 MMWEBSDK/20211001 Mobile Safari/537.36 MMWEBID/556 MicroMessenger/8.0.16.2040(0x28001056) Process/toolsmp WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
    "X-Requested-With": "com.tencent.mm",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

URLS = {
    # 调用API获取最新一期青春学习的URL
    "COURSE_INFO":"https://h5.cyol.com/special/weixin/sign.json",
    # 调用API获取用户的信息
    "USER":"https://api.fjg360.cn/index.php?m=vote&c=index&a=get_members",
    # 提交打卡信息
    "SAVE_DOOR":"https://cp.fjg360.cn/index.php?m=vote&c=index&a=save_door&sessionId=&imgTextId=&ip="
    }

def get_course_info():
    """
    调用API获取最新一期青春学习的CODE
    :return:
    """
    resp = s.get(URLS['COURSE_INFO'],headers=REQ_HEADERS).json()
    
    course_id = list(resp)[-1]
    course_url = 'https://h5.cyol.com/special/daxuexi/'+ course_id +'/m.html'
    
    response = s.get(course_url)
    soup = BeautifulSoup(response.content.decode("utf8"),"lxml")
    course_name = soup.title.string[7:]
    
    config.set('COURSEINFO','course_name',course_name) 
    config.write(open('./config','w',encoding='utf-8')) 
    return {"course_id": course_id, "course_name": course_name}


def get_user():
    """
    调用API获取用户的信息
    :return:
    """
    
    resp = s.get(URLS['USER'], headers=REQ_HEADERS,params = {'openid':openid}).json()
    if resp.get("code") == 1:
        return resp.get("h5_ask_member")
    else:
        logging.error("您的OPENID配置有误，请检查后重试")

def save_door(user_info,course_info):
    """
    调用API提交用户进入页面信息至青春湖北数据库
    :param info:
    :return:
    """

    url = "https://cp.fjg360.cn/index.php?m=vote&c=index&a=save_door&sessionId=&imgTextId=&ip="
    params = {
        "username" : user_info["name"],
        "phone": "未知",
        "city" : user_info["danwei1"],
        "danwei2" : user_info["danwei3"],
        "danwei" : user_info["danwei2"],
        "openid" : openid,
        "num": 10,
        "lesson_name" : course_info['course_name'],
    }
    resp = s.get(url,headers=REQ_HEADERS,params=params).json()
    if resp.get("code") == 1:
        return logging.info('学习成功')
    else:
        show_exit("您的用户信息有误，请检查后重试")

def download_pic(course_id):
    """
    获取截图并添加个人签名
    """
    url = 'https://h5.cyol.com/special/daxuexi/' + course_id + '/images/end.jpg'
    resp = s.get(url=url,headers = REQ_HEADERS)
    
    #打开底版图片
    pic=Image.open(BytesIO(resp.content))

    # 在图片上添加文字 1
    draw = ImageDraw.Draw(pic)
    font = ImageFont.truetype(r'./static/simsun.ttc', 200)
    draw.text((100, 100),username,(255,255,0),font=font)
    draw = ImageDraw.Draw(pic)
    # 保存
    pic.save("./static/end.jpg")

def get_pic():
   
    course_info = get_course_info()
    user_info = get_user()
    save_door(user_info, course_info)
    download_pic(course_info['course_id'])

if __name__ == '__main__':
    logging.basicConfig(handlers=[logging.FileHandler(filename='./teen.log',
                                                      encoding='utf-8', mode='a+')],
                        format='%(asctime)s %(message)s',
                        level=getattr(logging, 'INFO'))
    get_pic()
    