from sqlalchemy.orm import Relationship
from flask_login import UserMixin
from db import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(20), nullable=False, unique=True)
    senha = db.Column(db.String(), nullable=False)
    
    def __repr__(self):
        return f"<{self.nome}>"
    
class Tarefa(db.Model):
    __tablename__ = 'tarefas'

    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.String(350))
    status = db.Column(db.Integer, default=0)
    
    @property
    def status_str(self):
        match self.status:
            case 0:
                return 'Incompleto'
            case 1:
                return 'Em Andamento'
            case 2:
                return 'Completo'
            case _:
                return '?'
    
    usuario_id = db.Column(db.Integer,  db.ForeignKey('usuarios.id'))
    usuario = Relationship('Usuario', backref='tarefas', lazy='subquery')
