from sqlalchemy.orm import Session
import models, schemas

# Listar produtos
def get_produtos(db: Session):
    return db.query(models.Produto).all()

# Criar produto
def create_produto(db: Session, produto: schemas.ProdutoCreate):
    db_produto = models.Produto(nome=produto.nome, descricao=produto.descricao)
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

# Atualizar produto
def update_produto(db: Session, produto_id: int, produto: schemas.ProdutoCreate):
    db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not db_produto:
        return None
    db_produto.nome = produto.nome
    db_produto.descricao = produto.descricao
    db.commit()
    db.refresh(db_produto)
    return db_produto

# Deletar produto
def delete_produto(db: Session, produto_id: int):
    db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not db_produto:
        return None
    db.delete(db_produto)
    db.commit()
    return db_produto

# Listar todas as perguntas
def listar_perguntas(db: Session):
    return db.query(models.Pergunta).all()

# Listar perguntas não respondidas
def get_nao_respondidas(db: Session):
    return db.query(models.Pergunta).filter(models.Pergunta.respondida == False).all()

# Criar pergunta
def create_pergunta(db: Session, pergunta: schemas.PerguntaCreate):
    db_pergunta = models.Pergunta(pergunta=pergunta.pergunta)
    db.add(db_pergunta)
    db.commit()
    db.refresh(db_pergunta)
    return db_pergunta

# Responder pergunta
def responder(db: Session, pergunta_id: int, resposta: str):
    db_pergunta = db.query(models.Pergunta).filter(models.Pergunta.id == pergunta_id).first()
    if db_pergunta:
        db_pergunta.resposta = resposta
        db_pergunta.respondida = True
        db.commit()
        db.refresh(db_pergunta)
    return db_pergunta

# Corrigir pergunta
def corrigir_resposta(db: Session, pergunta_id: int, resposta: str):
    pergunta = db.query(models.Pergunta).filter(models.Pergunta.id == pergunta_id).first()
    if pergunta:
        pergunta.resposta = resposta
        pergunta.respondida = True
        db.commit()
        db.refresh(pergunta)
        return pergunta
    return None

# Deletar pergunta
def delete_pergunta(db: Session, pergunta_id: int):
    pergunta = db.query(models.Pergunta).filter(models.Pergunta.id == pergunta_id).first()
    if not pergunta:
        return None
    db.delete(pergunta)
    db.commit()
    return pergunta