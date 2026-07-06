import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from contextlib import asynccontextmanager

# Configuração de Log
logging.basicConfig(level=logging.INFO)

# =====================================================================
# IMPORTANTE: Substitua 'SEU_CLUSTER' pelo código do seu MongoDB Atlas
# =====================================================================
MONGO_URI = "mongodb+srv://warley:Lms2026@cluster0.hiuixgb.mongodb.net/portfolio_db?retryWrites=true&w=majority"

# Variáveis globais para o banco de dados
client = None
db = None
colecao = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Inicialização: Conecta ao banco de dados ---
    global client, db, colecao
    try:
        client = MongoClient(MONGO_URI)
        db = client["portfolio_db"]
        colecao = db["extracao"]
        logging.info("--- CONEXÃO COM MONGODB ESTABELECIDA ---")
    except Exception as e:
        logging.error(f"--- ERRO AO CONECTAR AO BANCO: {e} ---")
    
    yield # A aplicação FastAPI permanece em execução aqui
    
    # --- Encerramento: Fecha a conexão ---
    if client:
        client.close()
        logging.info("--- CONEXÃO COM O BANCO ENCERRADA ---")

# Inicializa o FastAPI utilizando o ciclo de vida (lifespan) correto
app = FastAPI(lifespan=lifespan)

# Modelo de Dados para a Requisição
class URLRequest(BaseModel):
    url: str

@app.post("/api/v1/decode")
async def decode_url(request: URLRequest):
    try:
        # 1. Realiza a requisição para a página do documento
        response = requests.get(str(request.url))
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. Extração das coordenadas da tabela
        linhas = soup.find_all('tr')
        coordenadas = []
        max_x = 0
        max_y = 0

        # Ignora a primeira linha (cabeçalho da tabela)
        for linha in linhas[1:]:
            colunas = linha.find_all('td')
            if len(colunas) == 3:
                x = int(colunas[0].get_text(strip=True))
                caractere = colunas[1].get_text(strip=True)
                y = int(colunas[2].get_text(strip=True))
                coordenadas.append((x, y, caractere))
                if x > max_x: max_x = x
                if y > max_y: max_y = y

        # 3. Construção da matriz do desenho
        grade = [[" " for _ in range(max_x + 1)] for _ in range(max_y + 1)]
        for x, y, caractere in coordenadas:
            grade[y][x] = caractere

        resultado_final = "\n".join(["".join(linha) for linha in grade])
        
        # 4. Gravação dos dados extraídos no MongoDB
        try:
            if colecao is not None:
                colecao.insert_one({"url": str(request.url), "resultado_decodificado": resultado_final})
                logging.info("--- DADO SALVO NO MONGODB COM SUCESSO ---")
            else:
                logging.warning("--- COLEÇÃO NÃO INICIALIZADA. DADO NÃO SALVO ---")
        except Exception as e:
            logging.error(f"--- ERRO AO SALVAR NO BANCO: {e} ---")
            
        return {"status": "sucesso", "resultado": resultado_final}
        
    except Exception as e:
        logging.error(f"--- ERRO DURANTE A EXTRAÇÃO DOS DADOS: {e} ---")
        raise HTTPException(status_code=500, detail=str(e))