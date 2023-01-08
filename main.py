from flask import Flask, Response, render_template, send_from_directory, jsonify
from os.path import dirname, abspath
import cv2

root_dir = abspath(dirname(__file__))
root_dir = root_dir.replace("\\", "/")

app = Flask(__name__)

camera = cv2.VideoCapture(1)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/vids/<name>')
def get_video(name):
    return send_from_directory(root_dir + "/data", name)

@app.route('/logs')
def json():
    return send_from_directory(root_dir + "/data", "logs.json")


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host="192.168.240.12")
