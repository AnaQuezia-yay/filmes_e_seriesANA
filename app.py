from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2 
from flasgger import Swagger
import os
import requests

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_MxjDJ95ZnihB@ep-gentle-bonus-axgnde7b-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
TMDB_API_KEY = '7316bff7a87ceb19bc03059e79ce0f6d'

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Adicionamos url_capa na tabela
    c.execute('''CREATE TABLE IF NOT EXISTS filmes 
                 (id SERIAL PRIMARY KEY, titulo TEXT, diretor TEXT, ano INTEGER, descricao TEXT, link_trailer TEXT, url_capa TEXT)''')
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS descricao TEXT')
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS link_trailer TEXT')
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS url_capa TEXT') # NOVA COLUNA
    conn.commit()
    conn.close()

init_db()

def buscar_dados_tmdb(titulo):
    """Busca o trailer oficial e a capa do filme no TMDB."""
    dados = {"trailer": "", "capa": ""}
    try:
        # 1. Busca o ID e a Capa do filme
        url_busca = "https://api.themoviedb.org/3/search/movie"
        params_busca = {"api_key": TMDB_API_KEY, "query": titulo, "language": "pt-BR"}
        resposta_busca = requests.get(url_busca, params=params_busca).json()
        
        if not resposta_busca.get('results'):
            print(f"TMDB: Nenhum filme encontrado com o título '{titulo}'")
            return dados
            
        filme = resposta_busca['results'][0]
        filme_id = filme['id']
        
        # Pega a imagem oficial da capa
        if filme.get('poster_path'):
            dados["capa"] = f"https://image.tmdb.org/t/p/w500{filme['poster_path']}"
        
        # 2. Busca os vídeos
        url_videos = f"https://api.themoviedb.org/3/movie/{filme_id}/videos"
        params_videos = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
        resposta_videos = requests.get(url_videos, params=params_videos).json()
        
        for video in resposta_videos.get('results', []):
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                dados["trailer"] = f"https://www.youtube.com/watch?v={video['key']}"
                return dados
                
        # 3. Fallback: Busca em Inglês
        params_videos_en = {"api_key": TMDB_API_KEY}
        resposta_videos_en = requests.get(url_videos, params=params_videos_en).json()
        for video in resposta_videos_en.get('results', []):
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                dados["trailer"] = f"https://www.youtube.com/watch?v={video['key']}"
                return dados
                
        return dados
    except Exception as e:
        print(f"ERRO CRÍTICO NO TMDB: {e}")
        return dados

@app.route('/filmes', methods=['GET'])
def listar_filmes():
    termo = request.args.get('busca') or request.args.get('termo') or request.args.get('q')
    conn = get_connection()
    c = conn.cursor()
    if termo:
        termo_formatado = f'%{termo}%'
        c.execute('''SELECT id, titulo, diretor, ano, descricao, link_trailer, url_capa FROM filmes 
                     WHERE titulo ILIKE %s OR diretor ILIKE %s OR descricao ILIKE %s
                     ORDER BY id''',
                  (termo_formatado, termo_formatado, termo_formatado))
    else:
        c.execute('SELECT id, titulo, diretor, ano, descricao, link_trailer, url_capa FROM filmes ORDER BY id')
    
    filmes = [
        {
            'id': row[0],
            'titulo': row[1],
            'diretor': row[2],
            'ano': row[3],
            'descricao': row[4] or '',
            'link_trailer': row[5] or '',
            'url_capa': row[6] or '' # Mapeia a capa
        }
        for row in c.fetchall()
    ]
    conn.close()
    return jsonify(filmes)

@app.route('/filmes', methods=['POST'])
def adicionar_filme():
    novo_filme = request.json
    
    if not novo_filme.get('titulo') or not novo_filme.get('diretor'):
        return jsonify({'erro': 'Título e diretor são obrigatórios!'}), 400
    if int(novo_filme.get('ano', 0)) < 1888:
        return jsonify({'erro': 'O ano do filme é inválido!'}), 400
        
    descricao = novo_filme.get('descricao', '')
    link_trailer = novo_filme.get('link_trailer', '').strip()
    url_capa = novo_filme.get('url_capa', '').strip()
    
    # Se faltar o trailer ou a capa, chama o TMDB
    if not link_trailer or not url_capa:
        dados_tmdb = buscar_dados_tmdb(novo_filme['titulo'])
        if not link_trailer:
            link_trailer = dados_tmdb['trailer']
        if not url_capa:
            url_capa = dados_tmdb['capa']
            
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO filmes (titulo, diretor, ano, descricao, link_trailer, url_capa) VALUES (%s, %s, %s, %s, %s, %s)', 
              (novo_filme['titulo'], novo_filme['diretor'], novo_filme['ano'], descricao, link_trailer, url_capa))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme cadastrado com sucesso!'}), 201

@app.route('/filmes/<int:id>', methods=['PUT'])
def atualizar_filme(id):
    dados = request.json
    descricao = dados.get('descricao', '')
    link_trailer = dados.get('link_trailer', '').strip()
    url_capa = dados.get('url_capa', '').strip()
    
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE filmes SET titulo = %s, diretor = %s, ano = %s, descricao = %s, link_trailer = %s, url_capa = %s WHERE id = %s', 
              (dados['titulo'], dados['diretor'], dados['ano'], descricao, link_trailer, url_capa, id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme atualizado com sucesso!'})

@app.route('/filmes/<int:id>', methods=['DELETE'])
def excluir_filme(id):
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