import urllib.request
import urllib.error
import json

# URL do seu servidor FastAPI
url_api = "http://127.0.0.1:8000/api/v1/decode"

# URL do Google Docs que será processada
payload = {
    "url": "https://docs.google.com/document/d/e/2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub"
}

# Configuração da requisição
req = urllib.request.Request(
    url_api, 
    data=json.dumps(payload).encode('utf-8'), 
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as resposta:
        # Lê a resposta da API
        conteudo = resposta.read().decode('utf-8')
        
        # Converte a string JSON para um dicionário Python
        dados = json.loads(conteudo)
        
        # Exibe o status e o desenho decodificado
        print(f"Status Code: {resposta.getcode()}")
        print("\n--- DESENHO DECODIFICADO ---\n")
        print(dados['resultado'])
        
except urllib.error.HTTPError as e:
    erro_api = e.read().decode('utf-8')
    print(f"❌ O Servidor respondeu com erro detalhado: {erro_api}")
except Exception as e:
    print(f"Erro na requisição: {e}")