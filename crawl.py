import os
import chardet
import requests

def urllink(link):
    html_1 = requests.urlopen(link,timeout=120).read()
    encoding_dict = chardet.detect(html_1)
    web_encoding = encoding_dict['encoding']
    if web_encoding == 'utf-8' or web_encoding == 'UTF-8':
        html = html_1
    else :
        html = html_1.decode('gbk','ignore').encode('utf-8')
    return html

def download(links, base_dir):
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    index=0
    for link in links:
        for key in link:
            if key.get('thumbURL') is not None:
                print('downloading image %s'%key.get('thumbURL'))
                req=requests.get(key.get('thumbURL'))
                with open(os.path.join(base_dir, '%d.jpg'%index), 'wb') as f:
                    f.write(req.content)
                index+=1
            else:
                print('image not exists')
    print('Download %d images'%index)
        
    
def get_dynamic_pages(url, keyword, page_num):
    params=[]
    for i in range(30,30*page_num+30,30):
        params.append({
                      'tn': 'resultjson_com',
                      'ipn': 'rj',
                      'ct': 201326592,
                      'is': '',
                      'fp': 'result',
                      'queryWord': keyword,
                      'cl': 2,
                      'lm': -1,
                      'ie': 'utf-8',
                      'oe': 'utf-8',
                      'adpicid': '',
                      'st': -1,
                      'z': '',
                      'ic': 0,
                      'word': keyword,
                      's': '',
                      'se': '',
                      'tab': '',
                      'width': '',
                      'height': '',
                      'face': 0,
                      'istype': 2,
                      'qc': '',
                      'nc': 1,
                      'fr': '',
                      'pn': i,
                      'rn': 30,
                      'gsm': '1e',
                      '1488942260214': ''
                  })
    urls = []
    for i in params:
        urls.append(requests.get(url,params=i).json().get('data'))
    return urls
    
def crawl():
    page='https://image.baidu.com/search/acjson'
    #for i in range(1,2):
    base_dir=os.getcwd()+'../images'
    #print(base_dir)
    links=get_dynamic_pages(page, '航母战斗机', 20)
    download(links, base_dir)
    

if __name__=='__main__':
    crawl()