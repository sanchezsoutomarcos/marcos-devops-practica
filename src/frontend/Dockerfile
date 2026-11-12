# Imagen del frontend: un servidor web nginx que sirve la página index.html
FROM nginx:1.27-alpine

# Configuración de nginx: sirve la página y reenvía /api/ al contenedor de la API
# (--chmod=644 da permiso de lectura para que el servidor web pueda abrir los ficheros)
COPY --chmod=644 nginx.conf /etc/nginx/conf.d/default.conf

# Página del frontend
COPY --chmod=644 index.html /usr/share/nginx/html/index.html

EXPOSE 80
