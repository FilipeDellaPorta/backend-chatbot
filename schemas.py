from pydantic import BaseModel

class ProdutoBase(BaseModel):
    nome: str
    descricao: str

class ProdutoCreate(ProdutoBase):
    pass

class Produto(ProdutoBase):
    id: int
    class Config:
        from_attributes = True

class PerguntaBase(BaseModel):
    pergunta: str

class PerguntaCreate(PerguntaBase):
    pass

class Pergunta(PerguntaBase):
    id: int
    resposta: str | None = None
    respondida: bool
    class Config:
        from_attributes = True

class RespostaCreate(BaseModel):
    id: int
    resposta: str