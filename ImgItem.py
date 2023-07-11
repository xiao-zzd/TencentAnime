"""
'img_store' 存储地址
'img_name'  图片名称
'web_url'   图片章节地址
'pic2pdf'   是否同步生成pdf文件
'img_url'   (数组)图片地址
"""

import os
import time
import random
import requests
from PIL import Image
import pic2pdf

def name_replace(name):
    name = name.replace(":", "")
    name = name.replace("?", "")
    name = name.replace("/", "")
    name = name.replace("*", "")
    name = name.replace(">", "")
    name = name.replace("<", "")
    name = name.replace("|", "")
    name = name.replace("\"", "")
    name = name.replace("\\", "")
    name = name.replace(".", "")

    return name


def check_img(file_path):
    try:
        Image.open(file_path).verify()
    except:
        os.remove(file_path)
        print('\033[35m' + 'error_img:' + '\033[0m' + '  ' + file_path)  # 带颜色输出


def make_dir_path(img_name, img_store):
    img_name = img_name.rstrip()  # 删除尾部空格
    dir_path = '%s/%s' % (img_store, img_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def process_item(item):
    if len(item['img_url']):
        item['img_name'] = name_replace(item['img_name'])
        dir_path = make_dir_path(item['img_name'], item['img_store'])
        cnt = str(len(item['img_url']))
        headers = {
            'Referer': item['web_url'],
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
        }
        for num, image_url in enumerate(item['img_url'], 1):
            # time.sleep(random.randint(3, 10)/10)
            image_file_name = '第' + str(num).rjust(3, '0') + '页-共' + cnt + '页.jpg'
            file_path = '%s/%s' % (dir_path, image_file_name)
            if os.path.exists(file_path):
                continue
            for index in range(5):
                try:
                    response = requests.get(url=image_url, timeout=15, headers=headers, verify=False)
                    if response.status_code == 200:
                        with open(file_path, 'wb') as handle:
                            for block in response.iter_content(1024):
                                handle.write(block)
                        check_img(file_path)
                        break
                    time.sleep(1+index)
                except:
                    print('error_img:' + item['img_name'] + '  ' + image_file_name)
            else:
                print('\033[31m' + 'error_img:' + item['img_name'] + '  ' + image_file_name + '\033[0m' + '  ' + image_url)  # 带颜色输出
        if os.listdir(dir_path):
            if item['pic2pdf']:
                pic2pdf.process_pic2pdf(dir_path, item['img_store'], item['img_name'])
            return str(len(os.listdir(dir_path))) + '/' + cnt + 'P'
        else:
            os.rmdir(dir_path)
        return '0/' + cnt + 'P'
    return '0/0P'
