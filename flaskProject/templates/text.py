# 导入需要的模块和函数
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
import time

app = Flask(__name__)
#连接到数据库包含了用户密码和数据库地址（账户密码是mysql密码吗？忘记当时怎么设置的rootroot了）
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/buptknown'
#一个密码（是随机设置的吗，还是哪里提供的）
app.secret_key = 'ww3erypwofshdaugyw3wr'
# 常见一个orm映射
db = SQLAlchemy(app)
class User(db.Model):
    # 定义 id 列，自动递增，是唯一标识（不知道什么意思）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 定义 username 列，作为用户名，必须唯一不空
    username = db.Column(db.String(80), unique=True, nullable=False)
    #同上，不能空
    password = db.Column(db.String(120), nullable=False)
    # 定义了一个函数？返回一个username
    def __repr__(self):
        return '<User %r>' % self.username
# 和上面类似，新建了个表格
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(80), unique=True, nullable=False)
    qid = db.Column(db.String(80), unique=True, nullable=False)
    ans = db.Column(db.String(8192), nullable=False)
    def __repr__(self):
        return '<Result %r %r %r>' % (self.uid, self.qid, self.ans)
    #这是以什么是返回的呀json吗
# 我写的一堆废物（这里好像是用不到了
def generate_user_id(username):
    timestamp = str(time.time())
    user_id = hashlib.sha256((username + timestamp).encode()).hexdigest()
    return user_id
# 创建数据库表格（不知道具体的用途）
def create_tables():
    db.create_all()
# 你说的什么状态验证，这个没看懂
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
# 打开页面展示
@app.route('/')
def index():
    return render_template('login.html')
# 登陆
@app.route('/login', methods=['POST'])
def login():
    #传递账号密码
    username = request.form.get('username')
    password = request.form.get('password')
    # 从数据库中查询用户（查了一下，是一个固定语法）
    user = User.query.filter_by(username=username).first()
    # 检查密码是否匹配
    true_password = user.password
    if password == true_password:
        # 状态，这行不太理解
        session['username'] = username
        return redirect(url_for('second', user_id=user.id))
    else:
        # 如果密码不匹配，返回错误信息
        return 'Invalid password'
# 定义处理第二个页面路径的路由，需要登录后才能访问（gpt说的，实现方式没看懂）
@app.route('/second/<user_id>')
@login_required
def second(user_id):
    # 获取用户名
    username = users.get(user_id)
    # 渲染欢迎页面的模板，传入用户名和用户 id
    return render_template('welcome.HTML', username=username, user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)
