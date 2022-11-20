# -*- coding: UTF-8 -*-
import sys
import tkinter
import re
import urllib3
import threadpool
import threading
import requests
import os
import shutil
import time
import glob
import json
from tkinter.ttk import *
from tkinter import *
from PIL import Image, ImageTk
from tkinter.filedialog import askdirectory
import customtkinter
import win32api

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
def clocksearch():
    global resulttextbox
    global resulttext
    resulttextbox.delete(0.0, tkinter.END)
    resulttextbox.insert("insert","搜索中 请稍后。。。")
    keyword = searchtext.get()
    url = 'http://cj.bajiecaiji.com/inc/feifei3bjm3u8/index.php?wd='+keyword
    s = requests.session()
    r = s.get(url)
    content = r.content
    jsonobject = json.loads(content)
    dataarray = jsonobject['data']
    result = ''
    for one in dataarray:
        title = one['vod_name']
        qingxidu = one['vod_remarks']
        m3u8url = one['vod_url']
        m3u8array = m3u8url.split('\r\n')
        result = result + title+ qingxidu + '\n'
        for oneone in m3u8array:
            lastarray = oneone.split('$')
            result = result+lastarray[0]+'\n'+lastarray[1]+'\n'
    resulttext = result
    resulttextbox.delete(0.0, tkinter.END)
    resulttextbox.insert("insert",resulttext)
    global searchbutton
    # searchbutton["state"] = 'normal'
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
def searchme():
    global searchbutton

    global on_hit_search
    # searchbutton.state = tkinter.DISABLED
    timer = threading.Thread(target=clocksearch)
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
    window = customtkinter.CTkToplevel()
    window.title('关于')
    window.geometry('600x100')# Note Toplevel, NOT Tk.
    msg = 'Rax m3u8下载器 v3.0\n写这个程序主要是为了学习Tk，顺便满足下自己看视频的需求。\n家里的移动网络看在线视频还是有些卡顿的。'
    label = customtkinter.CTkLabel(window, text=msg,text_font=('Arial', 15))
    label.grid()
def update():
    window = customtkinter.CTkToplevel()
    #title
    window.title('更新')
    window.geometry('300x300')
    msg = 'v3.0 采用两种全新主题界面\n\nv2.0 可以搜索想要下载的视频了\n主窗口会居中显示\n\nv1.5 可以选择保存的目录了\n\n v1.4 增加了菜单栏'
    label = customtkinter.CTkLabel(window, text=msg,text_font=('Arial', 15))
    label.place(x=0, y=10, anchor='nw')

def searchmain():
    windowsearch = customtkinter.CTkToplevel()
    windowsearch.geometry('560x415')
    windowsearch.title("Rax m3u8视频搜索器")

    #名称label
    msg = '名称：'
    label = customtkinter.CTkLabel(windowsearch, text=msg, text_font=('Arial', 10), width=20)
    label.place(x=20, y=15, anchor='nw')
    # 名称textbox
    global searchtext
    searchtext = tkinter.StringVar();
    searchtextbox = customtkinter.CTkEntry(windowsearch, show=None, textvariable=searchtext, text_font=('Arial', 10), width=200)

    v.set('')
    searchtextbox.place(x=75, y=15, anchor='nw')
    #   搜索按钮
    global searchbutton
    searchbutton = customtkinter.CTkButton(windowsearch, text='搜索', text_font=('Arial', 10), width=10, command=searchme)
    searchbutton.place(x=350, y=15, anchor='nw')

    #下拉条
    f = tkinter.Frame(windowsearch)
    s1 = tkinter.Scrollbar(f, orient=tkinter.VERTICAL)
    s1.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    #结果文本框
    global resulttextbox
    # xiala = customtkinter.CTkOptionMenu(windowsearch, text_font=('Arial', 10), width=20)
    # xiala.place(x=75, y=50, anchor='nw')
    resulttextbox = tkinter.Text(windowsearch,yscrollcommand=s1.set)
    resulttextbox.place(x=20, y=80, anchor='nw')
    # 声明label
    msg2 = '声明：本软件不储存任何视频资源，所有搜索结果均来自于互联网，与本软件无关，\n请勿使用本软件于非法用途。'
    label2 = customtkinter.CTkLabel(windowsearch, text=msg2, text_font=('Arial', 10))
    label2.place(x=20, y=375, anchor='nw')
    windowsearch.mainloop()

def donate():
    window = customtkinter.CTkToplevel()
    window.title('捐助')
    window.geometry('500x280')
    msg = '软件免费使用\n欢迎喜欢此软件的各位大佬打赏，谢谢。'
    label = customtkinter.CTkLabel(window, text=msg, text_font=('Arial', 20))
    i1 = tkinter.PhotoImage(file=get_resource_path("images\\wx.png"))
    i2 = tkinter.PhotoImage(file=get_resource_path("images\\zfb.png"))
    imagelabel = customtkinter.CTkLabel(window, text='aaa', image=i1, text_font=('Arial', 10))
    imagelabel2 = customtkinter.CTkLabel(window, text='vvv', image=i2, text_font=('Arial', 10))
    imagelabel.place(x=50, y=125, anchor='nw')
    imagelabel2.place(x=290, y=125, anchor='nw')
    label.place(x=20, y=30, anchor='nw')
    window.mainloop()
def clear():
    global v
    v.set("")
def paste():
    global v
    global window
    cont = window.clipboard_get()
    v.set(cont)
