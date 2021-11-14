import os

import requests as req
from bs4 import BeautifulSoup

URL = "https://athletix.run"


def get_pgc(i):
    # PGCのタイトルとリンクを取得
    html = req.get(URL + "/contents")
    soup = BeautifulSoup(html.content, "html.parser")
    titles = soup.find_all(class_="articleCard-title")
    links = soup.find_all(class_="articleList-item")
    title = titles[i].text.replace(" ", "")
    link = links[i].a["href"]
    return title, link


def get_latest_pgc():
    # 最新のPGCを取得
    title, link = get_pgc(0)
    title = title.replace(" ", "")
    name = get_company_name(URL + link).replace(" ", "").strip()
    result = {"name": name,
            "title": title,
            "url": URL + link}
    return result


def get_company_name(link):
    # PGCの企業を取得 引数はPGCページ
    html = req.get(URL + link)
    soup = BeautifulSoup(html.content, "html.parser")
    temp = soup.find('h2')
    name = temp.text.replace(" ", "").strip()
    return name


def get_pgc_status(i):
    # PGCの状態 終了:True それ以外:False
    html = req.get(URL + "/contents")
    soup = BeautifulSoup(html.content, "html.parser")
    status = soup.find_all(class_="articleCard-status tags")
    status_message = status[i].text.replace(" ", "").strip()
    if status_message == "終了":
        return True
    else:
        return False


def get_constant_pgc():
    # 常設コンテンツを表示
    constants_name = ["MEETUP", "ASSIST", "TOITS"]
    message = ""
    for name in constants_name:
        link = os.environ[name]
        html = req.get(link)
        soup = BeautifulSoup(html.content, "html.parser")
        titles = soup.find_all(class_="detailContent-heading")
        title = titles[0].text.replace(" ", "").strip()
        message += "{}\n{}\n\n".format(title, link)
    return message.rstrip()
