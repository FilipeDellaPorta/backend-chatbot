import spacy
from sqlalchemy.orm import Session
import models

# Carregar modelo de NLP em português
nlp = spacy.load("pt_core_news_sm")

def responder_chatbot(pergunta: str, db: Session):
    doc = nlp(pergunta.lower())

    # 1. Detectar se a pessoa está perguntando sobre produtos
    palavras_produto = {"produto", "produtos", "item", "itens", "catálogo", "loja"}
    if any(token.lemma_ in palavras_produto for token in doc):
        produtos = db.query(models.Produto).all()
        if produtos:
            nomes = ", ".join([p.nome for p in produtos])
            return f"Temos os seguintes produtos disponíveis: {nomes}."
        else:
            return "Ainda não temos produtos cadastrados."

    # 2. Detectar se a pessoa quer saber de preço
    palavras_preco = {"preço", "valor", "custa", "custar"}
    if any(token.lemma_ in palavras_preco for token in doc):
        return "Os preços variam conforme o produto. Qual produto você gostaria de saber?"

    # 3. Detectar se está perguntando sobre desconto
    palavras_desconto = {"desconto", "promoção", "oferta"}
    if any(token.lemma_ in palavras_desconto for token in doc):
        return "Temos descontos especiais para compras acima de 3 unidades."

    # 4. Se não entendeu → retorna None
    return None