from urllib import parse
from urllib import request
from lxml import etree
import time

class Novel:
    def __init__(self,*args):
        self.name = args[0]
        self.dict = args[1]
        self.txt = ''
        for key in sorted(self.dict):
            self.txt = self.txt + self.dict[key]

    def write(self):
        f = open(self.name+'.txt','w')
        f.write(self.txt)
        f.close()

#获取网页源代码
def get_http_page(url,**kw):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }
    req = request.Request(url,headers=headers)
    response = request.urlopen(req)
    page = response.read()
    encoding = 'gbk'
    if kw:
        encoding = kw['encoding']
    page = page.decode(encoding)
    return page

#获取漫画目录
def get_comics_directory(url):
    url_list = []
    page = get_http_page(url,encoding='utf-8')
    html = etree.HTML(page)
    result = html.xpath('/html/body/div[2]/div/div[2]/h3/a')
    elment_select = None
    if len(result):
        url2 = result[0].get('href')
    if url2:
        page = get_http_page(url2)
        html = etree.HTML(page)
        elment_select = html.xpath('/html/body/div[4]/div[9]/span[2]/select')
        if len(elment_select):
            result_option = elment_select[0].findall('option')
            for option in result_option:
                url_list.append('https://m.wenxuemi6.com{}'.format(option.get('value')))
    return url_list

def downdload_txt(url_list,**kw):
    if kw:
        start = int(kw['start'])
        stop = int (kw['stop'])
        if start >= 0 and start < len(url_list) and stop > start and stop <len(url_list):
            count = kw['start']
            count_max = kw['stop']
    else:
        count = 0
        count_max = len(url_list)
    print('正在爬取目录和章节地址,请稍等……')
    d = {}
    while count < count_max:
        url = url_list[count]
        page = get_http_page(url)
        html = etree.HTML(page)
        result = html.xpath('/html/body/div[4]/ul[2]/li/a')
        txt = ''
        if type(result).__name__ == 'list':
            for l in result:
                url = 'https://m.wenxuemi6.com{}'.format(l.get('href'))
                #url_list.append('https://m.wenxuemi6.com{}'.format(l.get('href')))
                print('Download chapters by URL:{}'.format(url))
                d2 = {'{}'.format(count): ''}
                page = get_http_page(url)
                html = etree.HTML(page)
                url_next = html.xpath('//*[@id="pb_next"]')
                t = html.xpath('//*[@id="nr1"]/text()')
                t2 = html.xpath('//*[@id="nr1"]/p')
                txt_title = ''
                txt_title_list = html.xpath('//*[@id="nr_title"]/text()')
                if type(txt_title_list).__name__ == 'list':
                    if (len(txt_title_list) == 1):
                        txt_title = txt_title_list[0]
                txt = txt + txt_title + '\r\n'
                for l2 in t:
                    txt = txt + l2 + '\r\n'
                if type(t2).__name__ == 'list':
                    if len(t2) == 1:
                        url = 'https://m.wenxuemi6.com{}'.format(l.get('href')[:-5] + '_2.html')
                        print('Download chapters by URL:{}'.format(url))
                        page = get_http_page(url)
                        html = etree.HTML(page)
                        t = html.xpath('//*[@id="nr1"]/text()')
                        for l2 in t:
                            txt = txt + l2 + '\r\n'
                d2['{}'.format(count)] = txt
                d.update(d2)
                time.sleep(1)
    return d



if __name__ == '__main__':
    txt_name = input("请输入要搜索的书名:")
    url = 'https://m.wenxuemi6.com/search.php?keyword={}'.format(parse.quote(txt_name))
    referer = url
    url_list = get_comics_directory(url)
    #下载第一页目录下的小说
    d = downdload_txt(url_list,start=0,stop=1)
    n1 = Novel(txt_name,d)
    #写出文件 [txt_name].txt 到当前目录下
    n1.write()

    #下载全本小说
    d2 = downdload_txt(url_list,start=0,stop=1)
    n2 = Novel(txt_name,d2)
    #写出文件 [txt_name].txt 到当前目录下
    n2.write()


