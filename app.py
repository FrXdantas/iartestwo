import os
from flask import Flask, request, render_template, send_from_directory
import pandas as pd
from datetime import datetime
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
import requests
from typing import List

app = Flask(__name__)

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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        tema = request.form["tema"]
        prompt_text = request.form["prompt_text"]

        prompt = PromptTemplate(template=prompt_text, input_variables=["tema"])
        chain = LLMChain(llm=llm, prompt=prompt)
        
        try:
            resposta = chain.run(tema=tema)
            perguntas = resposta.splitlines()

            df = pd.DataFrame({
                "Tema": [tema] * len(perguntas),
                "Pergunta": perguntas
            })

            data_atual = datetime.now().strftime("%d_%m_%Y_%H%M%S")
            nome_arquivo = f"testeIartes_{tema}_{data_atual}.xlsx"
            
            diretorio_saida = "saida"
            os.makedirs(diretorio_saida, exist_ok=True)
            caminho_arquivo = os.path.join(diretorio_saida, nome_arquivo)
            
            df.to_excel(caminho_arquivo, index=False)
            
            return render_template("index.html", download_link=nome_arquivo)
        
        except Exception as e:
            return f"Erro: {e}"

    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    diretorio_saida = "saida"
    return send_from_directory(directory=diretorio_saida, path=filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
