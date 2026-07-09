from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import urllib.parse

# Sua senha original com caractere especial
senha_original = "Fd@6190b"

# Transforma o '@' em '%40' para não quebrar a string de conexão
senha_codificada = urllib.parse.quote_plus(senha_original)

# Monta a URL injetando a senha mascarada com segurança
DATABASE_URL = f"postgresql+asyncpg://postgres:{senha_codificada}@127.0.0.1:5432/api_bancaria"

# Cria a engine de conexão assíncrona com o banco de dados
engine = create_async_engine(DATABASE_URL, echo=True)

# Cria o gerador de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Classe base para mapear as tabelas
Base = declarative_base()

# Função para abrir/fechar as conexões por requisição
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session