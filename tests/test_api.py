import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_fluxo_completo_crud():
    # 1. Criar categoria
    r_cat = client.post("/categorias", json={"nome": "Estudos"})
    assert r_cat.status_code == 201
    cat_id = r_cat.json()["id"]

    # 2. Listar categorias
    r_cats = client.get("/categorias")
    assert r_cats.status_code == 200
    assert len(r_cats.json()) == 1

    # 3. Criar tarefa
    r_tar = client.post("/tarefas", json={
        "titulo": "Estudar Azure",
        "descricao": "Ler sobre VMs e SKUs",
        "categoria_id": cat_id
    })
    assert r_tar.status_code == 201
    tar_id = r_tar.json()["id"]
    assert r_tar.json()["concluida"] is False

    # 4. Marcar como concluída (PATCH)
    r_patch = client.patch(f"/tarefas/{tar_id}", json={"concluida": True})
    assert r_patch.status_code == 200
    assert r_patch.json()["concluida"] is True

    # 5. Filtrar concluídas
    r_list = client.get("/tarefas?concluida=true")
    assert r_list.status_code == 200
    assert len(r_list.json()) == 1

    # 6. Deletar tarefa
    r_del = client.delete(f"/tarefas/{tar_id}")
    assert r_del.status_code == 204

    # 7. Confirmar 404
    r_get = client.get(f"/tarefas/{tar_id}")
    assert r_get.status_code == 404

def test_validacoes():
    # Categoria duplicada -> 409
    client.post("/categorias", json={"nome": "Trabalho"})
    r_dup = client.post("/categorias", json={"nome": "Trabalho"})
    assert r_dup.status_code == 409

    # Tarefa com título vazio -> 422
    r_inv = client.post("/tarefas", json={"titulo": "   "})
    assert r_inv.status_code == 422

    # Tarefa com categoria inexistente -> 404
    r_cat_404 = client.post("/tarefas", json={"titulo": "Teste", "categoria_id": 999})
    assert r_cat_404.status_code == 404
