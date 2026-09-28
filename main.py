import os
from typing import Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

URL = "https://api.pipefy.com/graphql"
HEADERS = {"Authorization": f"Bearer {os.environ['PIPEFY_TOKEN']}"}
PIPE_ID = 303843596

app = FastAPI()


def graphql(query, variaveis):

    resposta = requests.post(
        URL, 
        json={
            "query": query, 
            "variables": variaveis
        }, 
        headers=HEADERS, 
        timeout=30
    ).json()

    if "errors" in resposta or "error" in resposta:
        raise HTTPException(status_code=502, detail=resposta)
    
    return resposta["data"]


# Parametros da classe foram nomeados conforme os ids dos campos, exceto pelo 'cidade_id'
class Pessoa(BaseModel):
    nome: str
    cidade_id: str  # ID do registro na tabela "Cidade" (ex.: Fortaleza = 850256930)
    data_de_nascimento: Optional[str] = None  # AAAA-MM-DD
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    sexo: Optional[str] = None  # Masculino | Feminino | Prefere não responder
    hobbies: list[str] = []


@app.post("/cards")
def criar_card(pessoa: Pessoa):

    dados = pessoa.model_dump()

    id_cidade = dados.pop("cidade_id")

    campos = [
        {
            "field_id": "cidade", 
            "field_value": [id_cidade]
        },
    ]

    for campo, valor in dados.items():
        if valor:
            campos.append({"field_id": campo, "field_value": valor})

    query = \
    """
        mutation($input: CreateCardInput!) {
        createCard(input: $input) { card { id title current_phase { id name } } }
        }

    """
    data = graphql(
        query, 
        {
            "input": {
                "pipe_id": PIPE_ID, 
                "fields_attributes": campos
            }
        }
    )

    return data["createCard"]["card"]


@app.patch("/cards/{card_id}/fase")
def mudar_fase(card_id: str, fase_id: str):

    query = \
    """
        mutation($input: MoveCardToPhaseInput!) {
        moveCardToPhase(input: $input) { card { id current_phase { id name done } } }
    }
    """

    data = graphql(query, {"input": {"card_id": card_id, "destination_phase_id": fase_id}})

    fase = data["moveCardToPhase"]["card"]["current_phase"]

    return {"card_id": card_id, "fase_atual": fase["name"], "chegou_na_fase_fim": fase["done"]}


@app.delete("/cards/{card_id}")
def deletar_card(card_id: str):

    query = """
    mutation($input: DeleteCardInput!) {
      deleteCard(input: $input) { success }
    }
    """

    data = graphql(query, {"input": {"id": card_id}})

    return {"card_id": card_id, "deletado": data["deleteCard"]["success"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)