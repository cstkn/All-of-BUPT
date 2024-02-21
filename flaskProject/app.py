# flask app
# 导入flask模块，用于创建web应用
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
import time
import requests
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/buptknown'
app.secret_key = 'ww3erypwofshdaugyw3wr'
CORS(app)
db = SQLAlchemy(app)
users = {}
proxies = \
    {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890",
    }


# model = torch.load("")
def call_model(a):
    # res = requests.get("") # 本地国内api
    # res = requests.get("https://www.openai.com",proxies=proxies) # 使用代理

    # res = model(a)   # self load
    # return res

    return a


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashid = db.Column(db.String(256), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    qid = db.Column(db.String(80), unique=True, nullable=False)
    ans = db.Column(db.String(8192), nullable=True)

    def __repr__(self):
        return '<Result  %r %r>' % (self.qid, self.ans)


# 定义一个函数，用于根据用户名和时间戳生成一个唯一的用户id
def generate_user_id(user):
    # 获取当前时间戳，转换为字符串
    timestamp = str(time.time())
    # 将用户名和时间戳拼接起来，编码为字节，然后用sha256算法加密，再转换为十六进制字符串
    hashid = hashlib.sha256((user + timestamp).encode()).hexdigest()
    return hashid
    # 返回用户id


def create_qid(question):
    timestamp = str(time.time())
    qid = hashlib.sha256((question+timestamp).encode()).hexdigest()
    new_qid = Result(qid=qid)
    # 将新用户添加到会话中
    db.session.add(new_qid)
    # 提交更改到数据库
    db.session.commit()
    return qid


def create_tables():
    db.create_all()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 添加新用户到User数据库的函数
def add_user(username, password):
    new_user = User(username=username, password=password)
    # 将新用户添加到会话中
    db.session.add(new_user)
    # 提交更改到数据库
    db.session.commit()


# 添加哈希id
def add_hash(username, hashid):
    user = User.query.filter_by(username=username).first()
    # 查询指定用户名的用户
    # 如果用户存在，为其设置新的 hashid
    user.hashid = hashid
    # 提交更改到数据库
    db.session.commit()


# 定义一个路由，用于处理根路径的请求
@app.route('/')
def index():
    create_tables()  # 如果你修改了表结构，你就到mysql里drop tables *;然后把这行注释删了，跑create_tables()，然后再把这行注释了
    # 渲染index.html模板，返回给客户端
    return render_template('login.html')


# 注册页面的路由
@app.route('/register', methods=['POST'])
def register():
    # 从表单中获取用户名和密码
    username = request.form.get('username')
    password = request.form.get('password')
    # 检查用户名是否已经存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return 'Username already exists. Please choose a different username.'

    # 添加新用户
    add_user(username, password)
    # 注册成功后，重定向到登录页面
    return render_template('login.html')


# 定义一个路由，用于处理/login路径的请求，只接受POST方法
@app.route('/login', methods=['POST'])
def login():
    # 从表单中获取用户名和密码
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()  # 重点看 怎么查数据
    hashid = generate_user_id(user.username)
    add_hash(user.username, hashid)
    true_password = user.password
    session['username'] = username
    # 检查密码
    if password == true_password:
        # 重定向到第二个页面，将用户id作为参数传递
        return redirect(url_for('second', hashid=hashid))
    else:
        # 返回一个错误信息
        return 'Invalid password'


# 定义一个路由，用于处理/second/<user_id>路径的请求，其中<user_id>是一个变量
@app.route('/second/<hashid>')
@login_required
def second(hashid):
    # 从字典中根据用户id获取用户名
    username = users.get(hashid)
    # 渲染second.html模板，传入用户名和用户id
    return render_template('welcome.HTML', username=username, hashid=hashid, model_ret=call_model("wawawaaadsafasdf"))


@app.route('/ask', methods=['POST'])
@login_required
def ask():
    data = request.get_json()  # 获取请求的json数据
    username = session.get("username")
    # username = data.get('username')
    qid = create_qid(data.get('question'))
    while True:
        answer = Result.query.filter_by(qid=qid).first()

        if answer.ans:
            response = {
                'username': username,
                'answer': answer.ans,
                'timestamp': datetime.now().isoformat()
            }
            return jsonify(response)
        else:
            db.session.commit()
            time.sleep(2)
            print(answer)


# 这里是处理问题和生成回答的逻辑
    # 在这个示例中，我们只是简单地将问题原样返回



# 如果这个文件是主程序，就运行flask应用，开启调试模式
if __name__ == '__main__':
    app.run(debug=True)
