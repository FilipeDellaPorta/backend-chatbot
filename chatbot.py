import spacy
import unicodedata
from sqlalchemy.orm import Session
import models
import json
import string

# Carregar modelo de NLP em português
nlp = spacy.load("pt_core_news_sm") # nlp = spacy.load("pt_core_news_lg")

# Carrega manual de instruções
with open("manual.json", encoding="utf-8") as f:
    manual = json.load(f)

# Função de normalização (remove acentos, pontuação e deixa minúsculo)
def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Remove pontuação
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto

# Responder usando o manual (mais flexível, por palavra-chave)
def responder_manual(pergunta: str, db: Session) -> str:
    pergunta_norm = normalizar(pergunta)
    palavras_pergunta = set(pergunta_norm.split())

    for item in manual.values():
        palavras_chave = set(normalizar(" ".join(item["keywords"])).split())
        if palavras_chave.intersection(palavras_pergunta):
            # Se for resposta dinâmica
            if item.get("resposta_tipo") == "listar_produtos":
                produtos = db.query(models.Produto).all()
                nomes = [p.nome for p in produtos]
                return ", ".join(nomes)
            # Se for resposta fixa
            return item["resposta"]
    
    return None

# Função principal do chatbot
def responder_chatbot(pergunta: str, db: Session):
    pergunta_norm = normalizar(pergunta)
    doc = nlp(pergunta_norm)

    # 0. Tentar responder pelo manual primeiro
    resposta_manual = responder_manual(pergunta, db)
    if resposta_manual:
        return resposta_manual

    # 1. Verificar pergunta exata já respondida no banco
    resposta_existente = (
        db.query(models.Pergunta)
        .filter(models.Pergunta.pergunta.ilike(pergunta))
        .filter(models.Pergunta.respondida == True)
        .first()
    )
    if resposta_existente:
        return resposta_existente.resposta

    # 2. Procurar pergunta parecida usando NLP
    perguntas_respondidas = db.query(models.Pergunta).filter(models.Pergunta.respondida == True).all()
    melhor_resposta = None
    maior_score = 0.0

    for p in perguntas_respondidas:
        doc_salvo = nlp(normalizar(p.pergunta))
        score = doc.similarity(doc_salvo)
        if score > maior_score:
            maior_score = score
            melhor_resposta = p.resposta

    # 3. Se encontrou uma pergunta parecida o suficiente
    limiar = 0.70
    if maior_score >= limiar:
        return melhor_resposta

    # 4. Se não encontrou → retorna mensagem padrão
    return "Ainda não tenho uma resposta para isso, mas um atendente irá responder em breve."
