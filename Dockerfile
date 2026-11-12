# Imagen base oficial de Python, variante ligera
FROM python:3.12-slim

# No generar ficheros .pyc y mostrar los logs al momento
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Variables que lee main.py para arrancar el servidor
ENV HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

# 1) Dependencias: se copian antes que el código para aprovechar la caché de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Código fuente de la aplicación
COPY src/ ./src/

# 3) Usuario sin privilegios: se le da la propiedad del código y permisos para ejecutarlo
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app \
    && chmod -R u+rwX /app
USER appuser

# La API se arranca desde su carpeta para que encuentre models/ y Services/
WORKDIR /app/src/Tienda_online

EXPOSE 8000

# Comando de inicio: main.py arranca uvicorn con HOST y PORT
CMD ["python", "main.py"]
