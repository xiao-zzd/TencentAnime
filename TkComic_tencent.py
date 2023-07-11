"""
腾讯漫画网爬虫爬取带界面显示
"""


import ImgItem
import re
import os
import json
import base64
import execjs
import tkinter
import requests
from lxml import etree
from math import floor
import multiprocessing
import tkinter.messagebox
from urllib.parse import urljoin
from multiprocessing import Pool
from tkinter.filedialog import askdirectory
from tkinter import scrolledtext, INSERT, LEFT, RIGHT, Y, VERTICAL, HORIZONTAL, W, GROOVE, END
requests.packages.urllib3.disable_warnings()

ComicData = {'need_chapter': 0, 'ok_chapter': 0, 'comic_name': '', 'num': 0, 'CkBox': []}


# 爬取列表(章节)函数
#https://ac.qq.com/Comic/ComicInfo/id/636396
def get_chapter_url(start_url):
    try:
        response = requests.get(url=start_url, timeout=15)
        response.encoding = "utf-8"
        html = etree.HTML(response.text)
        span_xpaths = html.xpath('//div[@id="chapter"]//ol[@class="chapter-page-all works-chapter-list"]/li/p/span')
        comic_name = html.xpath('//h2[@class="works-intro-title ui-left"]/strong/text()')[0]
        print(comic_name + ':共' + str(len(span_xpaths)) + '章节')#   鸡汤皇后:共278章节
        items = []
        for num, span_xpath in enumerate(span_xpaths, 1):
            if span_xpath.xpath('./i/@class')[0] == 'ui-icon-pay':
                continue
            web_url = urljoin(start_url, span_xpath.xpath('./a/@href')[0])
            img_name = span_xpath.xpath('./a/@title')[0]
            item = {'web_url': web_url, 'img_name': img_name}
            items.append(item)
        return {'comic_name': comic_name, 'data': items}
        # {'comic_name': '鸡汤皇后', 'data': [{'web_url': 'https://ac.qq.com/ComicView/index/id/636396/cid/2', 'img_name': '鸡汤皇后：预告'},
    except:
        return {'comic_name': None, 'data': None}


# 列表爬取回调函数 存入CkBox 递增num
def callback_get_chapter_url(res):
    if not res['comic_name']:
        tkinter.messagebox.showerror('错误', '请输入正确的ID...')
    else:
        scr.insert(END, res['comic_name'] + ':共' + str(len(res['data'])) + '章节' + '--列表全部爬取完毕，请选择要爬取的选项！' + '\n')
        scr.see(END)
        ComicData['comic_name'] = res['comic_name']
        ComicData['num'] = len(res['data'])
        for num, item in enumerate(res['data'], 0):
            data = {'variable': tkinter.IntVar(), 'img_name': item['img_name'], 'web_url': item['web_url'], 'data':''}
            data['data'] = tkinter.Checkbutton(frame,  text=item['img_name'], variable=data['variable'], onvalue=1, offvalue=0, justify=LEFT, height=1)
            data['data'].grid(row=floor(num / 3), column=floor(num % 3), sticky=W)
            ComicData['CkBox'].append(data)
    B['state'] = tkinter.NORMAL
    print('callback_get_chapter_url end')


# 爬取列表按钮函数 --
def start_spider():
    B['state'] = tkinter.DISABLED
    ComicData['comic_name'] = None
    ComicData['num'] = 0
    for CkBox in ComicData['CkBox']:
        CkBox['data'].destroy()
    ComicData['CkBox'] = []
    scr.insert(END, '开始爬取，请耐心等待。。。' + '\n')
    scr.see(END)
    start_urls = [id_path.get()]  # ['https://ac.qq.com/Comic/comicInfo/id/505430']  #
    for start_url in start_urls:
        start_url = 'https://ac.qq.com/Comic/comicInfo/id/' + start_url
        res = p.apply_async(get_chapter_url, args=(start_url,), callback=callback_get_chapter_url)
    print('startSpider end')


