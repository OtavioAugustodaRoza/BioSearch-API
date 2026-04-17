from fastapi import FastAPI
import xml.etree.ElementTree as ET
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import httpx
import asyncio


load_dotenv()
API_KEY = os.getenv("NCBI_API_KEY")



class BancoDados(str, Enum):
    taxonomia = "taxonomy"
    artigos = "pubmed"
    genes = "gene"
    proteinas = "protein"
    
    
async def buscar_item(id:str , bd: str, client: httpx.AsyncClient):
    url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params_fetch = {
        "db": bd,
        "id": id,
        "retmode": "xml",
        "api_key": API_KEY
    }  
    resposta = await client.get(url_fetch, params=params_fetch, headers={"Accept-Encoding": "identity"})
    return resposta

async def buscar_virus(termo: str, bd:str, limite:int):
    async with httpx.AsyncClient() as cliente:
        
       url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
       params_search = {
        "db": bd,
        "term": termo,
        "retmode": "json",
        "usehistory": "y"  
      }
       resposta_search = await cliente.get(url_search, params=params_search)
       resultado = resposta_search.json()["esearchresult"]

       ids = resultado["idlist"]   
       ids = ids[:limite] 

       print("IDs encontrados:", ids)

       if not ids:
         print("Nenhum resultado encontrado.")
         return
    
       tarefas = [buscar_item(id, bd, cliente) for id in ids]
       respostas= await asyncio.gather(*tarefas)
       informacoes = [parsear(resposta, bd) for resposta in respostas]
       
        
    return  informacoes

def parsear(resposta,bd):
       if resposta.status_code == 429:
        return {"erro": "limite de requisições atingido"}
    
       if bd == "taxonomy":
         root = ET.fromstring(resposta.text)
         taxon = root.find("Taxon")
         return {
            "nome_cientifico": taxon.findtext("ScientificName"),
            "rank": taxon.findtext("Rank"),
            "linhagem": taxon.findtext("Lineage"),
        }
       elif bd == "protein":
          root = ET.fromstring(resposta.text)
          GBSEQ = root.find("GBSeq")
          return {
            "organismo": GBSEQ.findtext("GBSeq_organism"),
            "definicao": GBSEQ.findtext("GBSeq_definition"),
            "taxonomia": GBSEQ.findtext("GBSeq_taxonomy"),
        }
       elif bd == "gene":
            root = ET.fromstring(resposta.text)
            gene = root.find("Entrezgene")
            return {
            "locus": gene.find("Entrezgene_gene/Gene-ref/Gene-ref_locus").text,
            "definicao": gene.find("Entrezgene_gene/Gene-ref/Gene-ref_desc").text,
            "organismo": gene.find("Entrezgene_source/BioSource/BioSource_org/Org-ref/Org-ref_taxname").text,
            }
       elif bd == "pubmed":
        root = ET.fromstring(resposta.text)
        pubmed = root.find("PubmedArticle")
        return {
            "titulo": pubmed.find("MedlineCitation/Article/ArticleTitle").text,
            "journal": pubmed.find("MedlineCitation/Article/Journal/Title").text,
            "resumo": pubmed.find("MedlineCitation/Article/Abstract/AbstractText").text,
        }
       else:
         return {"resultado": resposta.text}


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bio-search-front.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hello():
    return {"mensagem": "olá, pesquise o vírus e receba suas informações"}

@app.get("/virus/{nome}")
async def rota_buscar_virus(nome: str):
    return await buscar_virus(nome,"taxonomy",5)

@app.get("/busca")
async def rota_buscar(q: str, db: BancoDados, limite: int = 5):
    return await buscar_virus(q, db, limite)
