from fastapi import FastAPI
import requests
import xml.etree.ElementTree as ET
from enum import Enum

class BancoDados(str, Enum):
    taxonomia = "taxonomy"
    artigos = "pubmed"
    genes = "gene"
    proteinas = "protein"

def buscar_virus(termo: str, bd:str, limite:int):
    
    url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params_search = {
        "db": bd,
        "term": termo,
        "retmode": "json",
        "usehistory": "y"  
    }
    resposta_search = requests.get(url_search, params=params_search)
    resultado = resposta_search.json()["esearchresult"]

    ids = resultado["idlist"]   
    ids = ids[:limite] 
    query_key = resultado["querykey"] 

    print("IDs encontrados:", ids)

    if not ids:
        print("Nenhum resultado encontrado.")
        return
    informacoes = []
    
    for id in ids:
        
        url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params_fetch = {
        "db": bd,
        "query_key": query_key,
        "id": id,
        "retmode": "xml"
     }
           
        resposta_fetch = requests.get(url_fetch, params=params_fetch)

        if bd == "taxonomy":
            root = ET.fromstring(resposta_fetch.text)
            taxon = root.find("Taxon")
            informacoes_do_virus = {
           "nome_cientifico": taxon.findtext("ScientificName"),
           "rank": taxon.findtext("Rank"),
        "linhagem": taxon.findtext("Lineage"),
    }
        elif bd == "protein" :
             root = ET.fromstring(resposta_fetch.text)
             GBSEQ= root.find("GBSeq")
             informacoes_do_virus = {
        "organismo": GBSEQ.findtext("GBSeq_organism"),
        "definicao": GBSEQ.findtext("GBSeq_definition"),
        "taxonomia": GBSEQ.findtext("GBSeq_taxonomy"),
    }
        elif bd == "gene":
          root = ET.fromstring(resposta_fetch.text)
          gene = root.find("Entrezgene")
          informacoes_do_virus = {
         "locus": gene.find("Entrezgene_gene/Gene-ref/Gene-ref_locus").text,
         "definicao": gene.find("Entrezgene_gene/Gene-ref/Gene-ref_desc").text,
         "organismo": gene.find("Entrezgene_source/BioSource/BioSource_org/Org-ref/Org-ref_taxname").text,
    }
        elif bd == "pubmed":
          root = ET.fromstring(resposta_fetch.text)
          pubmed = root.find("PubmedArticle")  
          informacoes_do_virus = {
            "titulo":  pubmed.find("MedlineCitation/Article/ArticleTitle").text,
            "journal": pubmed.find("MedlineCitation/Article/Journal/Title").text,
            "resumo":  pubmed.find("MedlineCitation/Article/Abstract/AbstractText").text,
        } 
        
        else:
          informacoes_do_virus = {"resultado": resposta_fetch.text}

        informacoes.append(informacoes_do_virus)
    return  informacoes
  


app = FastAPI()

@app.get("/")
def hello():
    return {"mensagem": "olá, pesquise o vírus e receba suas informções"}

@app.get("/virus/{nome}")
def rota_buscar_virus(nome: str):
    return buscar_virus(nome,"taxonomy",5)

@app.get("/busca")
def rota_buscar(q: str, db: BancoDados, limite: int = 5):
    return buscar_virus(q, db, limite)
