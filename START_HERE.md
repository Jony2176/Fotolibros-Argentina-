# 🚀 START HERE - Deployment en 5 Pasos

## Todo Listo para Deployar

Este proyecto incluye:
- ✅ Frontend (React + Vite)
- ✅ Backend (FastAPI + AGNO)
- ✅ Worker (procesamiento)
- ✅ Clawdbot (skills + config)
- ✅ Scripts automatizados

---

## 5 Pasos para Tener Todo Funcionando

### 1️⃣ Comprimir (EN TU PC)

```powershell
cd C:\Users\Usuario\Downloads\fotolibros_argentina\

Compress-Archive -Path fotolibros-vps-deploy\* -DestinationPath fotolibros.zip -Force
```

---

### 2️⃣ Subir al VPS

```powershell
scp fotolibros.zip usuario@168.231.98.115:/home/usuario/
```

O usar WinSCP / FileZilla.

---

### 3️⃣ Instalar (EN EL VPS)

```bash
ssh usuario@168.231.98.115

cd /home/usuario
unzip fotolibros.zip -d fotolibros-app
cd fotolibros-app
chmod +x scripts/*.sh
./scripts/install-full.sh
```

---

### 4️⃣ Configurar

#### A) Backend

```bash
nano backend/.env
```

Editar estas líneas:
```
CLAWDBOT_HOOK_TOKEN=tu_token_secreto
OPENROUTER_API_KEY=sk-or-v1-xxxx
TELEGRAM_ADMIN_CHAT=@tu_usuario
FDF_USER=tu_usuario_fdf
FDF_PASS=tu_password_fdf
```

#### B) Clawdbot

```bash
nano ~/.clawdbot/clawdbot.json
```

Agregar sección `hooks` y agente `fotolibros` (ver ejemplo en `clawdbot/clawdbot.json.example`).

Reiniciar:
```bash
sudo systemctl restart clawdbot
```

---

### 5️⃣ Iniciar

```bash
sudo systemctl start fotolibros-backend
sudo systemctl start fotolibros-worker
sudo systemctl enable fotolibros-backend
sudo systemctl enable fotolibros-worker
```

---

## ✅ Verificar

```bash
# Health check
curl http://localhost/health

# Ver frontend
curl http://localhost/

# Acceder desde navegador
# http://TU_IP_VPS
```

---

## 📚 Documentación Completa

- **`DEPLOYMENT_COMPLETO.md`** - Guía detallada paso a paso
- **`SQLITE_VS_REDIS.md`** - Por qué usamos SQLite
- **`ARQUITECTURA_COMPLETA.md`** - Diagrama del sistema
- **`README.md`** - Descripción general

---

## 🆘 Ayuda Rápida

### Ver logs

```bash
journalctl -u fotolibros-backend -f
journalctl -u fotolibros-worker -f
```

### Reiniciar

```bash
sudo systemctl restart fotolibros-backend
sudo systemctl restart fotolibros-worker
```

### Ver cola

```bash
sqlite3 /var/fotolibros/fotolibros.db "SELECT * FROM cola"
```

---

## 🎯 Resultado Final

Cuando esté funcionando:

1. Cliente entra a `http://TU_IP_VPS`
2. Completa wizard y sube fotos
3. Paga
4. Sistema automático:
   - AGNO analiza
   - Clawdbot ejecuta en FDF
   - Te notifica por Telegram
5. Vos aprobás
6. ¡Pedido en producción!

**Costo por pedido: ~$0.10 USD**

---

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| Base de Datos | SQLite |
| Cola | SQLite |
| Análisis IA | AGNO (5 agentes) |
| Ejecución | Clawdbot (Claude Max) |
| Browser | Chrome Headless |
| Servidor Web | Nginx |
| Sistema | Ubuntu 24.04 |

Todo en **un solo VPS** 🚀
