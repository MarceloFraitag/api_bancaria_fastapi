from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Conta(Base):
    __tablename__ = "contas"

    id = Column(Integer, primary_key=True, index=True)
    titular = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    saldo = Column(Float, default=0.0)

    # Relacionamento: uma conta pode ter várias transações
    transacoes = relationship("Transacao", back_populates="conta", cascade="all, delete-orphan")


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    conta_id = Column(Integer, ForeignKey("contas.id"), nullable=False)
    tipo = Column(String, nullable=False)  # "deposito" ou "saque"
    valor = Column(Float, nullable=False)
    data = Column(DateTime, default=datetime.utcnow)

    # Relacionamento: liga a transação de volta para a conta dona dela
    conta = relationship("Conta", back_populates="transacoes")