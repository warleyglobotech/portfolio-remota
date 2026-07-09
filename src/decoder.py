import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Tuple, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SecretGridDecoder:
    def __init__(self, target_url: str):
        self.__url = target_url
        self.__grid: Dict[Tuple[int, int], str] = {}
        self.__max_x = 0
        self.__max_y = 0

    def __fetch_and_parse(self) -> None:
        try:
            response = requests.get(self.__url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            linhas = soup.find_all('tr')[1:]
            
            for linha in linhas:
                colunas = linha.find_all('td')
                if len(colunas) < 3:
                    continue
                    
                x = int(colunas[0].get_text(strip=True))
                caractere = colunas[1].get_text(strip=True)
                y = int(colunas[2].get_text(strip=True))
                
                self.__grid[(x, y)] = caractere
                self.__max_x = max(self.__max_x, x)
                self.__max_y = max(self.__max_y, y)
                
        except Exception as e:
            logging.error(f"Erro no parse: {e}")
            raise ValueError(f"Falha ao processar os dados: {str(e)}")

    def get_grid_data(self) -> List[str]:
        if not self.__grid:
            self.__fetch_and_parse()
            
        resultado = []
        for y in range(self.__max_y, -1, -1):
            linha = "".join([self.__grid.get((x, y), ' ') for x in range(self.__max_x + 1)])
            resultado.append(linha)
            
        return resultado