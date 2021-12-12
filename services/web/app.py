from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, FlexSendMessage
)
from .crawler import Keyword_search
from datetime import datetime

app = Flask(__name__)

line_bot_api = LineBotApi(
    'AW9KO7SazRUPJq8I/8ALC8JbWPNxsdoJw+i50QoO9jKEwbcLy+INwiOWGDAVIx/tLPksmXRQM5Nus/krZcp5Yueb5FDnGxp/ZzvkSvDqoAKiegi3fa24rSv9IG/9Eb0juhZOQLQvhdIA9ZVnVcX4wAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('66d9c5847958f6b96e81c17087ca09a4')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


def carousel_msg(search):
    contents = dict()
    contents['type'] = 'carousel'
    result = Keyword_search(keyword=search).scrape()

    _contents = [{
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": item["img_url"],
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "uri": item["url"]
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": item["title"],
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": item["rate"],
                            "size": "sm",
                            "color": "#999999",
                            "margin": "md",
                            "flex": 0
                        }, {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "地址",
                                    "color": "#aaaaaa",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": item["address"],
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 5
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "均消",
                                    "color": "#aaaaaa",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": item["price"],
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 5
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "簡介",
                        "uri": item["url"]
                    }
                }
            ],
            "flex": 0
        }
    } for item in result]

    _contents.append(
        {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "找不到滿意的店家嗎？我們還有更多優質的選擇供您參考",
                        "weight": "bold",
                        "size": "xl"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "點我看更多",
                            "uri": "http://google.com"
                        }
                    }
                ],
                "flex": 0
            }
        }
    )

    contents['contents'] = _contents

    message = FlexSendMessage(alt_text='搜尋結果', contents=contents)

    return message


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    carousel = carousel_msg(event.message.text)
    reply = []
    reply.append(carousel)

    line_bot_api.reply_message(event.reply_token, reply)


if __name__ == "__main__":
    app.run()
