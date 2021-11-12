import os
import sys
import traceback

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import db_manager
import pgc_manager


app = Flask(__name__)

#環境変数設定
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)
app.config['SQLALCHEMY_DATABASE_URI'] = db_manager.db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


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


def send_message():
    n = 0
    result = ''
    for i in range(19, -1, -1):
        title, link = pgc_manager.get_pgc(i)
        exist_pgc = db_manager.is_exist(link)
        if exist_pgc:
            continue
        elif pgc_manager.get_pgc_status(i):
            db_manager.add_pgc(link)
            continue
        else:
            db_manager.add_pgc(link)
            name = pgc_manager.get_company_name(link)
            pgc_type = "チャレンジ" if "challenges" in link else "イベント"
            line_bot_api.broadcast(TextSendMessage(text="新しい{}が配信されました。\n{}\n{}\n{}".format(pgc_type, name, title, pgc_manager.URL + link)))
            n += 1
    else:
        result = "{}件のPGCが送信されました。".format(n)
        return result


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    if "最新" in event.message.text:
        latest_pgc = pgc_manager.get_latest_pgc()
        txt = "{}\n{}\n{}".format(
            latest_pgc["name"], latest_pgc["title"], latest_pgc["url"])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=txt))


if __name__ == "__main__":
    i = 0
    try:
        i = int(sys.argv[1])
    except:
        pass
    if i == 1:
        n = send_message()
        print(n)
    else:
        port = int(os.getenv("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
