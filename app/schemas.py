from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

# --- SCHEMAS DE AUTENTICAÇÃO E USUÁRIO ---

# Dados que o usuário envia para criar uma conta
class ContaCreate(BaseModel):
    titular: str = Field(..., min_length=3, description="Nome do titular da conta")
    email: str = Field(..., description="E-mail único para login")
    senha: str = Field(..., min_length=6, description="Senha de acesso (mínimo 6 caracteres)")

# Dados que a API devolve ao consultar uma conta (Sem expor a senha!)
class ContaResponse(BaseModel):
    id: int
    titular: str
    email: str
    saldo: float

    class Config:
        from_attributes = True


# --- SCHEMAS DE TRANSAÇÃO ---

# Dados recebidos ao realizar um depósito ou saque (Validação de valor negativo entra aqui!)
class TransacaoCreate(BaseModel):
    tipo: str = Field(..., description="Tipo da transação: 'deposito' ou 'saque'")
    valor: float = Field(..., gt=0, description="O valor deve ser estritamente maior que zero")

# Dados retornados ao listar as transações (Extrato)
class TransacaoResponse(BaseModel):
    id: int
    conta_id: int
    tipo: str
    valor: float
    data: datetime

    class Config:
        from_attributes = True


# --- SCHEMA DO EXTRATO COMPLETO ---
class ExtratoResponse(BaseModel):
    saldo_atual: float
    transacoes: List[TransacaoResponse]