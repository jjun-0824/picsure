from flask import Flask, request, render_template, url_for,jsonify
import os
from ultralytics import YOLO
import cv2
import time
import sys
import requests
import mod_dbconn
import boto3
from decouple import config

AWS_ACCESS_KEY = config('AWS_ACCESS_KEY')
AWS_SECRET_KEY = config('AWS_SECRET_KEY')

app = Flask(__name__)

def load_yolo_model(model_path):
    return YOLO(model=model_path, task='detect')

def is_person(image_filepath, model):
    results = model.predict(image_filepath)
    is_person_detected = any(0 in list(result.boxes.cls) for result in results)
    return is_person_detected


def transform_entire_image(image_filepath):
    image = cv2.imread(image_filepath)
    x, y, w, h = 0, 0, image.shape[1], image.shape[0]
    roi = image[y:y+h, x:x+w]
    factor = 10
    small_roi = cv2.resize(roi, (w // factor, h // factor))
    mosaic_roi = cv2.resize(small_roi, (w, h), interpolation=cv2.INTER_NEAREST)
    image[y:y+h, x:x+w] = mosaic_roi
    return image


def transform_faces(image_filepath, model):
    image = cv2.imread("." + image_filepath)
    results = model.predict(image_filepath)

    for result in results:
        boxes = result.boxes.xywh.tolist()

        for box in boxes:
            x, y, w, h = map(int, list(box))
            roi = image[y-h:y+h, x-w:x+w]
            factor = 20
            small_roi = cv2.resize(roi, (2*w // factor, 2*h // factor))
            mosaic_roi = cv2.resize(small_roi, (2*w, 2*h), interpolation=cv2.INTER_NEAREST)
            image[y-h:y+h, x-w:x+w] = mosaic_roi

    return image

@app.route('/process_image', methods=['POST'])
def process_image():
    file = request.files['file']
    filename = file.filename
    filepath = os.path.join('static/uploads', filename)
    file.save(filepath)

    yolo_model_person = load_yolo_model('yolov8n.pt')
    yolo_model_face = load_yolo_model('yolov8n-face.pt')

    if is_person(filepath, yolo_model_person):
        transformed_image = transform_faces(filepath, yolo_model_face)
    else:
        transformed_image = transform_entire_image(filepath)

    return {}

#s3 버킷과 연동
s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_SECRET_KEY)

#s3 test - image upload시 s3버킷에 업로드 확인, url 해당 image의 url인 것 확인
#image upload : input type="file"을 통해 업로드 받음
#s3버킷에 업로드 후 해당 image의 url 바로 db에 update
@app.route('/imgupload', methods=['POST'])
def upload_file():
    file = request.files['file']

    s3.upload_fileobj(file, 'myphotobuckettt', file.filename)

    db_class = mod_dbconn.Database()
    url = f"https://myphotobuckettt.s3.ap-northeast-2.amazonaws.com/{file.filename}"

    sql = "UPDATE User SET p2 = %s WHERE user_id = 1"
    db_class.execute(sql, (url,))
    db_class.commit()

    return f"https://myphotobuckettt.s3.ap-northeast-2.amazonaws.com/{file.filename}"

#s3 test - url을 통해서 image가져오기
#image 불러올 때 img src="url"로 불러오기 가능 확인
#db에서 해당 image의 url을 가져와서 그 url을 img src로 사용하도록 html로 넘겨주는 방식 (<img src="{{ image_url }}" alt="Rendered Image">)
@app.route('/getimg')
def get_file():
    db_class = mod_dbconn.Database()

    sql = "SELECT p2 FROM app_db.User WHERE user_id = 1"
    res = db_class.executeOne(sql)

    if res and 'p2' in res:
        url = res['p2']         #res에서 p2값 url을 추출

        #return render_template('img.html', image_url=url)      #해당 url값을 img src로 사용할 수 있도록 image_url을 통해 넘겨줌 (test시)
        return jsonify({'image_url': url})                      #해당 url값을 json 형식으로 return


@app.route('/db')
def select():
    db_class = mod_dbconn.Database()

    sql = "SELECT link_id, url, password FROM app_db.Link"
    row = db_class.executeAll(sql)

    print(row)

    #return render_template('db.html', resultData=row[0])

    return row


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
    link="https://"
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

    # 서버측으로 POST요청 보내는 경우
    url = 'http://server_domain/saveFavorA'
    data = {'photo_num': photo_num, 'favor': favor}

    response = requests.post(url, data=data)            #저장된 data들과 함께 서버의 엔드포인트로 POST요청을 보냄
    print(response.text)
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
        if photo_num in [1, 2, 3] and favor in ['Yes', 'No']:
            resp_dict_2['user_a'][photo_num] = favor          #해당되는 photo_num과 그에 대한 user_a의 response를 dictionary에 저장

    # 서버측으로 POST요청 보내는 경우
    url = 'http://server_domain/saveFavorA'
    data = {'photo_num': photo_num, 'favor': favor}

    response = requests.post(url, data=data)            #저장된 data들과 함께 서버의 엔드포인트로 POST요청을 보냄
    print(response.text)
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
    app.run(host='0.0.0.0', port=5000, debug=True)