# 进程-爬取图片
def get_picture_data(item):
    js = """
        function Base() {
            _keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
            this.decode = function(c) {
                var a = "",b, d, h, f, g, e = 0;
                for (c = c.replace(/[^A-Za-z0-9\+\/\=]/g, ""); 
                    e < c.length;) b = _keyStr.indexOf(c.charAt(e++)),
                    d = _keyStr.indexOf(c.charAt(e++)),
                    f = _keyStr.indexOf(c.charAt(e++)),
                    g = _keyStr.indexOf(c.charAt(e++)),
                    b = b << 2 | d >> 4,
                    d = (d & 15) << 4 | f >> 2,
                    h = (f & 3) << 6 | g,
                    a += String.fromCharCode(b),
                    64 != f && (a += String.fromCharCode(d)),
                    64 != g && (a += String.fromCharCode(h));
                return a = _utf8_decode(a)
            };
            _utf8_decode = function(c) {
                for (var a = "",b = 0,d = c1 = c2 = 0; b < c.length;) 
                    d = c.charCodeAt(b),128 > d ? (a += String.fromCharCode(d), b++) : 191 < d && 224 > d ? (c2 = c.charCodeAt(b + 1), a += String.fromCharCode((d & 31) << 6 | c2 & 63), b += 2) : (c2 = c.charCodeAt(b + 1), c3 = c.charCodeAt(b + 2), a += String.fromCharCode((d & 15) << 12 | (c2 & 63) << 6 | c3 & 63), b += 3);
                return a
            }
        }
        function getData(T,N){
        T = T.split('');
        var B = new Base(),len,locate,str;
        N = N.match(/\d+[a-zA-Z]+/g);
        len = N.length;
        while (len--) {
            locate = parseInt(N[len]) & 255;
            str = N[len].replace(/\d+/g, '');
            T.splice(locate, str.length)
        }
        T = T.join('');
        return B.decode(T);
        }
        """

    try:
        response = requests.get(url=item['web_url'], timeout=15)
        pat2 = 'window\["(.*?);'
        allid2 = re.compile(pat2).findall(response.text)

        pat1 = "'(.*?)',"
        allid = re.compile(pat1).findall(response.text)

        T = allid[0]

        nonce = allid2[1]
        nonce = '='.join(nonce.split('=')[1:])
        nonce = execjs.eval(nonce)
        N = nonce

        ctx = execjs.compile(js)
        data = ctx.call("getData", T, N)
    except:
        print('error' + item['img_name'])
        return get_picture_data(item)
    try:
        picture = json.loads(data)['picture']
        print(json.dumps(json.loads(data), indent=4))
        for url in picture:
            item['img_url'].append(url['url'])
    except:
        data = data.replace("\\", "")
        picture = re.finditer(r"https://manhua.qpic.cn/manhua_detail(.*?).(?:jpg|png|JPG|jpeg)/0", data)
        for pic in picture:
            item['img_url'].append(pic.group())

    ImgItem.process_item(item)
    return item['img_name']


# 进程回调函数 -- 爬取图片
def callback_get_picture_data(res):
    ComicData['ok_chapter'] += 1
    print('over:' + res)
    scr.insert(END, 'over:' + res + '\n')
    scr.see(END)
    if ComicData['need_chapter'] == ComicData['ok_chapter']:
        scr.insert(END, '数据全部爬取完毕！\n')
        scr.see(END)
        print('数据全部爬取完毕！')


# 爬取选中按钮函数 开进程分别爬取各个选中的选项==============================================================================
def get_data():
    scr.insert(END, 'beginSpider-开始爬取所选项' + '\n')
    scr.see(END)
    for CkBox in ComicData['CkBox']:
        if CkBox['variable'].get():
            ComicData['need_chapter'] += 1
            print(CkBox['img_name'])
            item = {'img_store': path.get() + '/' + ComicData['comic_name'], 'web_url': CkBox['web_url'], 'img_name': CkBox['img_name'], 'pic2pdf': 1, 'img_url': []}
            p.apply_async(get_picture_data, args=(item,), callback=callback_get_picture_data)


# 全选 反选按钮函数==================================================
def get_all():
    for CkBox in ComicData['CkBox']:
        CkBox['variable'].set(1)


def get_back():
    for CkBox in ComicData['CkBox']:
        if CkBox['variable'].get():
            CkBox['variable'].set(0)
        else:
            CkBox['variable'].set(1)


# 列表框长宽========================================================
def frame_function(event):
    canvas.configure(scrollregion=canvas.bbox("all"), width=screen_x-200, height=screen_y-400)


