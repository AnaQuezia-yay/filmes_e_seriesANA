from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2 
from flasgger import Swagger
import os
import requests
import jwt
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# --- CONFIGURAÇÕES DE SEGURANÇA ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'minha_chave_super_secreta_tsukiglow')

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_MxjDJ95ZnihB@ep-gentle-bonus-axgnde7b-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
TMDB_API_KEY = '7316bff7a87ceb19bc03059e79ce0f6d'

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Tabela de usuários
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    
    # 2. Cria o seu usuário padrão se ele não existir (Admin será sempre o ID 1)
    c.execute('SELECT * FROM usuarios WHERE username = %s', ('admin',))
    if not c.fetchone():
        senha_criptografada = generate_password_hash('TsukiGlow2026')
        c.execute('INSERT INTO usuarios (username, password) VALUES (%s, %s)', ('admin', senha_criptografada))
    
    # 3. Tabela de filmes agora com usuario_id
    c.execute('''CREATE TABLE IF NOT EXISTS filmes 
                 (id SERIAL PRIMARY KEY, titulo TEXT, diretor TEXT, ano INTEGER, descricao TEXT, link_trailer TEXT, url_capa TEXT, usuario_id INTEGER)''')
    
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS descricao TEXT')
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS link_trailer TEXT')
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS url_capa TEXT')
    c.execute('ALTER TABLE filmes ADD COLUMN IF NOT EXISTS usuario_id INTEGER')
    
    # 4. Transfere todos os filmes antigos (sem dono) para a sua conta Admin
    c.execute('UPDATE filmes SET usuario_id = 1 WHERE usuario_id IS NULL')
        
    conn.commit()
    conn.close()

init_db()

# --- O SEGURANÇA DA FESTA (DECORATOR JWT) ---
def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            if 'Bearer ' in token:
                token = token.split(' ')[1]
                
        if not token:
            return jsonify({'erro': 'Acesso negado! Faça login primeiro.'}), 401
            
        try:
            # Extrai o ID do usuário de dentro do token
            dados = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = dados.get('user_id')
        except Exception as e:
            return jsonify({'erro': 'Sessão expirada ou inválida. Faça login novamente!'}), 401
            
        # Passa o ID do usuário para a rota que foi chamada
        return f(current_user_id, *args, **kwargs)
    return decorated

# --- ROTA DE LOGIN ---
@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'erro': 'Usuário e senha são obrigatórios!'}), 400
        
    conn = get_connection()
    c = conn.cursor()
    # Pega o ID também
    c.execute('SELECT id, password FROM usuarios WHERE username = %s', (auth.get('username'),))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], auth.get('password')):
        # Guarda o ID do usuário dentro do token
        token = jwt.encode({
            'user_id': user[0],
            'user': auth.get('username'), 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token, 'mensagem': 'Login realizado com sucesso!'})
        
    return jsonify({'erro': 'Usuário ou senha incorretos!'}), 401

# --- ROTA DE CADASTRO ---
@app.route('/registrar', methods=['POST'])
def registrar():
    dados = request.json
    if not dados or not dados.get('username') or not dados.get('password'):
        return jsonify({'erro': 'Usuário e senha são obrigatórios!'}), 400
        
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM usuarios WHERE username = %s', (dados['username'],))
    if c.fetchone():
        conn.close()
        return jsonify({'erro': 'Este nome de usuário já está em uso! Escolha outro.'}), 400
        
    senha_criptografada = generate_password_hash(dados['password'])
    c.execute('INSERT INTO usuarios (username, password) VALUES (%s, %s)', 
              (dados['username'], senha_criptografada))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Conta criada com sucesso! Agora você pode fazer login.'}), 201

# --- FUNÇÃO DO TMDB ---
def buscar_dados_tmdb(titulo):
    dados = {"trailer": "", "capa": ""}
    try:
        url_busca = "https://api.themoviedb.org/3/search/movie"
        params_busca = {"api_key": TMDB_API_KEY, "query": titulo, "language": "pt-BR"}
        resposta_busca = requests.get(url_busca, params=params_busca).json()
        if not resposta_busca.get('results'): return dados
        filme = resposta_busca['results'][0]
        filme_id = filme['id']
        if filme.get('poster_path'):
            dados["capa"] = f"https://image.tmdb.org/t/p/w500{filme['poster_path']}"
        url_videos = f"https://api.themoviedb.org/3/movie/{filme_id}/videos"
        params_videos = {"api_key": TMDB_API_KEY, "language": "pt-BR"}
        resposta_videos = requests.get(url_videos, params=params_videos).json()
        for video in resposta_videos.get('results', []):
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                dados["trailer"] = f"https://www.youtube.com/watch?v={video['key']}"
                return dados
        return dados
    except Exception:
        return dados

