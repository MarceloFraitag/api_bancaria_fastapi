import time
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from jose import JWTError, jwt

from app.database import engine, Base, get_db
from app.models import Conta, Transacao
from app.schemas import ContaCreate, ContaResponse, TransacaoCreate, TransacaoResponse, ExtratoResponse
from app.security import gerar_senha_hash, verificar_senha, criar_token_acesso, SECRET_KEY, ALGORITHM

app = FastAPI(
    title="API Bancária Assíncrona Premium",
    description="Desafio de API RESTful com Logs, Paginação e Filtros avançados.",
    version="1.1.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- 1. MIDDLEWARE DE LOGS E AUDITORIA ---
@app.middleware("http")
async def log_auditoria(request: Request, call_next):
    inicio = time.time()
    response = await call_next(request)
    tempo_execucao = (time.time() - inicio) * 1000 # Converte para milissegundos
    
    # Log elegante impresso direto no seu terminal do VS Code
    print(f" LOG BANCÁRIO | {request.method} {request.url.path} | Status: {response.status_code} | Tempo: {tempo_execucao:.2f}ms")
    return response


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --- FUNÇÃO AUXILIAR PARA PEGAR O USUÁRIO LOGADO ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Conta:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(Conta).where(Conta.email == email))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user


# --- ROTAS DA API ---

@app.post("/cadastro", response_model=ContaResponse, status_code=status.HTTP_201_CREATED, tags=["Autenticação"])
async def cadastrar_conta(conta: ContaCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conta).where(Conta.email == conta.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    
    nova_conta = Conta(
        titular=conta.titular,
        email=conta.email,
        senha_hash=gerar_senha_hash(conta.senha),
        saldo=0.0
    )
    db.add(nova_conta)
    await db.commit()
    await db.refresh(nova_conta)
    return nova_conta


@app.post("/login", tags=["Autenticação"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conta).where(Conta.email == form_data.username))
    conta = result.scalars().first()
    
    if not conta or not verificar_senha(form_data.password, conta.senha_hash):
        raise HTTPException(status_code=400, detail="E-mail ou senha incorretos.")
    
    access_token = criar_token_acesso(dados={"sub": conta.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/transacoes", response_model=TransacaoResponse, status_code=status.HTTP_201_CREATED, tags=["Operações Bancárias"])
async def criar_transacao(transacao: TransacaoCreate, current_user: Conta = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if transacao.tipo not in ["deposito", "saque"]:
        raise HTTPException(status_code=400, detail="Tipo de transação inválido. Use 'deposito' ou 'saque'.")
    
    if transacao.tipo == "saque":
        if current_user.saldo < transacao.valor:
            raise HTTPException(status_code=400, detail="Saldo insuficiente para realizar o saque.")
        current_user.saldo -= transacao.valor
    else:
        current_user.saldo += transacao.valor

    nova_transacao = Transacao(
        conta_id=current_user.id,
        tipo=transacao.tipo,
        valor=transacao.valor
    )
    
    db.add(nova_transacao)
    await db.commit()
    await db.refresh(nova_transacao)
    return nova_transacao


# --- 2 e 3. ROTA DE EXTRATO COM PAGINAÇÃO E FILTROS ---
@app.get("/extrato", response_model=ExtratoResponse, tags=["Operações Bancárias"])
async def ver_extrato(
    tipo: str = None, 
    limite: int = 10, 
    offset: int = 0, 
    current_user: Conta = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Exibe o extrato com filtros por tipo ('deposito'/'saque') e paginação dos resultados."""
    # Monta a query base buscando transações daquele usuário específico
    query = select(Transacao).where(Transacao.conta_id == current_user.id)
    
    # Aplica o filtro de tipo se o usuário passar na URL (Ex: /extrato?tipo=saque)
    if tipo:
        if tipo not in ["deposito", "saque"]:
            raise HTTPException(status_code=400, detail="Filtro de 'tipo' deve ser 'deposito' ou 'saque'.")
        query = query.where(Transacao.tipo == tipo)
    
    # Aplica a ordenação por data decrescente, limite por página e o pulo (offset)
    query = query.order_by(Transacao.data.desc()).limit(limite).offset(offset)
    
    result = await db.execute(query)
    historico = result.scalars().all()
    
    return {
        "saldo_atual": current_user.saldo,
        "transacoes": historico
    }