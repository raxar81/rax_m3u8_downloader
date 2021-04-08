# -*- coding: UTF-8 -*-
import sys

sys.path.append("C:\\Python36-32\\Lib\\site-packages")
import tkinter
import re
import urllib3
import threadpool
import threading
import os
import shutil
import time
import glob
from tkinter.ttk import *
from PIL import Image, ImageTk
import pyperclip
from tkinter.filedialog import askdirectory

def get_image(filename,width,height):
    im = Image.open(filename).resize((width,height))
    return ImageTk.PhotoImage(im)


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def getrealtask(link):
    global key
    rooturl1 = ''
    rooturl2 = ''
    pattern3 = re.compile(r'^.*[\/]', re.M)
    result11 = pattern3.findall(link)
    if result11:
        rooturl1 = result11[0]
    pattern4 = re.compile(r'^http[s]?:\/\/[^\/]*', re.M)
    result114 = pattern4.findall(link)
    if result114:
        rooturl2 = result114[0]
    res = http.request('GET', link)
    content = str(res.data, 'utf8')
    list = content.split('\n')
    reallist = []
    for one in list:
        if one.endswith('"key.key"'):
            keyurl = rooturl1 + "key.key"
            res = http.request('GET', keyurl)
            key = str(res.data, 'utf8')
        if one.endswith('.ts') or one.endswith('.image'):
            if re.match(r'http', one, re.M | re.I):
                reallist.append(one)
            elif re.match(r'\/', one, re.M | re.I):
                reallist.append(rooturl2 + one)
            else:
                reallist.append(rooturl1 + one)
        if one.endswith('.m3u8'):
            if re.match(r'\/', one, re.M | re.I):
                reallist = getrealtask(rooturl2 + one)
            else:
                reallist = getrealtask(rooturl1 + one)
            break
    return reallist

def download_ts(result):
    url = result['url']
    name = result['name']
    num = result['num']
    rootpath = result['root']
    m3u8Name = result['m3u8name']
    t= str(result['total'])
    if num % 10000 == 0:
        print(str(num)+' / '+t)
    basepath = os.path.join(rootpath,m3u8Name)
    fullpath = os.path.join(basepath,name)
    isExist = os.path.exists(fullpath)
    if not isExist:
        http = urllib3.PoolManager(timeout=10.0)
        while(1):
            try:
                f = http.request('GET', url)
                break
            except:
                print("URL ERRO: " + url)
                time.sleep(2)
        d = f.data
        with open(fullpath, "wb") as code:
            code.write(d)
        print("SAVE: " + url)
def clock2(num,path):
    global window
    global key
    v3 = tkinter.StringVar();
    v4 = tkinter.StringVar();
    l3 = tkinter.Label(window, text='', textvariable=v3, font=('Arial', 10))
    l4 = tkinter.Label(window, text='', textvariable=v4, font=('Arial', 10))
    l3.place(x=10, y=130, anchor='nw')
    l4.place(x=10, y=160, anchor='nw')
    v3.set("下载中。。。")
    while(1):
        path_file_number = len(glob.glob(path+'/*.ts'))
        mp4_file_number = len(glob.glob(path + '/*.mp4'))
        numberstr = str(path_file_number) + '/'+str(num)
        v4.set(numberstr)
        if mp4_file_number==1:
            v3.set("下载完成！")
            key = ''
            break

def clock1():
    global v
    global v2
    global rootpath
    m3u8Name = v2.get()
    url = v.get()
    print(url)
    urls = getrealtask(url)
    total = len(urls)
    i = 0
    tasks = []
    tsNames = []
    for one in urls:
        task = {}
        task['root'] = rootpath
        task['m3u8name'] = m3u8Name
        task['url'] = one
        task['num'] = i
        task['total'] = total
        task['name'] = str(i) + '.ts'
        tsNames.append(str(i) + '.ts')
        i = i + 1
        tasks.append(task)
    print('tasks: ' + str(len(tasks)))
    targetpath = os.path.join(rootpath, m3u8Name)
    if not os.path.exists(targetpath):
        os.makedirs(targetpath)
    timer2 = threading.Thread(target=clock2,args=(len(tasks),targetpath))
    timer2.daemon = True
    timer2.start()
    requests = threadpool.makeRequests(download_ts, tasks)
    [task_pool.putRequest(req) for req in requests]
    task_pool.wait()
    mp4targetfile = os.path.join(targetpath, m3u8Name + '.mp4')
    with open(mp4targetfile, 'wb') as f:
        for ts in tsNames:
            tstargetfile = os.path.join(targetpath, ts)
            with open(tstargetfile, 'rb') as mergefile:
                shutil.copyfileobj(mergefile, f)
            print(tstargetfile + ' merged.')
        for tts in tsNames:
            tstargetfile = os.path.join(targetpath, tts)
            os.remove(tstargetfile)
    print(total)

def hit_me():
    global on_hit
    timer = threading.Thread(target=clock1)
    timer.daemon = True
    timer.start()
    return

