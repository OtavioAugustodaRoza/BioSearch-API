# BioSearch API

API desenvolvida em Python com FastAPI que realiza consultas na base de dados pública do NCBI.
Permite buscar informações nos bancos: taxonomy, pubmed, gene e protein.

## Tecnologias
- Python
- FastAPI
- Requests


## Como rodar o projeto

1. Clonar o repositório
```
git clone https://github.com/OtavioAugustodaRoza/BioSearch-API.git
```

2. Entrar na pasta
```
cd fastApi
```

3. Criar e ativar a venv
```
python -m venv venv
venv\Scripts\activate
```

4. Instalar as dependências
```
pip install -r requirements.txt
```

5. Rodar o servidor
```
uvicorn main:app --reload
```
