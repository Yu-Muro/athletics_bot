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
url = "https://athletix.run"

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

## 1 ##
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


def get_pgc():
    html = req.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    titles = soup.find_all(class_="articleCard-title")
    links = soup.find_all(class_="articleList-item")
    link = links[0].a["href"]
    # print(links[0].a["href"]) #PGCリンク
    # print(titles[0].text) # PGCタイトル
    return titles[0].text, link


def send_message():
    title, link = get_pgc()
    title.replace(" ", "")
    line_bot_api.broadcast(TextSendMessage(text="{}\n{}".format(str(title), url + link)))
    pgc_data = PGC(url = link)
    session.add(pgc_data)
    session.commit()
    print("{}\n{}".format(title, url + link))

# ポート番号の設定
if __name__ == "__main__":
    send_message()
