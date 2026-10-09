from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2 
from flasgger import Swagger
import os

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_MxjDJ95ZnihB@ep-gentle-bonus-axgnde7b-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Adicionamos link_trailer na criação inicial
    c.execute('''CREATE TABLE IF NOT EXISTS filmes 
                 (id SERIAL PRIMARY KEY, titulo TEXT, diretor TEXT, ano INTEGER, descricao TEXT, link_trailer TEXT)''')
    # Garante a criação das colunas caso a tabela já exista de antes
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS descricao TEXT')
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS link_trailer TEXT') # NOVA COLUNA DO TRAILER
    conn.commit()
    conn.close()

init_db()

@app.route('/filmes', methods=['GET'])
def listar_filmes():
    """
    Lista todos os filmes cadastrados ou busca por termo.
    ---
    parameters:
      - name: busca
        in: query
        type: string
        required: false
        description: Termo para pesquisar por título, diretor ou descrição.
    responses:
      200:
        description: Retorna uma lista de filmes do banco de dados.
    """
    termo = request.args.get('busca') or request.args.get('termo') or request.args.get('q')
    conn = get_connection()
    c = conn.cursor()
    if termo:
        termo_formatado = f'%{termo}%'
        # Adicionado link_trailer no SELECT
        c.execute('''SELECT id, titulo, diretor, ano, descricao, link_trailer FROM filmes 
                     WHERE titulo ILIKE %s OR diretor ILIKE %s OR descricao ILIKE %s
                     ORDER BY id''',
                  (termo_formatado, termo_formatado, termo_formatado))
    else:
        # Adicionado link_trailer no SELECT
        c.execute('SELECT id, titulo, diretor, ano, descricao, link_trailer FROM filmes ORDER BY id')
    
    filmes = [
        {
            'id': row[0],
            'titulo': row[1],
            'diretor': row[2],
            'ano': row[3],
            'descricao': row[4] or '',
            'link_trailer': row[5] or '' # Mapeia o trailer para enviar ao React
        }
        for row in c.fetchall()
    ]
    conn.close()
    return jsonify(filmes)

@app.route('/filmes', methods=['POST'])
def adicionar_filme():
    """
    Cadastra um novo filme no catálogo.
    """
    novo_filme = request.json
    
    if not novo_filme.get('titulo') or not novo_filme.get('diretor'):
        return jsonify({'erro': 'Título e diretor são obrigatórios!'}), 400
    if int(novo_filme.get('ano', 0)) < 1888:
        return jsonify({'erro': 'O ano do filme é inválido!'}), 400
        
    descricao = novo_filme.get('descricao', '')
    link_trailer = novo_filme.get('link_trailer', '') # Pega o trailer do formulário
    
    conn = get_connection()
    c = conn.cursor()
    # Adicionado link_trailer no INSERT
    c.execute('INSERT INTO filmes (titulo, diretor, ano, descricao, link_trailer) VALUES (%s, %s, %s, %s, %s)', 
              (novo_filme['titulo'], novo_filme['diretor'], novo_filme['ano'], descricao, link_trailer))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme cadastrado com sucesso!'}), 201

@app.route('/filmes/<int:id>', methods=['PUT'])
def atualizar_filme(id):
    """
    Atualiza os dados de um filme existente.
    """
    dados = request.json
    descricao = dados.get('descricao', '')
    link_trailer = dados.get('link_trailer', '') # Pega o trailer atualizado
    
    conn = get_connection()
    c = conn.cursor()
    # Adicionado link_trailer no UPDATE
    c.execute('UPDATE filmes SET titulo = %s, diretor = %s, ano = %s, descricao = %s, link_trailer = %s WHERE id = %s', 
              (dados['titulo'], dados['diretor'], dados['ano'], descricao, link_trailer, id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme atualizado com sucesso!'})

@app.route('/filmes/<int:id>', methods=['DELETE'])
def excluir_filme(id):
    """
    Exclui um filme do catálogo.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM filmes WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme excluído com sucesso!'})

@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css', methods=['GET'])
def style():
    return send_from_directory('.', 'style.css')

@app.route('/logotipo_sem_fundo.png', methods=['GET'])
def logotipo():
    return send_from_directory('.', 'logotipo_sem_fundo.png')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')