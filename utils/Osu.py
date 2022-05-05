import requests as r
from bs4 import BeautifulSoup
import json
from flask import send_from_directory
from tqdm import tqdm


def MapDownloader(mapid, cookie, novideo):
    url = f'https://osu.ppy.sh/beatmapsets/{mapid}'
    html = r.get(url)
    # with open('./test.html', 'wt', encoding='utf8') as f:
    #     f.write(html.text)
    soup = BeautifulSoup(html.text, 'lxml')
    data = soup.find_all(
        'script', id='json-beatmapset')
    result = json.loads(data[0].text)
    # with open('./data.json', 'wt', encoding='utf8') as f:
    #     f.write(json.dumps(result))
    title = result['title_unicode']
    artist = result['artist_unicode']
    if novideo:
        Downloadurl = f'https://osu.ppy.sh/d/{mapid}n'
    else:
        Downloadurl = f'https://osu.ppy.sh/d/{mapid}'
    topicid = result["legacy_thread_url"].replace('https://osu.ppy.sh/community/forums/topics/','')
    headers = {
        'Host': 'osu.ppy.sh',
        'Connection': 'close',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Microsoft Edge";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': f'https://osu.ppy.sh/community/forums/topics/{topicid}?n=1',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie
        }
    download(Downloadurl, f'/.cache/{mapid}.osz', headers)
    # content = response.content
    # with open(f'./.cache/{mapid}.osz', 'wb') as f:
    #     f.write(content)
    return send_from_directory('/.cache', f'{mapid}.osz', as_attachment=True, download_name=f'{title} - {artist}.osz')

def download(url: str, fname: str, headers: dict):
    # 用流stream的方式获取url的数据
    resp = r.get(url, stream=True, headers=headers)
    # 拿到文件的长度，并把total初始化为0
    total = int(resp.headers.get('content-length', 0))
    # 打开当前目录的fname文件(名字你来传入)
    # 初始化tqdm，传入总数，文件名等数据，接着就是写入，更新等操作了
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
