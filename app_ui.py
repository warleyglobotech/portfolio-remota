import streamlit as st
import requests

# Configuração da página
st.set_page_config(page_title="Decodificador de Matriz", page_icon="🕵️‍♂️", layout="centered")

st.title("Decodificador de Dados Remotos")
st.write("Insira a URL da tabela para extrair e visualizar a matriz oculta.")

# Campo de texto para a URL
url_input = st.text_input("URL do Documento:")

# Botão de ação
if st.button("Decodificar"):
    if url_input:
        with st.spinner("Conectando ao motor de extração..."):
            try:
                # Envia a URL para o seu backend (FastAPI)
                response = requests.post("https://portfolio-remota.onrender.com/api/v1/decode", json={"url": url_input})
                
                if response.status_code == 200:
                    dados = response.json()
                    st.success("Extração e decodificação concluídas com sucesso!")
                    
                    st.subheader("Resultado Visual:")
                    # st.text preserva os espaços em branco para a "arte" não quebrar
                    st.text(dados["resultado"])
                else:
                    st.error(f"Erro no motor de extração. Código: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Erro de conexão: O motor backend (uvicorn) parece estar desligado.")
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
    else:
        st.warning("Por favor, cole uma URL válida antes de decodificar.")
        