# --- ROTAS DE FILMES ---

@app.route('/filmes', methods=['GET'])
def listar_filmes():
    # ID 1 é o Admin (Você). Será a vitrine padrão para os visitantes.
    usuario_id = 1 
    
    # Se a pessoa enviou um crachá, mostramos o catálogo dela
    if 'Authorization' in request.headers:
        token_header = request.headers['Authorization']
        if 'Bearer ' in token_header:
            token = token_header.split(' ')[1]
            try:
                dados = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                usuario_id = dados.get('user_id', 1)
            except:
                pass # Se o token for falso, volta pra vitrine
                
    termo = request.args.get('busca') or request.args.get('termo') or request.args.get('q')
    conn = get_connection()
    c = conn.cursor()
    
    if termo:
        termo_formatado = f'%{termo}%'
        c.execute('''SELECT id, titulo, diretor, ano, descricao, link_trailer, url_capa FROM filmes 
                     WHERE (titulo ILIKE %s OR diretor ILIKE %s OR descricao ILIKE %s) AND usuario_id = %s
                     ORDER BY id''', (termo_formatado, termo_formatado, termo_formatado, usuario_id))
    else:
        c.execute('SELECT id, titulo, diretor, ano, descricao, link_trailer, url_capa FROM filmes WHERE usuario_id = %s ORDER BY id', (usuario_id,))
        
    filmes = [{'id': r[0], 'titulo': r[1], 'diretor': r[2], 'ano': r[3], 'descricao': r[4] or '', 'link_trailer': r[5] or '', 'url_capa': r[6] or ''} for r in c.fetchall()]
    conn.close()
    return jsonify(filmes)

@app.route('/filmes', methods=['POST'])
@token_obrigatorio
def adicionar_filme(current_user_id):
    novo_filme = request.json
    if not novo_filme.get('titulo') or not novo_filme.get('diretor'):
        return jsonify({'erro': 'Título e diretor são obrigatórios!'}), 400
    descricao = novo_filme.get('descricao', '')
    link_trailer = novo_filme.get('link_trailer', '').strip()
    url_capa = novo_filme.get('url_capa', '').strip()
    
    if not link_trailer or not url_capa:
        dados_tmdb = buscar_dados_tmdb(novo_filme['titulo'])
        link_trailer = link_trailer or dados_tmdb['trailer']
        url_capa = url_capa or dados_tmdb['capa']
        
    conn = get_connection()
    c = conn.cursor()
    # Salva o filme com a "etiqueta" do dono (current_user_id)
    c.execute('INSERT INTO filmes (titulo, diretor, ano, descricao, link_trailer, url_capa, usuario_id) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
              (novo_filme['titulo'], novo_filme['diretor'], novo_filme.get('ano'), descricao, link_trailer, url_capa, current_user_id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme cadastrado no seu catálogo!'}), 201

@app.route('/filmes/<int:id>', methods=['PUT'])
@token_obrigatorio
def atualizar_filme(current_user_id, id):
    dados = request.json
    conn = get_connection()
    c = conn.cursor()
    
    # Só atualiza se o filme for daquele usuário
    c.execute('UPDATE filmes SET titulo = %s, diretor = %s, ano = %s, descricao = %s, link_trailer = %s, url_capa = %s WHERE id = %s AND usuario_id = %s', 
              (dados['titulo'], dados['diretor'], dados['ano'], dados.get('descricao', ''), dados.get('link_trailer', ''), dados.get('url_capa', ''), id, current_user_id))
              
    if c.rowcount == 0:
        conn.close()
        return jsonify({'erro': 'Acesso negado ou título não encontrado no seu catálogo.'}), 403
        
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Filme atualizado com sucesso!'})

@app.route('/filmes/<int:id>', methods=['DELETE'])
@token_obrigatorio
def excluir_filme(current_user_id, id):
    conn = get_connection()
    c = conn.cursor()
    # Só deleta se o filme for daquele usuário
    c.execute('DELETE FROM filmes WHERE id = %s AND usuario_id = %s', (id, current_user_id))
    
    if c.rowcount == 0:
        conn.close()
        return jsonify({'erro': 'Acesso negado ou título não encontrado.'}), 403
        
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