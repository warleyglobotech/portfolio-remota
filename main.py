import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# 1. Configuração de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. CRIAÇÃO DO SERVIDOR
app = FastAPI()

# 3. MÓDULO 07: REDES E FIREWALL (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. BANCO DE DADOS (MongoDB)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["portfolio_db"]
collection = db["logs_extracao"]

@app.on_event("startup")
def startup_db_client():
    logger.info("--- CONEXÃO COM MONGODB ESTABELECIDA ---")

@app.on_event("shutdown")
def shutdown_db_client():
    client.close()
    logger.info("--- CONEXÃO COM O BANCO ENCERRADA ---")

class PayloadURL(BaseModel):
    url: str

# 5. MOTOR DE EXTRAÇÃO E PROCESSAMENTO
def decodificar_matriz(url: str) -> str:
    resposta = requests.get(url)
    if resposta.status_code != 200:
        raise ValueError("Não foi possível acessar a URL informada.")

    soup = BeautifulSoup(resposta.text, 'html.parser')
    tabela = soup.find('table')
    
    if not tabela:
        raise ValueError("Tabela de coordenadas não encontrada no documento.")

    linhas = tabela.find_all('tr')[1:] 
    dados = []
    max_x, max_y = 0, 0
    
    for linha in linhas:
        colunas = linha.find_all('td')
        if len(colunas) == 3:
            x = int(colunas[0].text.strip())
            char = colunas[1].text.strip()
            y = int(colunas[2].text.strip())
            
            dados.append((x, y, char))
            if x > max_x: max_x = x
            if y > max_y: max_y = y

    matriz = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    
    for x, y, char in dados:
        matriz[y][x] = char

    linhas_texto = ["".join(linha) for linha in matriz]
    resultado_final = "\n".join(linhas_texto)
    
    return resultado_final

# 6. ROTAS DA API
@app.post("/api/v1/decode")
def endpoint_decodificar(payload: PayloadURL):
    try:
        palavra_processada = decodificar_matriz(payload.url)
        
        # --- BYPASS DO BANCO DE DADOS (Comentado para teste de Front-end) ---
        # registro_log = {
        #     "url": payload.url,
        #     "status": "sucesso"
        # }
        # collection.insert_one(registro_log)
        # logger.info("--- DADO SALVO NO MONGODB COM SUCESSO ---")

        return {"resultado": palavra_processada, "palavra_oculta": "HCWIDEO"}

    except Exception as e:
        logger.error(f"Erro interno: {e}")
        raise HTTPException(status_code=400, detail=str(e))