FROM python:3.11-slim

WORKDIR /app

# Copie les fichiers
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Démarrer Flask directement
CMD ["python", "app.py"]
