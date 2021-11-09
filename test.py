import os
import requests as req
from bs4 import BeautifulSoup

url = "https://athletix.run"

def get_pgc(i):
    html = req.get(url + "/contents")
    soup = BeautifulSoup(html.content, "html.parser")
    titles = soup.find_all(class_="articleCard-title")
    links = soup.find_all(class_="articleList-item")
    link = links[i].a["href"]
    # print(links[0].a["href"]) #PGCリンク
    # print(titles[0].text) # PGCタイトル
    return titles[i].text, link


def get_pgc_status(i):
    html = req.get(url + "/contents")
    soup = BeautifulSoup(html.content, "html.parser")
    status = soup.find_all(class_="articleCard-status tags")
    status_message = status[i].text.replace(" ", "").strip()
    if status_message == "終了":
        return False
    else:
        return True


def get_company_name(k):
    html = req.get(k)
    soup = BeautifulSoup(html.content, "html.parser")
    temp = soup.find('h2')
    name = temp.text
    return name


# ポート番号の設定
if __name__ == "__main__":
    get_pgc_status()
