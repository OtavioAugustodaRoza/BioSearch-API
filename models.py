from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,JSON
from database import Base

class Usuarios(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer,primary_key=True)
    senha = Column(String)
    email = Column(String, unique=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    
class Colecoes(Base):
    __tablename__ = "colecoes"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    usuario_id = Column(Integer,ForeignKey("usuarios.id"))
    
    
class Favoritos(Base):
    __tablename__ = "favoritos"
    
    id = Column(Integer, primary_key=True, index=True)
    colecao_id = Column(Integer, ForeignKey("colecoes.id"))
    dados = Column(JSON)
    criado_em = Column(DateTime, default=datetime.utcnow)
