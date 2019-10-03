import sys
import os
from time import sleep
from secrets import choice
from copy import deepcopy
from datetime import datetime
from codecs import open


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as Soup


class OnePerson:
    
    def __init__(self):
        self.uid = 0
        self.name = ''
        self.fan = -1    # fan or not, -1 for not set for future use...
        self.reply = []
        self.got= ''
        
    def __str__(self):
        return f'{self.name}, {self.uid}'
                                                          
    @property
    def link(self):
        return f'https://space.bilibili.com/{self.uid}'


class StartSection:
    
    def __init__(self, chrome_location, url):
        
        self.url = url
        self.dict_of_persons = dict()
        self.page_ct = 1
        self.reply_ct = 0
        options = Options()
        options.binary_location = chrome_location
        
        self.generate_html()
        self.display = webdriver.Chrome(options=options, executable_path="chromedriver.exe", )
        self.display.get(self.result_html)
        self.display.refresh()
        
        self.driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe", )
        self.driver.get(self.url)

        self.refresh()
        
    def refresh(self):
        self.html = self.driver.page_source
    
    def generate_html(self):
        self.cwd = os.getcwd()
        self.result_html = os.path.join(self.cwd, 'result.html')
        
        with open(self.result_html, 'w') as html:
            html.write(r'<center><img src=".\loading.gif" alt=”loading” /><br>')
            html.write(f'<font size="6" face="Microsoft YaHei">正在打开<br>{self.url}<br>等待载入完成后请开始抓取数据。。。</font>')

    def get_one_page(self):
        soup = Soup(self.html, 'html.parser')
        divs = soup.findAll("div", {"class": "list-item"})
        
        for div in divs:
            self.reply_ct += 1
            face = div.find('div', {'class': 'user-face'})
            uid = int(face.a.attrs['data-usercard-mid'])
            link = face.a.attrs['href']
            con = div.find('div', {'class': 'con'})
            time = con.find('span', {'class': 'time'}).text
            text = con.find('p', {'class': 'text'}).text
            name = con.find('div', {'class': 'user'}).a.text
            
            if uid in self.dict_of_persons:
                self.dict_of_persons[uid].reply.append([time, text])
            else:
                p = OnePerson()
                p.uid = uid
                p.name = name
                p.reply = [[time, text]]
                self.dict_of_persons[uid] = p
    
    def get_all_pages(self):
        
        self.driver.find_element_by_class_name('new-sort').click()
        sleep(3)
        
        with open(self.result_html, 'w') as html:
            html.write(r'<center><img src=".\loading.gif" alt=”loading” /><br>')
            html.write(f'<font size="6" face="Microsoft YaHei">正在抓取数据，请稍后。。。<br>{self.url}</font>')
        self.display.refresh()
        
        while True:
            self.refresh()
            self.get_one_page()
            
            try:
                self.driver.find_element_by_class_name('next').click()
                self.page_ct += 1
                sleep(choice(range(3, 6)))
            except:
                break
        
        print(f'Done with {self.url}.')
        self.report()
        self.display_all()
        
    def report(self):
        print(f'  page: {self.page_ct}\n reply: {self.reply_ct}\nperson: {len(self.dict_of_persons)}')
    
    def print_all(self):
        for i, p in enumerate(self.dict_of_persons.values()):
            print(f'#{i+1}')
            print(p.name, p.link)
            for j in p.reply:
                print(j)
            print()
            
    def display_all(self):
        with open(self.result_html, 'w', 'utf-8') as html:
            html.write(f'<font size="4" face="Microsoft YaHei">{datetime.now()}，抓取数据完成。<br>')
            html.write(f'&emsp;&emsp;页数：{self.page_ct}<br>&emsp;回复数：{self.reply_ct}<br>实际人数：{len(self.dict_of_persons)}<br><br>')
            
            for i, p in enumerate(self.dict_of_persons.values()):
                html.write(f'#{i+1}<br>')
                html.write(f'<b>{p.name}</b>&nbsp;&nbsp;&nbsp;<a href="{p.link}">{p.link}</a><br>')
                for j in p.reply:
                    html.write(f'{j[0]}&nbsp;&nbsp;{j[1]}<br>')
                html.write('<br>')
            html.write('</font>')
        self.display.refresh()

    @staticmethod
    def choose_one_key(dict_pool):
        
        assert isinstance(dict_pool, dict), 'Please input a dictionary as the pool'
        
        if dict_pool:
            return choice(list(dict_pool.keys()))
        else:
            raise ValueError('Empty pool dictionary')

    def choose_mul(self, num, rank=[]):
        
        if rank:
            assert len(rank) == num, '奖项数量需要等于中奖人数'
        
        self.result = []
        pool_copy = deepcopy(self.dict_of_persons)
        
        for i in black_list:
            try:
                del pool_copy[i]
            except KeyError:
                pass
        
        for i in range(num):
            key = self.choose_one_key(pool_copy)
            try:
                pool_copy[key].got = rank[i]
            except IndexError:
                pass # error already detected by assertion.

            self.result.append(pool_copy[key])
            
            del pool_copy[key]

    def print_result(self, wait=0.3):
        
        print(f'    抽奖时间：{datetime.now()}\n抽奖动态链接：{self.url}\n    参与人数：{len(self.dict_of_persons)}\n    中奖人数：{len(self.result)}\n   黑名单uid：', end='')
        for i in black_list:
            print(i, end='  ')
        print('\n\n')
        print('中奖名单：\n')
        
        for i in self.result:
            sleep(wait)
            if i.got:
                print(i.got)
            print(i.name, i.link)
            print(i.reply, end='\n\n')
        print('\n\n本获奖名单由【大叔厨房·Bilibili动态抽奖小软件】生成\n详细情况请访问软件页（git）\n\n欢迎支持访问大叔厨房视频频道：\nBilibili: https://space.bilibili.com/11909\nYoutube: https://www.youtube.com/channel/UCQMfI0Xdr3-1d6F_Fjsvlxw\n\n谢谢使用~')
        
    def display_result(self, wait=0.5):
        header = f'<font size="4" face="Microsoft YaHei">&emsp;&emsp;抽奖时间：{datetime.now()}<br>抽奖动态链接：{self.url}<br>&emsp;&emsp;参与人数：{len(self.dict_of_persons)}<br>&emsp;&emsp;中奖人数：{len(self.result)}<br>&emsp;黑名单&ensp;uid：'
        header += "&emsp;".join((str(i) for i in black_list))
        header += r'<br><br><br>中奖名单：<br><br>'
        
        with open(self.result_html, 'w', "utf-8") as html:
            html.write(header)
            
            html.write(r'<img src=".\loading.gif" alt=”loading” /><br>')
            html.write(r'正在抽奖。。。<br><br><br><br>')
            html.write(f'</font>')
        self.display.refresh()
        sleep(1)

        for i in range(len(self.result)):
            sleep(wait)

            with open(self.result_html, 'w', "utf-8") as html:
                html.write(header)
                
                for j in range(i+1):
                    p = self.result[j]
                    if p.got:
                        html.write(f'{p.got}:<br>')
                    html.write(f'<b>{p.name}</b>&nbsp;&nbsp;&nbsp;<a href="{p.link}">{p.link}</a><br>')
                    for k in p.reply:
                        html.write(f'{k[0]}&nbsp;&nbsp;{k[1]}<br>')
                    html.write('<br>')
                    
                if i+1 < len(self.result):
                    html.write(r'<img src=".\loading.gif" alt=”loading” /><br>')
                    html.write(r'正在抽奖。。。<br><br><br><br>')
                else:
                    html.write('<br><br><br></font><font size="2" face="Microsoft YaHei">本获奖名单由【大叔厨房·Bilibili动态抽奖小软件】生成<br>详细情况请访问软件页（git）<br><br>欢迎支持访问大叔厨房视频频道：<br>Bilibili: <a href="https://space.bilibili.com/11909">https://space.bilibili.com/11909</a><br>Youtube: <a href="https://www.youtube.com/channel/UCQMfI0Xdr3-1d6F_Fjsvlxw">https://www.youtube.com/channel/UCQMfI0Xdr3-1d6F_Fjsvlxw</a><br><br>谢谢使用~')
                
                html.write(f'</font>')
            self.display.refresh()







## ==========settings=============

### chrome 路径:
chrome_location = r"E:\PortableApps\PortableApps\GoogleChromePortable\App\Chrome-bin\chrome.exe"

### bilibili动态 地址:
url = r'https://t.bilibili.com/305801383717966503'

### 黑名单，比如自己的或者仇人的 uid:
black_list = [11909]  ## in order NOT to get yourself

### 抽奖等级，或者奖品，或者留空
#### 举例 1： rank = ['三等奖'] * 4 + ['二等奖'] * 3 + ['一等奖'] * 2 + ['特等奖']
#### 举例 2： rank = ['冰箱'] * 3 + ['彩电'] * 2 + ['洗衣机']
#### 举例 3： rank = []
#### 数量需要等于下面设置的中奖人数
rank = []

### 中奖人数
number = 10

### 开奖间隔，心跳时间，单位：喵
wait = 2

## =========end of settings==========



def step1():
    global s
    s = StartSection(chrome_location, url)

def step2():
    s.get_all_pages()

def step3():
    s.choose_mul(number, rank)
    s.display_result(wait)



