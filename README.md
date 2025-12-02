# 🛒 MercApp  
### Sistema Web de Gestión para Minimarkets, Almacenes y Comercios Locales

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)]()
[![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)]()
[![SQLite](https://img.shields.io/badge/SQLite-Dev_DB-blue?logo=sqlite)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Prod_DB-336791?logo=postgresql)]()
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple?logo=railway)]()
[![Security](https://img.shields.io/badge/Security-.env%20%7C%20Permissions-important?logo=security)]()

---

## 📌 Descripción general

**MercApp** es una plataforma web profesional orientada a la administración de pequeños comercios.  
Ofrece herramientas simples pero potentes para gestionar inventario, ventas, usuarios, reportes y control operativo diario.

Creada como Proyecto de Título del programa **Analista Programador — INACAP (2025)**, MercApp refleja un desarrollo realista, seguro y alineado con las prácticas modernas de la industria del software.

---

## 👨‍💻 Autores

- **Claudio Martínez**  
- **Nicolás Guzmán**  
- **Óscar Verdugo**

---

## 🎯 Propósito del sistema

MercApp fue diseñado para resolver necesidades reales:

- Pérdidas por falta de control de stock  
- Ventas sin registro o sin historial  
- Falta de reportes simples para decidir compras  
- Desorden en precios o productos  
- Dificultad de manejo para usuarios sin experiencia técnica

Su diseño prioriza:

- Simplicidad  
- Rapidez  
- Trazabilidad  
- Seguridad  

---

## 🛠️ Tecnologías utilizadas

| Componente | Tecnología |
|-----------|------------|
| Backend | Django 5.2 (Python 3.12) |
| Base de Datos Desarrollo | SQLite |
| Base de Datos Producción | PostgreSQL (Railway) |
| Frontend | Bootstrap, HTML5, JS puro |
| Estáticos | WhiteNoise |
| Seguridad | Variables de entorno, permisos, CSRF |
| Infraestructura | Railway |

---

## ⚙️ Funcionalidades principales

### 🧾 **Gestión de productos**
- Crear, editar y eliminar productos  
- Stock y stock mínimo configurable  
- Categorización  
- Activar/desactivar producto  
- Búsqueda por código o nombre  
- Índices optimizados para rendimiento

---

### 💰 **Módulo de ventas**
- Flujo intuitivo de venta rápida  
- Búsqueda de productos por código/ID  
- Cálculo automático de subtotales y total  
- Métodos de pago configurables  
- Actualización automática de stock  
- Registro de usuario que efectúa la venta  

---

### ❌ **Anulación de ventas (Auditoría)**
- Anulación con motivo obligatorio  
- Registro de quién anuló  
- Fecha y hora de anulación  
- Venta marcada sin eliminarse (integridad histórica)

---

### 📊 **Reportes**
- Filtrado por rango de fechas  
- Monto total vendido  
- Listado detallado  
- Ideal para decisiones de compra o cierres de caja

---

### 👤 **Usuarios y roles**
- Roles diferenciados 
- Permisos adicionales personalizados:
  - Ver reportes avanzados  
  - Administrar respaldos  
  - Anular ventas  

---

## 📦 Instalación y ejecución en entorno local

### 1️⃣ Clonar repositorio
```bash
git clone https://github.com/tuusuario/mercapp.git
cd mercapp
```

### 2️⃣ Crear entorno virtual
```bash
python -m venv .venv
```

Activar:

**Windows**
```bash
.venv\Scripts\activate
```

**Mac/Linux**
```bash
source .venv/bin/activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Crear archivo `.env`
```
SECRET_KEY=dev_secret_key_123
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

### 5️⃣ Migraciones
```bash
python manage.py migrate
```

### 6️⃣ Crear administrador
```bash
python manage.py createsuperuser
```

### 7️⃣ Ejecutar servidor
```bash
python manage.py runserver
```

---

## ☁️ Deploy a Railway – Producción

### 1. Subir el proyecto a GitHub  
### 2. Crear servicio en Railway  
### 3. Añadir plugin PostgreSQL  
### 4. Configurar variables de entorno en Railway:

```
SECRET_KEY=tu_clave_segura_produccion
DEBUG=False
DATABASE_URL=postgresql://<railway-string>
ALLOWED_HOSTS=tudominio.up.railway.app
```

### 5. Ejecutar comandos post-deploy:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Railway detectará automáticamente el entorno Django + Gunicorn + WhiteNoise.

---

## 🔐 Seguridad implementada

✔ **SECRET_KEY fuera del código**  
✔ **Uso de .env para todos los entornos**  
✔ **CSRF activado**  
✔ **Permisos y grupos por rol**  
✔ **WhiteNoise para archivos estáticos (sin servidor adicional)**  
✔ **Migraciones controladas**  
✔ **Índices en campos críticos (código, nombre)**  

---

## 🧩 Estructura del proyecto

```
mercapp_app/
│── config/            # Configuración Django
│── mercapp/           # Aplicación principal
│── static/            # Archivos estáticos durante desarrollo
│── staticfiles/       # Archivos colectados para producción
│── templates/         # Vistas HTML
│── .env               # Variables de entorno
│── db.sqlite3         # Base de datos local
│── manage.py
│── requirements.txt
```

---

## 📜 Licencia

Proyecto académico — INACAP, 2025.  
Libre de modificar y extender para fines educativos.

---

## 🙌 Agradecimientos

Gracias por revisar MercApp.  
