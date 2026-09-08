# sei-digitals
# SEI Digitals

Plataforma web para la gestión integral de **FL Servicios Eléctricos Integrales SpA**: clientes, proveedores, proyectos, insumos, compras, ventas, facturación, dashboards financieros y un módulo de Inteligencia Artificial predictiva de ganancias y utilidades.

Proyecto APT — Asignatura Capstone, Ingeniería Informática, Duoc UC (Sede Viña del Mar).

**Equipo:** Moisés Roa · Tomás Vega · Natanael Yáñez

---

## Stack tecnológico

- **Lenguaje:** Python 3.12
- **Interfaz:** Streamlit
- **Base de datos:** PostgreSQL (Supabase / Neon en el free tier)
- **ORM / migraciones:** SQLAlchemy + Alembic
- **Datos / ML:** pandas, scikit-learn
- **Visualización:** Plotly

---

## Estructura del proyecto

```
sei-digitals/
├── app/                # Interfaz Streamlit (páginas)
├── core/                # Lógica de negocio (clientes, proveedores, proyectos, facturación, auth, notificaciones)
├── data/                # Conexión a BD, modelos ORM, migraciones e integración de datos externos
├── ml/                  # Preprocesamiento, entrenamiento y predicción del modelo de IA
├── tests/               # Pruebas automatizadas
├── docs/                # Documentación y evidencias del APT
├── .streamlit/          # Configuración y secretos de Streamlit (secrets.toml NO se sube a git)
├── requirements.txt
└── .env.example
```

---

## Requisitos previos

- Python **3.12** (recomendado; versiones muy nuevas como 3.13/3.14 pueden dar problemas al instalar algunas librerías).
- Git instalado.
- Una cuenta de base de datos PostgreSQL gratuita (Supabase o Neon.tech).

---

## Instalación — Windows

**1. Instalar Python 3.12**

Descarga el instalador desde [python.org/downloads](https://www.python.org/downloads/release/python-3120/) (elige "Windows installer 64-bit"). Durante la instalación, **marca la casilla "Add python.exe to PATH"** antes de darle a Instalar — es el paso que más gente olvida.

Verifica en PowerShell o CMD:
```powershell
python --version
```
Debería mostrar `Python 3.12.x`.

**2. Clonar el repositorio**
```powershell
cd Desktop
git clone https://github.com/T-VeMo/sei-digitals.git
cd sei-digitals
```

**3. Crear el entorno virtual**
```powershell
python -m venv venv
```

**4. Activar el entorno virtual**
```powershell
venv\Scripts\activate
```
Tu prompt debería mostrar `(venv)` al inicio de la línea.

> Si PowerShell muestra un error de "no se puede cargar el script porque la ejecución de scripts está deshabilitada", ejecuta esto una sola vez y vuelve a intentar:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

**5. Instalar las dependencias**
```powershell
pip install -r requirements.txt
```

**6. Verificar la instalación**
```powershell
pip list
```

**7. Desactivar el entorno cuando termines de trabajar**
```powershell
deactivate
```

---

## Instalación — macOS

**1. Instalar Python 3.12** (vía Homebrew)
```bash
brew install python@3.12
python3.12 --version
```

**2. Clonar el repositorio**
```bash
cd ~/Desktop
git clone https://github.com/tu-usuario/sei-digitals.git
cd sei-digitals
```

**3. Crear el entorno virtual**
```bash
python3.12 -m venv venv
```

**4. Activar el entorno virtual**
```bash
source venv/bin/activate
```

**5. Instalar las dependencias**
```bash
pip install -r requirements.txt
```

**6. Verificar la instalación**
```bash
pip list
```

**7. Desactivar el entorno cuando termines de trabajar**
```bash
deactivate
```

---

## Variables de entorno

Copia `.env.example` a `.env` y completa con tus credenciales reales de la base de datos:

```
DATABASE_URL=postgresql://usuario:password@host:puerto/nombre_bd
```

El archivo `.env` **nunca se sube a GitHub** (ya está en `.gitignore`). Cada integrante mantiene su propia copia local.

---

## Ejecutar la aplicación

Con el entorno virtual activado:
```bash
streamlit run app/main.py
```

---

## Flujo de trabajo en Git

- Nunca se trabaja directo sobre `main`.
- Cada tarea se hace en una rama nueva: `feature/nombre-de-la-tarea`.
- Al terminar, se sube la rama y se abre un Pull Request para que otro integrante lo revise antes de fusionar a `main`.
- Siempre hacer `git pull origin main` antes de empezar a trabajar.

Convenciones de nombres de rama:
| Prefijo | Uso |
|---|---|
| `feature/` | Funcionalidad nueva |
| `fix/` | Corrección de errores |
| `docs/` | Cambios solo en documentación |

---

## Roles del equipo

| Integrante | Área principal |
|---|---|
| Moisés Roa | Base de datos, backend, requerimientos |
| Tomás Vega | Frontend, dashboards |
| Natanael Yáñez | Modelo predictivo (IA), pruebas, despliegue |