def change_mode():
    global flag
    if flag == 1:
        customtkinter.set_appearance_mode("dark")
        flag = 0
    else:
        customtkinter.set_appearance_mode("light")
        flag = 1
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
key = ''
on_hit = False
rootpath = "d:\\"
#最高50线程
task_pool = threadpool.ThreadPool(50)
http = urllib3.PoolManager(timeout=5.0)
urllib3.disable_warnings()

sw = win32api.GetSystemMetrics(0)
sh = win32api.GetSystemMetrics(1)
#主窗口初始化
window = customtkinter.CTk()
ww = 500
wh = 250
x = (sw-ww) / 2
y = (sh-wh) / 2
print(x,y)
window.style = Style()
window.style.theme_use("clam")
window.title("Rax m3u8视频下载器")
window.geometry("%dx%d+%d+%d" %(ww,wh,x,y))
window.resizable(0,0)
frame_row1 = customtkinter.CTkFrame(master=window,width=490,corner_radius=0,height=50)
frame_row1.grid(row=0, column=0, sticky="w",padx=5,pady=2)
frame_row1.grid_propagate(0)
# frame_row1.columnconfigure(0, minsize=50)
frame_row2 = customtkinter.CTkFrame(master=window,width=490,corner_radius=0,height=50)
frame_row2.grid_propagate(0)
frame_row2.grid(row=1, column=0, sticky="w",padx=5,pady=2)
frame_row3 = customtkinter.CTkFrame(master=window,width=490,corner_radius=0,height=50)
frame_row3.grid(row=2, column=0, sticky="w",padx=5,pady=2)
frame_row3.grid_columnconfigure(0,minsize=5)
frame_row3.grid_columnconfigure(4, weight=1)
frame_row3.grid_propagate(0)
frame_row4 = customtkinter.CTkFrame(master=window,width=490,corner_radius=0,height=50)
frame_row4.grid(row=3, column=0, sticky="w",padx=5,pady=2)

#第一行
#各控件初始状态
v53 = customtkinter.StringVar();
l1 = customtkinter.CTkLabel(frame_row1, textvariable = v53,width=50)
v53.set('m3u8地址：')
l1.grid(row=0, column=0,pady=5, padx=0,sticky="nswe")
# l1.place(x=10, y=0, anchor='nw')

#   地址栏
v = customtkinter.StringVar();
e2 = customtkinter.CTkEntry(frame_row1, show=None, textvariable = v,width=240)
v.set('')
e2.grid(row=0, column=1, pady=5, padx=10)

#   清空按钮
b2 = customtkinter.CTkButton(frame_row1, text='清空', width=10, command=clear,fg_color="#D35B58", hover_color="#C77C78")
b2.grid(row=0, column=2, pady=5, padx=12 ,sticky="nswe")

#   粘贴地址按钮
b3 = customtkinter.CTkButton(frame_row1, text='粘贴地址', width=10, command=paste)
b3.grid(row=0, column=3, pady=5, padx=0,sticky="nswe")

#第二行
#   保存位置
v5 = customtkinter.StringVar();
l2 = customtkinter.CTkLabel(frame_row2, textvariable = v5,width=400,anchor='w')
v5.set('文件夹: D:/')
l2.grid(row=0, column=0,pady=5, padx=0,columnspan=2,sticky="nswe")
l2.grid_propagate(0)
#   选择路径按钮
pathselectButton = customtkinter.CTkButton(frame_row2, text='选择路径', width=10, command=choose_dir)
pathselectButton.grid(row=0, column=2, pady=5, padx=12,sticky="w")

#第三行
#   视频名称
v54 = customtkinter.StringVar();
l6 = customtkinter.CTkLabel(frame_row3, textvariable = v54,width=50,anchor='w')
v54.set('视频文件名称：')
l6.grid(row=0, column=0,pady=5, padx=0,sticky="nswe")

#   视频名称栏
v2 = customtkinter.StringVar();
e3 = customtkinter.CTkEntry(frame_row3, show=None, textvariable = v2,width=150)
v2.set('')
e3.grid(row=0, column=1, pady=5, padx=0,sticky="nswe",columnspan=2)

#   下载按钮
b = customtkinter.CTkButton(frame_row3, text='下载', width=10, command=hit_me)
b.grid(row=0, column=5, pady=5, padx=10,sticky="nswe")

#   求捐赠按钮
l5 = customtkinter.CTkLabel(frame_row4, text='软件免费使用，欢迎各位喜欢此软件的大佬打赏，谢谢。\nQQ讨论群：519565890')
l5.grid(row=0, column=1, rowspan=2,pady=5, padx=10,sticky="nswe")
global flag
flag = 0
switch_2 = customtkinter.CTkSwitch(master=frame_row4,text="明亮/暗黑主题",command=change_mode,height=20)
switch_2.grid(row=1, column=0, rowspan=2,pady=5, padx=10,sticky="nswe")
window.option_add('*tearOff', False)

#菜单栏
menubar = tkinter.Menu(window)
window['menu'] = menubar
help_menu = tkinter.Menu(menubar)
menubar.add_command(label='搜索m3u8',command=lambda: searchmain())
menubar.add_command(label='捐助作者',command=lambda: donate())
menubar.add_cascade(menu=help_menu, label='帮助')

#帮助 下拉菜单
help_menu.add_command(label='更新内容',command=lambda: update())
help_menu.add_command(label='关于',command=lambda: about())

# 进入消息循环
window.mainloop()
