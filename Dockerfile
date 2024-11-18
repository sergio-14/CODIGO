# Usa la imagen oficial de Python como base
FROM python:3.10

# Establece el directorio de trabajo
WORKDIR /code

# Copia los archivos de requisitos
COPY requirements.txt /code/

# Instala las dependencias
RUN pip install --upgrade pip  
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el proyecto al contenedor
COPY . /code/

# Configura la variable de entorno para Django
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Ejecuta el comando para iniciar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
