#!/usr/bin/env bash
# Script para provisionar a infraestrutura na Microsoft Azure via Azure CLI
set -e

RG="rg-tarefas-api"
LOCATION="brazilsouth"
VM_NAME="vm-tarefas-api"
VM_IMAGE="Ubuntu2204"
VM_SIZE="Standard_B1s"
ADMIN_USER="azureuser"

echo "1. Criando grupo de recursos $RG em $LOCATION..."
az group create --name "$RG" --location "$LOCATION"

echo "2. Criando máquina virtual $VM_NAME ($VM_SIZE)..."
az vm create \
  --resource-group "$RG" \
  --name "$VM_NAME" \
  --image "$VM_IMAGE" \
  --size "$VM_SIZE" \
  --admin-username "$ADMIN_USER" \
  --generate-ssh-keys \
  --storage-sku StandardSSD_LRS \
  --os-disk-size-gb 30 \
  --public-ip-sku Standard

echo "3. Liberando porta 80 (HTTP) no NSG..."
az vm open-port --resource-group "$RG" --name "$VM_NAME" --port 80 --priority 1010

PUBLIC_IP=$(az vm show -d -g "$RG" -n "$VM_NAME" --query publicIps -o tsv)
echo "===================================================="
echo "VM provisionada com sucesso!"
echo "IP Público: $PUBLIC_IP"
echo "Conecte via SSH: ssh $ADMIN_USER@$PUBLIC_IP"
echo "===================================================="
