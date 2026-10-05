import { useState, useEffect } from 'react'
import './App.css'
import CartaoFilme from './components/CartaoFilme'

function App() {
  const [filmes, setFilmes] = useState([])
  const [pesquisa, setPesquisa] = useState('')
  const [filtro, setFiltro] = useState('todos')
  const [carregando, setCarregando] = useState(true)
  const [modalAberto, setModalAberto] = useState(false)
  const [filmeEdicao, setFilmeEdicao] = useState(null)
  const [formDados, setFormDados] = useState({ titulo: '', diretor: '', ano: '', descricao: '' })
  const [toast, setToast] = useState(null)

  const [apiUrl, setApiUrl] = useState(
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'http://127.0.0.1:5000/filmes'
      : 'https://filmes-e-seriesana.onrender.com/filmes'
  )

  const exibirToast = (mensagem, isErro = false) => {
    setToast({ mensagem, isErro })
    setTimeout(() => {
      setToast(null)
    }, 3500)
  }

  const carregarFilmes = async () => {
    setCarregando(true)
    try {
      let resposta
      try {
        resposta = await fetch(apiUrl)
        if (!resposta.ok) throw new Error('Falha na API primária')
      } catch {
        const fallback = apiUrl.includes('127.0.0.1') || apiUrl.includes('localhost')
          ? 'https://filmes-e-seriesana.onrender.com/filmes'
          : 'http://127.0.0.1:5000/filmes'
        resposta = await fetch(fallback)
        if (resposta.ok) setApiUrl(fallback)
      }
      const dados = await resposta.json()
      setFilmes(dados)
    } catch (erro) {
      console.error("Erro ao carregar filmes:", erro)
      exibirToast("Erro ao conectar ao banco de filmes.", true)
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => {
    carregarFilmes()
  }, [])

  const abrirModalCadastro = () => {
    setFilmeEdicao(null)
    setFormDados({ titulo: '', diretor: '', ano: '', descricao: '' })
    setModalAberto(true)
  }

  const abrirModalEdicao = (filme) => {
    setFilmeEdicao(filme)
    setFormDados({
      titulo: filme.titulo || '',
      diretor: filme.diretor || '',
      ano: filme.ano || '',
      descricao: filme.descricao || ''
    })
    setModalAberto(true)
  }

  const fecharModal = () => {
    setModalAberto(false)
    setFilmeEdicao(null)
  }

  const handleSalvar = async (e) => {
    e.preventDefault()
    const corpo = {
      titulo: formDados.titulo.trim(),
      diretor: formDados.diretor.trim(),
      ano: parseInt(formDados.ano),
      descricao: formDados.descricao.trim()
    }

    try {
      let resposta
      if (filmeEdicao) {
        resposta = await fetch(`${apiUrl}/${filmeEdicao.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(corpo)
        })
        exibirToast("Título atualizado com sucesso!")
      } else {
        resposta = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(corpo)
        })
        exibirToast("Título cadastrado com sucesso!")
      }

      if (!resposta.ok) throw new Error("Erro ao salvar dados.")
      fecharModal()
      carregarFilmes()
    } catch (err) {
      exibirToast(err.message || "Erro ao salvar filme.", true)
    }
  }

  const handleExcluir = async (id, titulo) => {
    const nome = titulo ? `"${titulo}"` : 'este título'
    if (window.confirm(`Deseja remover ${nome} do catálogo Crunchyroll?`)) {
      try {
        const res = await fetch(`${apiUrl}/${id}`, { method: 'DELETE' })
        if (!res.ok) throw new Error("Erro ao excluir")
        exibirToast("Título removido com sucesso!")
        carregarFilmes()
      } catch {
        exibirToast("Erro ao excluir filme.", true)
      }
    }
  }

  // Filtragem e ordenação
  let filmesProcessados = filmes.filter((filme) => {
    const termo = pesquisa.toLowerCase().trim()
    const tituloMatch = filme.titulo && filme.titulo.toLowerCase().includes(termo)
    const descMatch = filme.descricao && filme.descricao.toLowerCase().includes(termo)
    const diretorMatch = filme.diretor && filme.diretor.toLowerCase().includes(termo)
    return tituloMatch || descMatch || diretorMatch
  })

  if (filtro === 'recentes') {
    filmesProcessados.sort((a, b) => (b.ano || 0) - (a.ano || 0))
  } else if (filtro === 'antigos') {
    filmesProcessados.sort((a, b) => (a.ano || 0) - (b.ano || 0))
  } else if (filtro === 'az') {
    filmesProcessados.sort((a, b) => (a.titulo || '').localeCompare(b.titulo || ''))
  }

  return (
    <div className="app-wrapper">
      {/* NAVBAR */}
      <header className="cr-navbar">
        <div className="cr-nav-left">
          <div className="cr-brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <svg className="cr-logo-svg" viewBox="0 0 36 36" fill="none">
              <circle cx="18" cy="18" r="16" fill="#FF640A" />
              <path d="M18 6C11.373 6 6 11.373 6 18C6 24.627 11.373 30 18 30C24.627 30 30 24.627 30 18C30 11.373 24.627 6 18 6ZM18 26.5C13.306 26.5 9.5 22.694 9.5 18C9.5 13.306 13.306 9.5 18 9.5C20.086 9.5 22.001 10.252 23.491 11.511C20.406 12.221 17.925 14.685 17.195 17.765C17.07 18.291 17 18.839 17 19.4C17 21.042 17.658 22.529 18.73 23.633C17.915 24.183 16.924 24.5 15.86 24.5C13.728 24.5 12 22.772 12 20.64C12 18.508 13.728 16.78 15.86 16.78C16.486 16.78 17.074 16.928 17.595 17.191C18.423 13.684 21.391 11 25 11C26.565 11 28 11.522 29.155 12.404C28.136 20.355 21.306 26.5 18 26.5Z" fill="#FFFFFF" />
            </svg>
            <div className="cr-brand-name">Crunchy<span>roll</span></div>
          </div>
          <ul className="cr-nav-links">
            <li><a href="#catalogo" className="active">Explorar</a></li>
            <li><a href="#catalogo">Catálogo</a></li>
            <li><a href="#catalogo">Populares</a></li>
          </ul>
        </div>

        <div className="cr-nav-right">
          <button className="btn-add-nav" onClick={abrirModalCadastro}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Novo Título
          </button>
          <div className="cr-user-badge" title="Usuário Premium">CR</div>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="cr-hero">
        <div className="cr-hero-content">
          <div className="cr-hero-badge">★ Destaque da Temporada</div>
          <h1 className="cr-hero-title">O Melhor do Cinema & Séries em um só Lugar</h1>
          <div className="cr-hero-meta">
            <span className="tag-rating">★ 4.9 Recomendado</span>
            <span>•</span>
            <span className="tag-quality">4K ULTRA HD</span>
            <span>•</span>
            <span>Dublado & Legendado</span>
            <span>•</span>
            <span>Neon Cloud DB</span>
          </div>
          <p className="cr-hero-desc">
            Organize, acompanhe e gerencie seu catálogo de filmes e animações com o design e a velocidade que você merece. Cadastre novas produções instantaneamente.
          </p>
          <div className="cr-hero-actions">
            <a href="#catalogo" className="btn-hero-primary">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              Explorar Catálogo
            </a>
            <button className="btn-hero-secondary" onClick={abrirModalCadastro}>
              + Cadastrar Novo Título
            </button>
          </div>
        </div>
      </section>

      {/* CATÁLOGO PRINCIPAL */}
      <main className="cr-main-container" id="catalogo">
        <div className="cr-section-header">
          <div className="cr-section-title-wrap">
            <div className="cr-orange-bar" />
            <h2 className="cr-section-title">Catálogo de Títulos</h2>
          </div>
          <div className="cr-counter-badge">
            {carregando ? 'Carregando catálogo...' : `${filmesProcessados.length} títulos encontrados`}
          </div>
        </div>

        {/* CONTROLES */}
        <div className="cr-controls-bar">
          <div className="cr-search-box">
            <input
              type="text"
              placeholder="Pesquisar por título, diretor ou sinopse..."
              value={pesquisa}
              onChange={(e) => setPesquisa(e.target.value)}
              className="cr-search-input"
            />
            <div className="cr-search-icon">🔍</div>
          </div>

          <div className="cr-filter-tabs">
            <button
              className={`cr-filter-btn ${filtro === 'todos' ? 'active' : ''}`}
              onClick={() => setFiltro('todos')}
            >
              Todos
            </button>
            <button
              className={`cr-filter-btn ${filtro === 'recentes' ? 'active' : ''}`}
              onClick={() => setFiltro('recentes')}
            >
              Mais Recentes
            </button>
            <button
              className={`cr-filter-btn ${filtro === 'antigos' ? 'active' : ''}`}
              onClick={() => setFiltro('antigos')}
            >
              Clássicos
            </button>
            <button
              className={`cr-filter-btn ${filtro === 'az' ? 'active' : ''}`}
              onClick={() => setFiltro('az')}
            >
              A-Z
            </button>
          </div>
        </div>

        {/* GRADE DE FILMES */}
        {carregando ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div className="cr-spinner" />
            <p style={{ color: '#a0a0a0', marginTop: '10px' }}>Carregando produções da nuvem...</p>
          </div>
        ) : filmesProcessados.length === 0 ? (
          <div className="cr-empty-state" style={{ textAlign: 'center', padding: '4rem 2rem', background: '#141519', borderRadius: '8px', border: '1px dashed #32353e' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎬</div>
            <h3 style={{ fontFamily: 'Rubik, sans-serif', fontSize: '1.3rem', color: '#fff' }}>Nenhum título encontrado</h3>
            <p style={{ color: '#a0a0a0', margin: '0.5rem 0 1.5rem' }}>Adicione um novo filme ou tente pesquisar por outro termo.</p>
            <button className="btn-hero-primary" onClick={abrirModalCadastro}>+ Cadastrar Primeiro Título</button>
          </div>
        ) : (
          <div className="cr-movies-grid">
            {filmesProcessados.map((filme) => (
              <CartaoFilme
                key={filme.id}
                id={filme.id}
                titulo={filme.titulo}
                diretor={filme.diretor}
                ano={filme.ano}
                descricao={filme.descricao}
                onEdit={abrirModalEdicao}
                onDelete={handleExcluir}
              />
            ))}
          </div>
        )}
      </main>

      {/* MODAL */}
      {modalAberto && (
        <div className="cr-modal-overlay" onClick={(e) => e.target.className.includes('cr-modal-overlay') && fecharModal()}>
          <div className="cr-modal">
            <div className="cr-modal-header">
              <div className="cr-modal-title-wrap">
                <div className="cr-orange-bar" />
                <h3 className="cr-modal-title">
                  {filmeEdicao ? 'Editar Título' : 'Cadastrar Novo Título'}
                </h3>
              </div>
              <button className="cr-modal-close" onClick={fecharModal}>&times;</button>
            </div>

            <form onSubmit={handleSalvar}>
              <div className="cr-modal-body">
                <div className="cr-form-group">
                  <label>Título da Obra</label>
                  <input
                    type="text"
                    required
                    className="cr-form-control"
                    placeholder="Ex: Demon Slayer: Mugen Train, Carros, Matrix"
                    value={formDados.titulo}
                    onChange={(e) => setFormDados({ ...formDados, titulo: e.target.value })}
                  />
                </div>

                <div className="cr-form-group" style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px' }}>
                  <div>
                    <label>Diretor / Estúdio</label>
                    <input
                      type="text"
                      required
                      className="cr-form-control"
                      placeholder="Ex: John Lasseter, Haruo Sotozaki"
                      value={formDados.diretor}
                      onChange={(e) => setFormDados({ ...formDados, diretor: e.target.value })}
                    />
                  </div>
                  <div>
                    <label>Ano</label>
                    <input
                      type="number"
                      required
                      min="1888"
                      max="2099"
                      className="cr-form-control"
                      placeholder="Ex: 2024"
                      value={formDados.ano}
                      onChange={(e) => setFormDados({ ...formDados, ano: e.target.value })}
                    />
                  </div>
                </div>

                <div className="cr-form-group">
                  <label>Sinopse / Descrição</label>
                  <textarea
                    className="cr-form-control"
                    placeholder="Conte um pouco sobre a história, personagens e gênero..."
                    value={formDados.descricao}
                    onChange={(e) => setFormDados({ ...formDados, descricao: e.target.value })}
                  />
                </div>

                <div className="cr-modal-footer">
                  <button type="button" className="btn-modal-cancel" onClick={fecharModal}>
                    Cancelar
                  </button>
                  <button type="submit" className="btn-modal-submit">
                    {filmeEdicao ? 'Atualizar Título' : 'Salvar no Catálogo'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* TOAST */}
      {toast && (
        <div className="cr-toast-container">
          <div className={`cr-toast ${toast.isErro ? 'toast-error' : ''}`}>
            <span>{toast.isErro ? '❌' : '✨'}</span>
            <div>{toast.mensagem}</div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer className="cr-footer">
        <div className="cr-footer-inner">
          <div className="cr-footer-grid">
            <div className="cr-footer-brand">
              <div className="cr-brand">
                <svg className="cr-logo-svg" viewBox="0 0 36 36" fill="none">
                  <circle cx="18" cy="18" r="16" fill="#FF640A" />
                  <path d="M18 6C11.373 6 6 11.373 6 18C6 24.627 11.373 30 18 30C24.627 30 30 24.627 30 18C30 11.373 24.627 6 18 6ZM18 26.5C13.306 26.5 9.5 22.694 9.5 18C9.5 13.306 13.306 9.5 18 9.5C20.086 9.5 22.001 10.252 23.491 11.511C20.406 12.221 17.925 14.685 17.195 17.765C17.07 18.291 17 18.839 17 19.4C17 21.042 17.658 22.529 18.73 23.633C17.915 24.183 16.924 24.5 15.86 24.5C13.728 24.5 12 22.772 12 20.64C12 18.508 13.728 16.78 15.86 16.78C16.486 16.78 17.074 16.928 17.595 17.191C18.423 13.684 21.391 11 25 11C26.565 11 28 11.522 29.155 12.404C28.136 20.355 21.306 26.5 18 26.5Z" fill="#FFFFFF" />
                </svg>
                <div className="cr-brand-name">Crunchy<span>roll</span></div>
              </div>
              <p>Sua plataforma premium para catalogar filmes, séries e animes com alto desempenho e sincronização em tempo real na nuvem.</p>
            </div>

            <div className="cr-footer-col">
              <h4>Navegação</h4>
              <ul>
                <li><a href="#catalogo">Catálogo Completo</a></li>
                <li><a href="#catalogo">Novidades</a></li>
                <li><a href="#catalogo">Mais Avaliados</a></li>
              </ul>
            </div>

            <div className="cr-footer-col">
              <h4>Gerenciamento</h4>
              <ul>
                <li><a href="#catalogo" onClick={abrirModalCadastro}>+ Adicionar Título</a></li>
                <li><a href="#catalogo" onClick={carregarFilmes}>Atualizar Lista</a></li>
              </ul>
            </div>

            <div className="cr-footer-col">
              <h4>Conta & Status</h4>
              <ul>
                <li><span style={{ color: '#4cd137' }}>● Banco Neon Conectado</span></li>
                <li><span>Versão 2.0 • Streaming Interface</span></li>
              </ul>
            </div>
          </div>

          <div className="cr-footer-bottom">
            <div>© 2026 Crunchyroll, LLC • Inspirado no design oficial da Crunchyroll</div>
            <div className="cr-footer-badges">
              <span>Português (Brasil)</span>
              <span>Privacidade</span>
              <span>Termos</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App