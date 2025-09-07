import spacy
import unicodedata
from sqlalchemy.orm import Session
import models

# Carregar modelo de NLP em português
nlp = spacy.load("pt_core_news_sm")

# Função de normalização (remove acentos e pontuação, deixa minúsculo)
def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

def responder_chatbot(pergunta: str, db: Session):
    pergunta_norm = normalizar(pergunta)
    doc = nlp(pergunta_norm)

    # 1. Verificar pergunta exata já respondida
    resposta_existente = (
        db.query(models.Pergunta)
        .filter(models.Pergunta.pergunta.ilike(pergunta))
        .filter(models.Pergunta.respondida == True)
        .first()
    )
    if resposta_existente:
        print(f"[DEBUG] Pergunta exata encontrada: {resposta_existente.pergunta}")
        return resposta_existente.resposta

    # 2. Procurar pergunta parecida usando NLP
    perguntas_respondidas = db.query(models.Pergunta).filter(models.Pergunta.respondida == True).all()
    melhor_resposta = None
    maior_score = 0.0

    for p in perguntas_respondidas:
        doc_salvo = nlp(normalizar(p.pergunta))
        score = doc.similarity(doc_salvo)  # similaridade semântica
        print(f"[DEBUG] Comparando com '{p.pergunta}' → Score: {score:.2f}")

        if score > maior_score:
            maior_score = score
            melhor_resposta = p.resposta

    # 3. Se encontrou uma pergunta parecida o suficiente
    limiar = 0.70  # threshold ajustável
    if maior_score >= limiar:
        print(f"[DEBUG] Melhor correspondência encontrada (score={maior_score:.2f})")
        return melhor_resposta
    else:
        print(f"[DEBUG] Nenhuma correspondência forte (score máximo={maior_score:.2f})")

    # 4. Se não encontrou nada → salvar como nova pergunta
    nova_pergunta = models.Pergunta(pergunta=pergunta, respondida=False)
    db.add(nova_pergunta)
    db.commit()
    db.refresh(nova_pergunta)
    print(f"[DEBUG] Nova pergunta salva no banco: '{pergunta}'")

    return "Ainda não tenho uma resposta para isso, mas um atendente irá responder em breve."
