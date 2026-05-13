FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copia las imágenes de personajes (agrega las tuyas aquí: frontend/images/<id>.png)
COPY images/ /usr/share/nginx/html/images/
EXPOSE 80
