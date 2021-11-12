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
        return True
    else:
        return False


def get_company_name(k):
    html = req.get(k)
    soup = BeautifulSoup(html.content, "html.parser")
    temp = soup.find('h2')
    name = temp.text
    return name


def send_message():
    n = 0
    for i in range(19, -1, -1):
        title, link = get_pgc(i)
        title = title.replace(" ", "")
        # pgc = session.query(PGC.url).filter(PGC.url == link).all()
        if get_pgc_status(i):
            # add_pgc(link)
            n += 1
            continue
        else:
            # add_pgc(link)
            name = get_company_name(url + link).replace(" ", "").strip()
            pgc_type = "チャレンジ" if "challenges" in link else "イベント"
            # line_bot_api.broadcast(TextSendMessage(text="新しいチャレンジが配信されました。\n   {}\n \n{}\n{}".format(name, title, url + link)))
            print("新しい{}が配信されました。\n   {}\n \n{}\n{}".format(
                pgc_type, name, title, url + link))
    else:
        if n == 20:
            # line_bot_api.broadcast(TextSendMessage(text="新しいチャレンジはありません"))
            result = "新しいチャレンジはありません"
        else:
            result = "{}件のPGCが送信されました。".format(20 - n)
    return result


# ポート番号の設定
if __name__ == "__main__":
    n = send_message()
    print(n)
