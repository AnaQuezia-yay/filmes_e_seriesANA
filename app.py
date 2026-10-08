from flask import Flask, request, jsonify, send_from_directory
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
                 (id SERIAL PRIMARY KEY, titulo TEXT, diretor TEXT, ano INTEGER, descricao TEXT)''')
    # Garante a criação da coluna caso a tabela já exista
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS descricao TEXT')
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
        c.execute('''SELECT id, titulo, diretor, ano, descricao FROM filmes 
                     WHERE titulo ILIKE %s OR diretor ILIKE %s OR descricao ILIKE %s
                     ORDER BY id''',
                  (termo_formatado, termo_formatado, termo_formatado))
    else:
        c.execute('SELECT id, titulo, diretor, ano, descricao FROM filmes ORDER BY id')
    
    filmes = [
        {
            'id': row[0],
            'titulo': row[1],
            'diretor': row[2],
            'ano': row[3],
            'descricao': row[4] or ''
        }
        for row in c.fetchall()
    ]
    conn.close()
    return jsonify(filmes)

@app.route('/filmes', methods=['POST'])
def adicionar_filme():
    """
    Cadastra um novo filme no catálogo.
    ---
    parameters:
      - in: body
        name: body
        required: true
        description: Dados do filme (título, diretor, ano e descrição).
        schema:
          type: object
          properties:
            titulo:
              type: string
              example: Matrix
            diretor:
              type: string
              example: Lana Wachowski
            ano:
              type: integer
              example: 1999
            descricao:
              type: string
              example: Um programador descobre a verdadeira realidade do mundo.
    responses:
      201:
        description: Filme cadastrado com sucesso!
      400:
        description: Erro de validação dos dados enviados.
    """
    novo_filme = request.json
    
    if not novo_filme.get('titulo') or not novo_filme.get('diretor'):
        return jsonify({'erro': 'Título e diretor são obrigatórios!'}), 400
    if int(novo_filme.get('ano', 0)) < 1888:
        return jsonify({'erro': 'O ano do filme é inválido!'}), 400
        
    descricao = novo_filme.get('descricao', '')
    conn = get_connection()
    c = conn.cursor()
    # O Postgre usa %s em vez de ?
    c.execute('INSERT INTO filmes (titulo, diretor, ano, descricao) VALUES (%s, %s, %s, %s)', 
              (novo_filme['titulo'], novo_filme['diretor'], novo_filme['ano'], descricao))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme cadastrado com sucesso!'}), 201

@app.route('/filmes/<int:id>', methods=['PUT'])
def atualizar_filme(id):
    """
    Atualiza os dados de um filme existente.
    ---
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID numérico do filme a ser atualizado.
      - in: body
        name: body
        required: true
        description: Novos dados do filme.
        schema:
          type: object
          properties:
            titulo:
              type: string
            diretor:
              type: string
            ano:
              type: integer
            descricao:
              type: string
    responses:
      200:
        description: Filme atualizado com sucesso!
    """
    dados = request.json
    descricao = dados.get('descricao', '')
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE filmes SET titulo = %s, diretor = %s, ano = %s, descricao = %s WHERE id = %s', 
              (dados['titulo'], dados['diretor'], dados['ano'], descricao, id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme atualizado com sucesso!'})

@app.route('/filmes/<int:id>', methods=['DELETE'])
def excluir_filme(id):
    """
    Exclui um filme do catálogo.
    ---
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID numérico do filme a ser excluído.
    responses:
      200:
        description: Filme excluído com sucesso!
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