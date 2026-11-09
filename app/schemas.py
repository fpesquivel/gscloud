from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

class CategoriaCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=80)

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("O nome da categoria não pode ser vazio.")
        return v

class CategoriaOut(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)

class TarefaCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=120)
    descricao: Optional[str] = None
    concluida: bool = False
    categoria_id: Optional[int] = None

    @field_validator("titulo")
    @classmethod
    def titulo_nao_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("O título da tarefa não pode ser vazio.")
        return v

class TarefaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=120)
    descricao: Optional[str] = None
    concluida: Optional[bool] = None
    categoria_id: Optional[int] = None

    @field_validator("titulo")
    @classmethod
    def titulo_nao_vazio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("O título da tarefa não pode ser vazio.")
        return v

class TarefaOut(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    concluida: bool
    categoria_id: Optional[int] = None
    criada_em: datetime

    model_config = ConfigDict(from_attributes=True)
