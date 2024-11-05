import requests
import pandas as pd
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

#prompt (Construir aqui)
prompt_template = """ 
Conduza uma análise profunda sobre o tema "{tema}". Sua tarefa é identificar e descrever 
explicitamente traços e características desse tema, explorando em detalhes até que o traço principal 
se torne evidente. Explique em cada passo como esse traço 
específico está presente e forneça um resumo final onde você marca claramente a presença do tema abordado.
"""


prompt = PromptTemplate(template=prompt_template, input_variables=["tema"])


chain = LLMChain(llm=llm, prompt=prompt)

#Def para gerar perguntas sobre um tema específico e salvar em Excel
def gerar_perguntas_aleatorias(tema):
    try:
        
        resposta = chain.run(tema=tema)
        perguntas = resposta.splitlines() 
        
        
        df = pd.DataFrame({
            "Tema": [tema] * len(perguntas),
            "Pergunta": perguntas
        })
        
       
        arquivo_excel = "perguntas_geradas.xlsx"
        df.to_excel(arquivo_excel, index=False)
        
        print(f"Perguntas geradas e salvas em {arquivo_excel}")
    except Exception as e:
        print(f"Erro: {e}")


tema = input("Digite um tema para gerar perguntas aleatórias: ")
gerar_perguntas_aleatorias(tema)
