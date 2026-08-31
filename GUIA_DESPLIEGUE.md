# 🚀 Guía de Despliegue Automatizado a Producción: Llankay

Esta guía explica cómo desplegar **Llankay** en la nube de forma **100% automatizada y gratuita** utilizando **Railway (Backend)** y **Vercel (Frontend)** con conexión continua a GitHub.

---

## 🏗️ Arquitectura de Producción

```
   [ Cliente / Navegador ]
             │
      ┌──────┴───────────────────────────┐
      ▼                                  ▼
[ Frontend: Vercel ]           [ Backend: Railway / Render ]
  • Vue 3 + Vite + PWA           • Django + Gunicorn + Whitenoise
  • Dominio HTTPS gratuito       • PostgreSQL Gestionado
  • CDN Global                   • Agente IA Groq (LLaMA 3.3 70B)
```

---

## ⚡ Paso 1: Desplegar el Backend en Railway (3 minutos)

1. Ingresa a [Railway.app](https://railway.app) e inicia sesión con tu cuenta de **GitHub**.
2. Haz clic en **"New Project"** ➔ **"Deploy from GitHub repo"**.
3. Selecciona tu repositorio `TesinaLlankayVS`.
4. En la configuración del servicio:
   - **Root Directory:** Pon `/backend`
5. Añade una base de datos PostgreSQL:
   - En el canvas de Railway, haz clic en **"+ New"** ➔ **"Database"** ➔ **"Add PostgreSQL"**.
   - Railway creará automáticamente la variable `DATABASE_URL` conectada a tu Django.
6. Agrega las **Variables de Entorno (Variables)** en Railway:
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(Genera cualquier texto seguro)*
   - `ALLOWED_HOSTS`: `*`
   - `GROQ_API_KEY`: *(Tu API key de Groq `gsk_...`)*
   - `CORS_ALLOWED_ORIGINS`: `https://tu-frontend.vercel.app` *(o `*` inicialmente)*
   - `CSRF_TRUSTED_ORIGINS`: `https://tu-backend.up.railway.app,https://tu-frontend.vercel.app`
7. En la pestaña **Settings** de tu servicio Django en Railway:
   - En **Networking**, haz clic en **"Generate Domain"** (ej: `https://llankay-backend.up.railway.app`).
8. ¡Listo! Railway detectará automáticamente el archivo [`Procfile`](file:///c:/Users/cheba/Downloads/TesinaLlankayVS/backend/Procfile) y [`build.sh`](file:///c:/Users/cheba/Downloads/TesinaLlankayVS/backend/build.sh), ejecutará las migraciones y levantará Django con Gunicorn.

---

## ⚡ Paso 2: Desplegar el Frontend en Vercel (2 minutos)

1. Ingresa a [Vercel.com](https://vercel.com) e inicia sesión con tu cuenta de **GitHub**.
2. Haz clic en **"Add New..."** ➔ **"Project"**.
3. Importa el repositorio `TesinaLlankayVS`.
4. Configura el proyecto en Vercel:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Haz clic en *Edit* y selecciona `frontend`
5. Despliega la sección **Environment Variables**:
   - Nombre: `VITE_API_URL`
   - Valor: `https://tu-backend.up.railway.app/api` *(La URL que te generó Railway)*
6. Haz clic en **"Deploy"**.
7. En menos de 1 minuto tendrás tu web online con HTTPS y dominio `https://tu-proyecto.vercel.app`.

---

## 🔄 ¿Cómo se actualiza en el futuro? (Despliegue Continuo / CI/CD)

Cada vez que hagas un cambio en tu código y ejecutes:
```powershell
git add .
git commit -m "Nuevas mejoras"
git push origin main
```
Tanto **Railway** como **Vercel** detectarán el commit automáticamente, compilarán y publicarán la nueva versión **sin que tengas que hacer nada manual**.

---

## 💻 Ejecución Local Rápida (1-Click)

Si estás en tu computadora y quieres abrir todo el proyecto para trabajar o hacer una demostración:
- Haz doble clic en el archivo [`iniciar_proyecto.bat`](file:///c:/Users/cheba/Downloads/TesinaLlankayVS/iniciar_proyecto.bat).
- Se abrirán el backend en el puerto `8000`, el frontend en el puerto `5173` y tu navegador por defecto automáticamente.
