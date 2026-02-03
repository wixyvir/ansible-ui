# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy package files and install dependencies (including devDependencies for build)
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Build backend package
FROM rockylinux:9 AS backend-builder

# Install Python and Poetry
RUN dnf install -y epel-release && dnf install -y python3.11 && curl -sSL https://install.python-poetry.org | python3.11 -
ENV PATH="/root/.local/bin:$PATH"

# Copy backend files needed for build
ADD backend/README.md /app/README.md
ADD backend/manage.py /app/manage.py
ADD backend/pyproject.toml /app/pyproject.toml
ADD backend/ansible_ui /app/ansible_ui
ADD backend/api /app/api

WORKDIR /app

# Build the package
RUN poetry build

# Stage 3: Django API service
FROM rockylinux:9 AS api

EXPOSE 8000

# Environment configuration
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1

ENV DJANGO_PROD=True
ENV DJANGO_SETTINGS_MODULE=ansible_ui.settings
ENV DJANGO_STATIC_ROOT=/var/www/html/static/
ENV DJANGO_ALLOWED_HOSTS=localhost:8000

ENV DB_NAME=ansible_ui
ENV DB_USERNAME=ansible_ui
ENV DB_PASSWORD=none
ENV DB_HOSTNAME=db
ENV DB_PORT=5432

# Copy entrypoint script
ADD docker/entrypoint.api.sh /entrypoint.sh

# Install system dependencies
RUN dnf install -y epel-release && dnf install -y python3.11 python3.11-pip nc postgresql python3.11-devel.x86_64 libpq-devel gcc

# Install gunicorn
RUN pip3.11 install gunicorn

# Copy and install built package
COPY --from=backend-builder /app/dist/* /dist/
RUN pip3.11 install ./dist/ansible_ui_backend-*.tar.gz

# Collect static files
RUN django-admin collectstatic --no-input

CMD ["/entrypoint.sh"]

# Stage 4: nginx web server
FROM nginx:stable-alpine AS web

# Copy frontend build
COPY --from=frontend-builder /frontend/dist /var/www/html/frontend

# Copy Django static files
COPY --from=api /var/www/html/static/ /var/www/html/static/

# Copy nginx configuration
RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx.conf /etc/nginx/conf.d

EXPOSE 80
