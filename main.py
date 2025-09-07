from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud, chatbot
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

# Criar as tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Loja Virtual API")

# Usuário e senha fixos (apenas para teste)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-chatbot-hazel.vercel.app", "http://localhost:5173"],  # permite qualquer origem (ou só ["http://localhost:5173"])
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependência para injetar sessão no banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rotas

# Listar produtos
@app.get("/produtos", response_model=list[schemas.Produto])
def listar_produtos(db: Session = Depends(get_db)):
    return crud.get_produtos(db)

# Criar produto
@app.post("/produto", response_model=schemas.Produto)
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    return crud.create_produto(db, produto)

# Atualizar produto
@app.put("/produto/{produto_id}", response_model=schemas.Produto)
def atualizar_produto(produto_id: int, produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    result = crud.update_produto(db, produto_id, produto)
    if not result:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return result

# Deletar produto
@app.delete("/produto/{produto_id}")
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    result = crud.delete_produto(db, produto_id)
    if not result:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"message": "Produto deletado com sucesso"}

# Listar todas as perguntas
@app.get("/perguntas", response_model=list[schemas.Pergunta])
def listar_perguntas(db: Session = Depends(get_db)):
    return crud.listar_perguntas(db)

# Listar perguntas não respondidas
@app.get("/nao-respondidas", response_model=list[schemas.Pergunta])
def listar_nao_respondidas(db: Session = Depends(get_db)):
    return crud.get_nao_respondidas(db)

# Criar pergunta
@app.post("/pergunta", response_model=schemas.Pergunta)
def criar_pergunta(pergunta: schemas.PerguntaCreate, db: Session = Depends(get_db)):
    # Verifica se a pergunta já existe
    db_pergunta = db.query(models.Pergunta).filter(models.Pergunta.pergunta == pergunta.pergunta).first()
    if db_pergunta:
        return db_pergunta  # retorna o registro existente
    return crud.create_pergunta(db, pergunta)

# Responder pergunta
@app.post("/responder", response_model=schemas.Pergunta)
def responder(resposta_data: schemas.RespostaCreate, db: Session = Depends(get_db)):
    result = crud.responder(db, resposta_data.id, resposta_data.resposta)
    if not result:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")
    return result

# Corrigir resposta
@app.put("/resposta/{pergunta_id}", response_model=schemas.Pergunta)
def corrigir_resposta(correcao: schemas.CorrecaoResposta, db: Session = Depends(get_db)):
    result = crud.corrigir_resposta(db, correcao.id, correcao.resposta)
    if not result:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")
    return result

# Deletar pergunta
@app.delete("/pergunta/{pergunta_id}")
def deletar_pergunta(pergunta_id: int, db: Session = Depends(get_db)):
    result = crud.delete_pergunta(db, pergunta_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")
    return {"message": "Pergunta deletada com sucesso"}