# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_ask import Ask, question, statement, audio
import json

app = Flask(__name__)
ask = Ask(app, '/')


# 起動時の対応
@ask.launch
def launched():
    return question('ジャービスです。いかがなさいましたか？')

# 音楽を再生
@ask.intent('musicStart')
def music_start():
    # 心拍のload
    file2 = open("heart_rate.json", "r")
    json_dict = json.load(file2)
    heart_rate = json_dict["heart_rate"]

    # 心拍の異常値処理
    if heart_rate > 200:
        heart_rate = 0

    # 条件分岐
    mean_heart_rate = 70
    if heart_rate > mean_heart_rate:
        out_index = 0
    else:
        out_index = 1
        
   # 出力の文章を作成
    speech_0 = '心拍数は{}です。'.format(heart_rate)

    speech_1 = [
        '普段の平均より高いです。落ち着いた曲を再生します', 
        '普段の平均より低いです。テンションが上がる曲を再生します'
    ]

    speech = speech_0 + speech_1[out_index]

    # 音楽URL
    stream_url = [
        "※音楽1のURLをここに書きます※", 
        "※音楽2のURLをここに書きます※"
    ]

    return audio(speech).play(stream_url[out_index])


@ask.intent('AMAZON.PauseIntent')
def stop():
    return audio("Jarvisを終了します").stop()


@ask.intent('AMAZON.StopIntent')
def stop():
    return audio("Jarvisを終了します").stop()


@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
