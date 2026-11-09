#!/usr/bin/env bash
# Script executado dentro da VM Ubuntu 22.04 para instalar e configurar a API
# Uso: sudo bash setup_vm.sh <URL_DO_SEU_REPOSITORIO_GITHUB>
set -e

REPO_URL=$1
if [ -z "$REPO_URL" ]; then
    echo "Uso: sudo bash setup_vm.sh https://github.com/SEU_USUARIO/tarefas-api.git"
    exit 1
fi

echo "1. Atualizando pacotes e instalando dependências do sistema..."
apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx git sqlite3 curl

echo "2. Clonando o repositório em /opt/tarefas-api..."
rm -rf /opt/tarefas-api
git clone "$REPO_URL" /opt/tarefas-api

echo "3. Criando ambiente virtual e instalando pacotes Python..."
python3 -m venv /opt/tarefas-api/venv
/opt/tarefas-api/venv/bin/pip install --upgrade pip
/opt/tarefas-api/venv/bin/pip install -r /opt/tarefas-api/requirements.txt

echo "4. Preparando diretório persistente do banco SQLite..."
mkdir -p /var/lib/tarefas-api
chown -R www-data:www-data /var/lib/tarefas-api
chown -R www-data:www-data /opt/tarefas-api

echo "5. Configurando serviço systemd..."
cp /opt/tarefas-api/deploy/tarefas-api.service /etc/systemd/system/tarefas-api.service
systemctl daemon-reload
systemctl enable tarefas-api
systemctl restart tarefas-api

echo "6. Configurando Nginx como proxy reverso na porta 80..."
cp /opt/tarefas-api/deploy/nginx-tarefas-api.conf /etc/nginx/sites-available/tarefas-api
ln -sf /etc/nginx/sites-available/tarefas-api /etc/nginx/sites-enabled/tarefas-api
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo "===================================================="
echo "Deploy concluído! Testando endpoint /health local:"
sleep 2
curl -s http://127.0.0.1/health
echo ""
echo "===================================================="