# 路径选择按钮=======================================================
def select_path():
    path_ = askdirectory()
    if path_:
        path.set(path_)


if __name__ == '__main__':
    # os.environ["EXECJS_RUNTIME"] = "Node"
    # print(execjs.get().name)
    multiprocessing.freeze_support()  # 多进程必须要这个否者会卡死
    # 第1步，实例化object，建立窗口window 设定窗口的大小(长 * 宽)
    window = tkinter.Tk()
    screen_x = window.winfo_screenwidth()
    screen_y = window.winfo_screenheight()
    print(screen_x, 'x', screen_y)
    window.geometry('%dx%d+%d+%d' % (screen_x-100, screen_y-100, 50, 15))
    # 第2步，写一个图标
    window.iconbitmap(default = r'zzz.ico')
    # 第3步，给窗口的可视化起名字
    window.title('腾讯漫画爬虫程序')
    # 第4步，在窗口界面设置放置Button按键
    id_path = tkinter.StringVar()
    id_path.set('505430')
    id_frame = tkinter.Frame(window, relief=GROOVE)
    tkinter.Label(id_frame, font=('隶书', 14), text="输入正确的漫画ID:").pack(side="left")
    tkinter.Entry(id_frame, font=('隶书', 14), textvariable=id_path).pack(side="left")
    B = tkinter.Button(id_frame, text="爬取列表", font=('隶书', 16), width=10, height=1, command=start_spider)
    B.pack(side="left")
    id_frame.pack()
    # 第5步，创建并放置一个多行文本框ScrolledText用以显示
    scr = scrolledtext.ScrolledText(window, width=120, height=10, state=tkinter.NORMAL, font=("隶书", 14))  # 滚动文本框（宽，高（这里的高应该是以行数为单位），字体样式）
    # scr.place(x=50, y=50)  # 滚动文本框在页面的位置
    scr.pack()
    # 第6步，写一个Frame放列表-带滚动条
    f_btn = tkinter.Frame(window)
    f_btn.pack()
    my_frame = tkinter.Frame(window, relief=GROOVE, bd=1)
    # my_frame.place(x=10, y=10)
    my_frame.pack()
    canvas = tkinter.Canvas(my_frame)
    frame = tkinter.Frame(canvas)
    my_scrollbar_y = tkinter.Scrollbar(my_frame, orient=VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=my_scrollbar_y.set)
    my_scrollbar_y.pack(side="right", fill="y")
    my_scrollbar_x = tkinter.Scrollbar(my_frame, orient=HORIZONTAL, command=canvas.xview)
    canvas.configure(xscrollcommand=my_scrollbar_x.set)
    my_scrollbar_x.pack(side="bottom", fill="x")
    canvas.pack(side="left")
    canvas.create_window((0, 0), window=frame, anchor='nw')
    frame.bind("<Configure>", frame_function)
    # 第7步，Frame中写三个按钮 爬取 全选 反选
    Button_frame = tkinter.Frame(window, relief=GROOVE)
    tkinter.Button(Button_frame, text="爬取选中", font=('隶书', 14), width=10, height=1, command=get_data).pack(side="left")
    tkinter.Button(Button_frame, text="全选", font=('隶书', 14), width=10, height=1, command=get_all).pack(side="left")
    tkinter.Button(Button_frame, text="反选", font=('隶书', 14), width=10, height=1, command=get_back).pack(side="left")
    # 第8步，Frame中写保存路径选择输入框和按钮
    path = tkinter.StringVar()
    path.set('D:/Comic_Tencent')
    tkinter.Label(Button_frame, font=('隶书', 14), text="存储路径:").pack(side="left")
    tkinter.Entry(Button_frame, font=('隶书', 14), state='disable', textvariable=path).pack(side="left")
    tkinter.Button(Button_frame,font=('隶书', 14), text="路径选择", command=select_path).pack(side="left")
    Button_frame.pack()
    # 第9步，创建进程池异步爬取
    # maxtasksperchild本意是每个进程最大的任务量，如果你maxtasksperchild = 2, 那么他每次干完两个任务后，就会spawn一个新的进程。可以防止某个进程内存泄露被oom，这样可以通过原始kill进程的方式回收内存资源。
    p = Pool(10, maxtasksperchild=2)
    # 第10步，循环刷窗口
    window.mainloop()
    p.terminate()
    print('---over---')


