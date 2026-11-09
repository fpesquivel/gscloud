from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Tarefas",
    description="API REST básica com banco de dados SQLite para gerenciamento de tarefas e categorias.",
    version="1.0.0",
)

@app.get("/health", tags=["Saúde"])
def health_check():
    return {"status": "ok"}

@app.post("/categorias", response_model=schemas.CategoriaOut, status_code=status.HTTP_201_CREATED, tags=["Categorias"])
def criar_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    existente = db.query(models.Categoria).filter(models.Categoria.nome == categoria.nome).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria já existe")
    nova = models.Categoria(nome=categoria.nome)
    db.add(nova)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria já existe")
    db.refresh(nova)
    return nova

@app.get("/categorias", response_model=List[schemas.CategoriaOut], tags=["Categorias"])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).order_by(models.Categoria.nome.asc()).all()

@app.post("/tarefas", response_model=schemas.TarefaOut, status_code=status.HTTP_201_CREATED, tags=["Tarefas"])
def criar_tarefa(tarefa: schemas.TarefaCreate, db: Session = Depends(get_db)):
    if tarefa.categoria_id is not None:
        cat = db.query(models.Categoria).filter(models.Categoria.id == tarefa.categoria_id).first()
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    nova = models.Tarefa(
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        concluida=tarefa.concluida,
        categoria_id=tarefa.categoria_id,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@app.get("/tarefas", response_model=List[schemas.TarefaOut], tags=["Tarefas"])
def listar_tarefas(
    concluida: Optional[bool] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Tarefa)
    if concluida is not None:
        query = query.filter(models.Tarefa.concluida == concluida)
    if categoria_id is not None:
        query = query.filter(models.Tarefa.categoria_id == categoria_id)
    return query.order_by(models.Tarefa.id.asc()).all()

@app.get("/tarefas/{tarefa_id}", response_model=schemas.TarefaOut, tags=["Tarefas"])
def obter_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    tarefa = db.query(models.Tarefa).filter(models.Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    return tarefa

@app.patch("/tarefas/{tarefa_id}", response_model=schemas.TarefaOut, tags=["Tarefas"])
def atualizar_tarefa(tarefa_id: int, dados: schemas.TarefaUpdate, db: Session = Depends(get_db)):
    tarefa = db.query(models.Tarefa).filter(models.Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    
    update_data = dados.model_dump(exclude_unset=True)
    if "categoria_id" in update_data and update_data["categoria_id"] is not None:
        cat = db.query(models.Categoria).filter(models.Categoria.id == update_data["categoria_id"]).first()
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
            
    for campo, valor in update_data.items():
        setattr(tarefa, campo, valor)
        
    db.commit()
    db.refresh(tarefa)
    return tarefa

@app.delete("/tarefas/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tarefas"])
def remover_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    tarefa = db.query(models.Tarefa).filter(models.Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    db.delete(tarefa)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