def choose_dir():
    global v5
    global rootpath
    rootpath = askdirectory()
    v5.set('文件夹: '+rootpath+'/')
    return

def about():
    window = tkinter.Toplevel()
    window.geometry('600x100')# Note Toplevel, NOT Tk.
    msg = 'Rax m3u8下载器 v1.4\n写这个程序主要是为了学习Tk，顺便满足下自己看视频的需求。\n家里的移动网络看在线视频还是有些卡顿的。'
    label = tkinter.Label(window, text=msg,font=('Arial', 15))
    label.grid()
def update():
    window = tkinter.Toplevel()
    window.geometry('250x200')
    msg = 'Rax m3u8下载器 v1.5\n可以选择保存的目录了\nRax m3u8下载器 v1.4\n增加了菜单栏'
    label = tkinter.Label(window, text=msg,font=('Arial', 13))
    label.place(x=30, y=30, anchor='nw')
def donate():
    window = tkinter.Toplevel()
    window.geometry('500x400')
    msg = '软件免费使用\n欢迎喜欢此软件的各位大佬打赏，谢谢。'
    label = tkinter.Label(window, text=msg, font=('Arial', 20))


    i1 = tkinter.PhotoImage(file=get_resource_path("images\\wx.png"))
    i2 = tkinter.PhotoImage(file=get_resource_path("images\\zfb.png"))
    imagelabel = tkinter.Label(window, text='aaa', image=i1, font=('Arial', 10))
    imagelabel2 = tkinter.Label(window, text='vvv', image=i2, font=('Arial', 10))
    imagelabel.place(x=10, y=145, anchor='nw')
    imagelabel2.place(x=230, y=145, anchor='nw')
    label.place(x=40, y=50, anchor='nw')
    window.mainloop()
def clear():
    global v
    v.set("")
def paste():
    global v
    v.set(pyperclip.paste())

key = ''
on_hit = False
rootpath = "d:\\"
#最高50线程
task_pool = threadpool.ThreadPool(50)
http = urllib3.PoolManager(timeout=5.0)
urllib3.disable_warnings()

#主窗口初始化
window = tkinter.Tk()
window.style = Style()
window.style.theme_use("clam")
window.title("Rax m3u8视频下载器")
window.geometry('500x300')
window.resizable(0,0)


#飞机背景图
canvas_root = tkinter.Canvas(window,width=500,height=300)
im_root = get_image(get_resource_path('images\\feiji.jpeg'),500,300)
canvas_root.create_image(250,240,image=im_root)
canvas_root.pack()

#各控件初始状态
l1 = tkinter.Label(window, text='m3u8地址：', font=('Arial', 10))
l1.place(x=10, y=0, anchor='nw')

#   地址栏
v = tkinter.StringVar();
e2 = tkinter.Entry(window, show=None, textvariable = v,font=('Arial', 10),width=40)
v.set('')
e2.place(x=10, y=30, anchor='nw')

#   视频名称
l6 = tkinter.Label(window, text = ' 视频文件名称：', font=('Arial', 10))
l6.place(x=0, y=90, anchor='nw')

#   视频名称栏
v2 = tkinter.StringVar();
e3 = tkinter.Entry(window, show=None, textvariable = v2,font=('Arial', 10),width=15)
v2.set('')
e3.place(x=105, y=90, anchor='nw')

#   保存位置
v5 = tkinter.StringVar();
l2 = tkinter.Label(window, textvariable = v5, font=('Arial', 10))
v5.set('文件夹: D:/')
l2.place(x=10, y=60, anchor='nw')

#   下载按钮
b = tkinter.Button(window, text='下载', font=('Arial', 10), width=10, command=hit_me)
b.place(x=400, y=100, anchor='nw')

#   选择路径按钮
pathselectButton = tkinter.Button(window, text='选择路径', font=('Arial', 10), width=10, command=choose_dir)
pathselectButton.place(x=400, y=60, anchor='nw')

#   清空按钮
b2 = tkinter.Button(window, text='清空', font=('Arial', 10), width=10, command=clear)
b2.place(x=300, y=25, anchor='nw')

#   粘贴地址按钮
b3 = tkinter.Button(window, text='粘贴地址', font=('Arial', 10), width=10, command=paste)
b3.place(x=400, y=25, anchor='nw')

#   求捐赠按钮
l5 = tkinter.Label(window, text='软件免费使用，欢迎各位喜欢此软件的大佬打赏，谢谢。\nQQ讨论群：519565890', font=('Arial', 10))
l5.place(x=100, y=160, anchor='nw')

window.option_add('*tearOff', False)

#菜单栏
menubar = tkinter.Menu(window)
window['menu'] = menubar
help_menu = tkinter.Menu(menubar)
menubar.add_command(label='捐助作者',command=lambda: donate())
menubar.add_cascade(menu=help_menu, label='帮助')

#帮助 下拉菜单
help_menu.add_command(label='更新内容',command=lambda: update())
help_menu.add_command(label='关于',command=lambda: about())

# 进入消息循环
window.mainloop()
