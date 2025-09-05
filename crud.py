from sqlalchemy.orm import Session
import models, schemas

# Produtos
def get_produtos(db: Session):
    return db.query(models.Produto).all()

def create_produto(db: Session, produto: schemas.ProdutoCreate):
    db_produto = models.Produto(nome=produto.nome, descricao=produto.descricao)
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

# Perguntas
def create_pergunta(db: Session, pergunta: schemas.PerguntaCreate):
    db_pergunta = models.Pergunta(pergunta=pergunta.pergunta)
    db.add(db_pergunta)
    db.commit()
    db.refresh(db_pergunta)
    return db_pergunta

def get_nao_respondidas(db: Session):
    return db.query(models.Pergunta).filter(models.Pergunta.respondida == False).all()

def responder_pergunta(db: Session, pergunta_id: int, resposta: str):
    db_pergunta = db.query(models.Pergunta).filter(models.Pergunta.id == pergunta_id).first()
    if db_pergunta:
        db_pergunta.resposta = resposta
        db_pergunta.respondida = True
        db.commit()
        db.refresh(db_pergunta)
    return db_pergunta