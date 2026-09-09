# 1. Escolhe o sistema e a versão do Python (nosso fogão)
FROM python:3.10-slim

# 2. Cria a pasta onde o projeto vai ficar dentro do container
WORKDIR /app

# 3. Copia a lista de compras e instala as bibliotecas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia todos os seus arquivos (app.py, banco de dados) para dentro
COPY . .

# 5. Avisa que o Food Truck atende na porta 5000
EXPOSE 5000

# 6. O comando para ligar o motor quando alguém rodar o projeto
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]