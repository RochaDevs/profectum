# API Pessoa x Pipefy

API em FastAPI que cria, deleta e movimenta cards de cadastro de Pessoa no Pipefy (GraphQL).

## Rodar
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # preencha PIPEFY_TOKEN
uvicorn main:app --reload
```
Swagger para demonstrar: http://localhost:8000/docs

## Endpoints
| Método | Rota | O que faz |
|---|---|---|
| POST | `/pessoas` | Cria o card. Recebe a cidade **pelo nome** e a API resolve o ID do registro. |
| DELETE | `/cards/{card_id}` | Deleta o card. Card inexistente devolve 404. |
| POST | `/cards/{card_id}/avancar` | Avança para a próxima fase; `?destino_fase_id=` move para uma fase específica. Na fase fim devolve `chegou_na_fase_fim: true`. |

Exemplo:
```bash
curl -X POST localhost:8000/pessoas -H "Content-Type: application/json" -d '{
  "nome": "Maria Teste", "cidade": "Fortaleza", "sexo": "Feminino",
  "hobbies": ["Leitura", "Música"], "cpf": "CPF_DE_TESTE", "telefone": "+55 85 99999-9999"
}'
```

## Decisões de design
- **Cidade por nome:** o campo `cidade` é um *connector* e só aceita ID de registro. A API busca na tabela (com paginação), ignora acento/caixa e prefere a grafia exata, pois a tabela tem duplicatas ("Fortaleza" e "fortaleza").
- **Valores fixos validados na entrada** (`sexo`, `hobbies`), espelhando as opções do formulário.
- **Variáveis GraphQL** em vez de interpolar strings, evitando injeção.
- **Token só em `.env`**, nunca no código.
- **Erros do Pipefy** viram respostas HTTP claras (404 para card inexistente, 409 se já está na fase fim, 502 para falhas do Pipefy).
