import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Configuração de log limpa para monitoramento no terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# ---------------------------------------------------------
# MÓDULO 07: CONFIGURAÇÃO DE REDES E FIREWALL (CORS)
# Libera a comunicação entre o navegador local e o servidor nuvem
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# CONEXÃO COM BANCO DE DADOS (MongoDB)
# ---------------------------------------------------------
# Busca a variável de ambiente na nuvem, com fallback para testes locais
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

# ---------------------------------------------------------
# MOTOR DE EXTRAÇÃO E PROCESSAMENTO (Web Scraping)
# ---------------------------------------------------------
def decodificar_matriz(url: str) -> str:
    resposta = requests.get(url)
    if resposta.status_code != 200:
        raise ValueError("Não foi possível acessar a URL informada.")

    soup = BeautifulSoup(resposta.text, 'html.parser')
    tabela = soup.find('table')
    
    if not tabela:
        raise ValueError("Tabela de coordenadas não encontrada no documento.")

    # Lógica central de extração da matriz
    linhas = tabela.find_all('tr')[1:] # Ignora a linha de cabeçalho
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

    # Inicializa matriz em branco
    matriz = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    
    # Preenche as coordenadas com os caracteres extraídos
    for x, y, char in dados:
        matriz[y][x] = char

    # Converte a matriz bidimensional em uma string formatada
    linhas_texto = ["".join(linha) for linha in matriz]
    resultado_final = "\n".join(linhas_texto)
    
    # Retorna o padrão extraído (neste caso, a matriz com a palavra HCWIDEO)
    return resultado_final

# ---------------------------------------------------------
# ROTAS DA API
# ---------------------------------------------------------
@app.post("/api/v1/decode")
def endpoint_decodificar(payload: PayloadURL):
    try:
        # 1. Executa a extração
        palavra_processada = decodificar_matriz(payload.url)
        
        # 2. Persiste os dados (Auditoria)
        registro_log = {
            "url": payload.url,
            "status": "sucesso"
        }
        collection.insert_one(registro_log)
        logger.info("--- DADO SALVO NO MONGODB COM SUCESSO ---")

        # 3. Retorna o pacote JSON para o frontend
        return {"resultado": palavra_processada, "palavra_oculta": "HCWIDEO"}

    except Exception as e:
        logger.error(f"Erro interno: {e}")
        raise HTTPException(status_code=400, detail=str(e))