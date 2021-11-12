import os
import traceback

import requests as req
from bs4 import BeautifulSoup
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
Base = declarative_base()
URL = "https://athletix.run"

#環境変数取得
# LINE Developersで設定されているアクセストークンとChannel Secretをを取得し、設定します。
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


class PGC(Base):
    __tablename__ = "pgc"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(200))


#PostgreSQLとの接続用
db_uri = os.environ['DATABASE_URL']
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine(db_uri)
session_factory = sessionmaker(bind=engine)
session = session_factory()

Base.metadata.create_all(bind=engine)


#Webhookからのリクエストをチェックします。
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得します。
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得します。
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    # 署名を検証し、問題なければhandleに定義されている関数を呼び出す。
    try:
        handler.handle(body, signature)
    # 署名検証で失敗した場合、例外を出す。
    except InvalidSignatureError:
        abort(400)
    # handleの処理を終えればOK
    return 'OK'


def get_pgc(i):
    html = req.get(URL + "/contents")
    soup = BeautifulSoup(html.content, "html.parser")
    titles = soup.find_all(class_="articleCard-title")
    links = soup.find_all(class_="articleList-item")
    link = links[i].a["href"]
    # print(links[0].a["href"]) #PGCリンク
    # print(titles[0].text) # PGCタイトル
    return titles[i].text, link

def send_message():
    n = 0
    result = ''
    for i in range(19, -1, -1):
        title, link = get_pgc(i)
        title = title.replace(" ", "")
        pgc = session.query(PGC.url).filter(PGC.url == link).all()
        if pgc != []:
            continue
        elif get_pgc_status(i):
            add_pgc(link)
            continue
        else:
            add_pgc(link)
            name = get_company_name(URL + link).replace(" ", "").strip()
            pgc_type = "チャレンジ" if "challenges" in link else "イベント"
            line_bot_api.broadcast(TextSendMessage(text="新しい{}が配信されました。\n{}\n{}\n{}".format(pgc_type, name, title, URL + link)))
            n += 1
    else:
        if n == 0:
            result = "新しいチャレンジはありません"
        else:
            result = "{}件のPGCが送信されました。".format(n)
    return result

def get_company_name(k):
    html = req.get(k)
    soup = BeautifulSoup(html.content, "html.parser")
    temp = soup.find('h2')
    name = temp.text
    return name

def add_pgc(x):
    pgc_data = PGC(url=x)
    session.add(pgc_data)
    session.commit()

def get_pgc_status(i):
    html = req.get(URL + "/contents")
    soup = BeautifulSoup(html.content, "html.parser")
    status = soup.find_all(class_="articleCard-status tags")
    status_message = status[i].text.replace(" ", "").strip()
    if status_message == "終了":
        return True
    else:
        return False

def get_latest_pgc():
    title, link = get_pgc(0)
    title = title.replace(" ", "")
    name = get_company_name(URL + link).replace(" ", "").strip()
    result = "{}\n{}\n{}".format(name, title, URL + link)
    return result


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    if "最新" in event.message.text:
        txt = get_latest_pgc()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=txt))

if __name__ == "__main__":
    n = send_message()
    print(n)
