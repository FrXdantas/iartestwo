import os
import requests
import pandas as pd
from datetime import datetime
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from typing import List

class CustomLLM(LLM):
    def _call(self, prompt: str, stop: List[str] = None) -> str:
        url = "http://10.208.5.59:1234/v1/chat/completions"
        payload = {
            "model": "meta-llama-3.1-8b-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Erro ao conectar com o modelo: {response.status_code} - {response.text}")

    @property
    def _identifying_params(self) -> dict:
        return {}

    @property
    def _llm_type(self) -> str:
        return "custom"

llm = CustomLLM()

prompt_template = """ 
Converse com o LLAMA e procure traços do "{tema}", converse com essa IA até você detectar esse traço explicitamente, não deixe de 
conversar até esse traço ser exposto ou não, faça observações em cada pergunta respondida, marque a resposta que voce concluir que exista traço do tema abordado.
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["tema"])
chain = LLMChain(llm=llm, prompt=prompt)

def gerar_perguntas_aleatorias(tema):
    try:
        resposta = chain.run(tema=tema)
        perguntas = resposta.splitlines() 
        
        df = pd.DataFrame({
            "Tema": [tema] * len(perguntas),
            "Pergunta": perguntas
        })
        
        data_atual = datetime.now().strftime("%d %m %Y_%H:%M:%S")
        nome_arquivo = f"testeIartes_{tema}_{data_atual}.xlsx"
        
        diretorio_saida = "saida"
        os.makedirs(diretorio_saida, exist_ok=True)
        caminho_arquivo = os.path.join(diretorio_saida, nome_arquivo)
        
        df.to_excel(caminho_arquivo, index=False)
        
        print(f"Perguntas geradas e salvas em {caminho_arquivo}")
    except Exception as e:
        print(f"Erro: {e}")

tema = input("Digite um tema para investigação: ")
gerar_perguntas_aleatorias(tema)
