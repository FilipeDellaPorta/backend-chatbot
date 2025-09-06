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
@app.get("/produtos", response_model=list[schemas.Produto])
def listar_produtos(db: Session = Depends(get_db)):
    return crud.get_produtos(db)

@app.get("/perguntas", response_model=list[schemas.Pergunta])
def listar_perguntas(db: Session = Depends(get_db)):
    perguntas = db.query(models.Pergunta).all()
    return perguntas

@app.post("/produtos", response_model=schemas.Produto)
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    return crud.create_produto(db, produto)

@app.post("/pergunta", response_model=schemas.Pergunta)
def fazer_pergunta(pergunta: schemas.PerguntaCreate, db: Session = Depends(get_db)):
    resposta = chatbot.responder_chatbot(pergunta.pergunta, db)
    db_pergunta = crud.create_pergunta(db, pergunta)
    
    if resposta:
        # marcar como respondida com a resposta do chatbot
        db_pergunta.resposta = resposta
        db_pergunta.respondida = True
        db.commit()
        db.refresh(db_pergunta)
    
    return db_pergunta

@app.get("/nao-respondidas", response_model=list[schemas.Pergunta])
def listar_nao_respondidas(db: Session = Depends(get_db)):
    return crud.get_nao_respondidas(db)

@app.post("/responder", response_model=schemas.Pergunta)
def responder_pergunta(resposta_data: schemas.RespostaCreate, db: Session = Depends(get_db)):
    pergunta = db.query(models.Pergunta).filter(models.Pergunta.id == resposta_data.id).first()
    if pergunta:
        pergunta.resposta = resposta_data.resposta
        pergunta.respondida = True
        db.commit()
        db.refresh(pergunta)
        return pergunta
    raise HTTPException(status_code=404, detail="Pergunta não encontrada")

@app.put("/corrigir", response_model=schemas.Pergunta)
def corrigir_resposta(correcao: schemas.CorrecaoResposta, db: Session = Depends(get_db)):
    pergunta = db.query(models.Pergunta).filter(models.Pergunta.id == correcao.id).first()
    if pergunta:
        pergunta.resposta = correcao.resposta
        pergunta.respondida = True  # garante que fique marcada como respondida
        db.commit()
        db.refresh(pergunta)
        return pergunta
    raise HTTPException(status_code=404, detail="Pergunta não encontrada")