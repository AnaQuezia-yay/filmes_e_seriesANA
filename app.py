from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from flasgger import Swagger # 1. Importando o Swagger

app = Flask(__name__)
CORS(app)
swagger = Swagger(app) # 2. Inicializando o Swagger

def init_db():
    conn = sqlite3.connect('filmes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS filmes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, diretor TEXT, ano INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/filmes', methods=['GET'])
def listar_filmes():
    """
    Lista todos os filmes cadastrados.
    ---
    responses:
      200:
        description: Retorna uma lista de filmes do banco de dados.
    """
    conn = sqlite3.connect('filmes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM filmes')
    filmes = [{'id': row[0], 'titulo': row[1], 'diretor': row[2], 'ano': row[3]} for row in c.fetchall()]
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
        description: Dados do filme (título, diretor e ano).
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
    responses:
      201:
        description: Filme cadastrado com sucesso!
      400:
        description: Erro de validação dos dados enviados.
    """
    novo_filme = request.json
    
    # --- NOSSA BLINDAGEM DE SEGURANÇA ---
    if not novo_filme.get('titulo') or not novo_filme.get('diretor'):
        return jsonify({'erro': 'Título e diretor são obrigatórios!'}), 400
    if int(novo_filme.get('ano', 0)) < 1888:
        return jsonify({'erro': 'O ano do filme é inválido!'}), 400
    # ------------------------------------
        
    conn = sqlite3.connect('filmes.db')
    c = conn.cursor()
    c.execute('INSERT INTO filmes (titulo, diretor, ano) VALUES (?, ?, ?)', 
              (novo_filme['titulo'], novo_filme['diretor'], novo_filme['ano']))
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
    responses:
      200:
        description: Filme atualizado com sucesso!
    """
    dados = request.json
    conn = sqlite3.connect('filmes.db')
    c = conn.cursor()
    c.execute('UPDATE filmes SET titulo = ?, diretor = ?, ano = ? WHERE id = ?', 
              (dados['titulo'], dados['diretor'], dados['ano'], id))
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
    conn = sqlite3.connect('filmes.db')
    c = conn.cursor()
    c.execute('DELETE FROM filmes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme excluído com sucesso!'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)