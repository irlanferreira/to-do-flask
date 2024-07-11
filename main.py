from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, LoginManager, current_user
from models import Usuario, Tarefa
from db import db
import hashlib

app = Flask(__name__)
app.secret_key = 'tijolo'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.db"
db.init_app(app)
lm = LoginManager(app)
lm.login_view = 'login'

def hash(txt):
    hash_obj = hashlib.sha256()
    hash_obj.update(txt.encode('utf-8'))
    return hash_obj.hexdigest()

@lm.user_loader
def user_lodaer(id):
    user = db.session.query(Usuario).filter_by(id=id).first()
    return user

@app.route('/')
@login_required
def home():
    return render_template('home.html', usuario=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        senha_hash = hash(senha)
        
        usuario = db.session.query(Usuario).filter_by(nome=nome, senha=senha_hash).first()
        if not usuario:
            flash('Usuário ou senha incorretos.')
            return redirect(url_for('login'))
        login_user(usuario)
        return redirect(url_for('home'))

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == "GET":
        return render_template('cadastrar-tarefa.html')
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        
        usuario = Usuario(nome=nome, senha=hash(senha))
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario)
        return redirect(url_for('home'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/status/<int:id>')
def status(id):
    tarefa = db.session.query(Tarefa).filter_by(id=id).first()
    if current_user != tarefa.usuario:
        flash('Você não tem permissão para editar essa tarefa.')
        return redirect(url_for('home'))
    match tarefa.status:
        case 0:
            tarefa.status = 1
        case 1:
            tarefa.status = 2
        case 2:
            tarefa.status = 0
        case _:
            tarefa.status = tarefa.status
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/adicionar-tarefa', methods=['GET', 'POST'])
def adicionar_tarefa():
    if request.method == "GET":
        return render_template('adicionar-tarefa.html')
    elif request.method == "POST":
        nome = request.form['nomeForm']
        desc = request.form['descForm']

        tarefa = Tarefa(nome=nome, descricao=desc, usuario_id=current_user.id)
        db.session.add(tarefa)
        db.session.commit()
        return redirect(url_for('home'))

@app.route('/editar-tarefa/<int:id>', methods=['GET', 'POST'])
def editar_tarefa(id):
    tarefa = db.session.query(Tarefa).filter_by(id=id).first()
    if tarefa.usuario != current_user:
        flash('Você não tem permissão para editar essa tarefa.')
        return redirect(url_for('home'))
    if request.method == "GET":
        return render_template('editar-tarefa.html', tarefa=tarefa)
    elif request.method == "POST":
        nome = request.form['nomeForm']
        desc = request.form['descForm']

        tarefa.nome = nome
        tarefa.descricao = desc
        db.session.commit()
        return redirect(url_for('home'))

@app.route('/deletar/<int:id>')
def deletar(id):
    tarefa = db.session.query(Tarefa).filter_by(id=id).first()
    if tarefa.usuario != current_user:
        flash('Você não tem permissão para deletar essa tarefa.')
        return redirect(url_for('home'))
    db.session.delete(tarefa)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)