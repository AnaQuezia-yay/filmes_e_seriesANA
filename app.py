from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2 # Nossa nova biblioteca de banco em nuvem
from flasgger import Swagger
import os

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# Cole o seu link do Neon dentro das aspas simples do segundo parâmetro!
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_MxjDJ95ZnihB@ep-gentle-bonus-axgnde7b-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # No Postgre, AUTOINCREMENT se chama SERIAL
    c.execute('''CREATE TABLE IF NOT EXISTS filmes 
                 (id SERIAL PRIMARY KEY, titulo TEXT, diretor TEXT, ano INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/filmes', methods=['GET'])
def listar_filmes():
    """... (Documentação Swagger omitida para economizar espaço, pode manter a sua) ..."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM filmes')
    filmes = [{'id': row[0], 'titulo': row[1], 'diretor': row[2], 'ano': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(filmes)

@app.route('/filmes', methods=['POST'])
def adicionar_filme():
    """... (Documentação Swagger) ..."""
    novo_filme = request.json
    
    if not novo_filme.get('titulo') or not novo_filme.get('diretor'):
        return jsonify({'erro': 'Título e diretor são obrigatórios!'}), 400
    if int(novo_filme.get('ano', 0)) < 1888:
        return jsonify({'erro': 'O ano do filme é inválido!'}), 400
        
    conn = get_connection()
    c = conn.cursor()
    # O Postgre usa %s em vez de ?
    c.execute('INSERT INTO filmes (titulo, diretor, ano) VALUES (%s, %s, %s)', 
              (novo_filme['titulo'], novo_filme['diretor'], novo_filme['ano']))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme cadastrado com sucesso!'}), 201

@app.route('/filmes/<int:id>', methods=['PUT'])
def atualizar_filme(id):
    """... (Documentação Swagger) ..."""
    dados = request.json
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE filmes SET titulo = %s, diretor = %s, ano = %s WHERE id = %s', 
              (dados['titulo'], dados['diretor'], dados['ano'], id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme atualizado com sucesso!'})

@app.route('/filmes/<int:id>', methods=['DELETE'])
def excluir_filme(id):
    """... (Documentação Swagger) ..."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM filmes WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme excluído com sucesso!'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')