from flask import Flask, request, render_template, url_for,jsonify
import os
import time
import sys
import requests

app = Flask(__name__)

@app.route('/')
def index():
    # 기본적으로 이 index 함수가 실행됨.
    return render_template('get_url.html')

@app.route('/getphoto/1')
def get_photo_a():
    # 기본적으로 이 index 함수가 실행됨
    return render_template('get_photo_a.html')

@app.route('/getphoto/2')
def get_photo_b():
    # 기본적으로 이 index 함수가 실행됨.
    return render_template('get_photo_b.html')

@app.route('/exchange/1')
def exchange_a():
    # 기본적으로 이 index 함수가 실행됨.
    return render_template('exchange_a.html')


@app.route('/exchange/2')
def exchange_b():
    # 기본적으로 이 index 함수가 실행됨.
    return render_template('exchange_b.html')


@app.route('/fail')
def fail():
    # 기본적으로 이 index 함수가 실행됨.
    return render_template('fail.html')

@app.route('/success')
def success():
    # 기본적으로 이 index 함수가 실행됨.
    return render_template('success.html')
@app.route('/link')
def get_link():
    link="https://1234"
    # 전달해주고 싶은 결과값을 html내에서 변경해주고 싶을 때 하단과 같은 방법으로 변환
    return render_template('home.html', url=link) # 넘겨주고 싶은 변수 옆에 적어넣기

@app.route('/upload', methods = ['POST'])
def upload():
    file= request.files['file'] # 사진이나 입력값은 request로 받기
    filename = file.filename
    filepath=os.path.join('static/uploads', filename)
    file.save(filepath)

    return render_template('get_photo_a.html',image=filepath)

resp_dict = {               #user_a의 각 사진에 대한 response를 저장하는 dictionary
    'user_a': {
        1: None,
        2: None,
        3: None
    }
}

@app.route('/saveFavorA', methods=['POST'])
def saveFavorA():
    data = request.form         #photo_num과 user_a의 favor 받아옴

    photo_num = int(data['photo_num'])
    favor = data['favor']

    if photo_num in [1, 2, 3] and favor in ['Yes', 'No']:
        resp_dict['user_a'][photo_num] = favor          #해당되는 photo_num과 그에 대한 user_a의 response를 dictionary에 저장

    #서버측으로 POST요청 보내는 경우
    # url = 'http://server_domain/saveFavorA'
    # data = {'photo_num': photo_num, 'favor': favor}

    # response = requests.post(url, data=data)            #저장된 data들과 함께 서버의 엔드포인트로 POST요청을 보냄
    # print(response.text)
    return {}

@app.route('/getFavorA', methods=['GET'])               
def getFavorA():

    photo_num = int(request.args.get('photo_num'))  #몇번째 사진인지 photo_num으로 받아옴

    if photo_num in [1, 2, 3]:
        favor = resp_dict['user_a'].get(photo_num)      #해당 photo_num에 대한 'favor'를 dictionary에서 받아옴

        if favor is not None:                           #favor이 None이 아니라면 'Yes'인지 'No'인지 확인 후 'Yes'이면 result: true를 json형식으로 return, 'No'이면 result: false를 json형식으로 return
            return jsonify({'result': 'true' if favor == 'Yes' else 'false'})
        else:                                           #favor이 None이라면 아직 사용자의 응답이 선택되지 않았으므로 result: yet을 json형식으로 return
            return jsonify({'result': 'yet'})
        
resp_dict_2 = {               #user_a의 각 사진에 대한 response를 저장하는 dictionary
    'user_b': {
        1: None,
        2: None,
        3: None
    }
}
@app.route('/saveFavorB', methods=['POST'])
def saveFavorB():
    data = request.form         #photo_num과 user_a의 favor 받아옴

    photo_num = int(data['photo_num'])
    favor = data['favor']

    if photo_num in [1, 2, 3] and favor in ['Yes', 'No']:
        resp_dict_2['user_b'][photo_num] = favor          #해당되는 photo_num과 그에 대한 user_a의 response를 dictionary에 저장

    #서버측으로 POST요청 보내는 경우
    # url = 'http://server_domain/saveFavorA'
    # data = {'photo_num': photo_num, 'favor': favor}

    # response = requests.post(url, data=data)            #저장된 data들과 함께 서버의 엔드포인트로 POST요청을 보냄
    # print(response.text)
    return {}

@app.route('/getFavorB', methods=['GET'])               
def getFavorB():
    photo_num = int(request.args.get('photo_num'))      #몇번째 사진인지 photo_num으로 받아옴

    if photo_num in [1, 2, 3]:
        favor = resp_dict_2['user_b'].get(photo_num)      #해당 photo_num에 대한 'favor'를 dictionary에서 받아옴

        if favor is not None:                           #favor이 None이 아니라면 'Yes'인지 'No'인지 확인 후 'Yes'이면 result: true를 json형식으로 return, 'No'이면 result: false를 json형식으로 return
            return jsonify({'result': 'true' if favor == 'Yes' else 'false'})
        else:                                           #favor이 None이라면 아직 사용자의 응답이 선택되지 않았으므로 result: yet을 json형식으로 return
            return jsonify({'result': 'yet'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
