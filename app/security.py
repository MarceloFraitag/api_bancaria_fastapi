from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuração do algoritmo de criptografia para as senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações do JWT (Em produção, isso ficaria em variáveis de ambiente)
SECRET_KEY = "uma_chave_secreta_muito_segura_e_longa_para_o_desafio"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- FUNÇÕES PARA CRIPTOGRAFIA DE SENHA ---

def gerar_senha_hash(senha: str) -> str:
    """Transforma a senha limpa em um hash seguro para salvar no banco."""
    return pwd_context.hash(senha)

def verificar_senha(senha_limpa: str, senha_hash: str) -> bool:
    """Compara a senha que o usuário digitou no login com o hash do banco."""
    return pwd_context.verify(senha_limpa, senha_hash)


# --- FUNÇÕES PARA O TOKEN JWT ---

def criar_token_acesso(dados: dict, tempo_expiracao: Optional[timedelta] = None) -> str:
    """Gera o token JWT que o usuário usará para acessar as rotas privadas."""
    dados_para_codificar = dados.copy()
    
    if tempo_expiracao:
        expire = datetime.utcnow() + tempo_expiracao
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    dados_para_codificar.update({"exp": expire})
    token_jwt = jwt.encode(dados_para_codificar, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt