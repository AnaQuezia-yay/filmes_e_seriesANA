import React from 'react'

const temasPoster = [
  { bg: 'linear-gradient(135deg, #ff640a 0%, #a32200 60%, #150500 100%)', cat: 'AÇÃO & AVENTURA', icon: '🔥' },
  { bg: 'linear-gradient(135deg, #6c5ce7 0%, #2b1055 60%, #0d051a 100%)', cat: 'FICÇÃO CIENTÍFICA', icon: '⚡' },
  { bg: 'linear-gradient(135deg, #00b894 0%, #004d40 60%, #001a14 100%)', cat: 'FANTASIA', icon: '🌌' },
  { bg: 'linear-gradient(135deg, #e84393 0%, #631238 60%, #1a030c 100%)', cat: 'DRAMA', icon: '🌸' },
  { bg: 'linear-gradient(135deg, #0984e3 0%, #0b3966 60%, #021221 100%)', cat: 'SHONEN', icon: '⚔️' },
  { bg: 'linear-gradient(135deg, #f39c12 0%, #7d4800 60%, #1f1100 100%)', cat: 'CLÁSSICO', icon: '⭐' },
  { bg: 'linear-gradient(135deg, #e17055 0%, #631f10 60%, #1b0703 100%)', cat: 'SUSPENSE', icon: '🌑' }
]

function obterTemaPoster(id, titulo) {
  let hash = 0
  const str = (titulo || '') + id
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    hash |= 0
  }
  return temasPoster[Math.abs(hash) % temasPoster.length]
}

function CartaoFilme({ id, titulo, diretor, ano, descricao, onEdit, onDelete }) {
  const tema = obterTemaPoster(id, titulo)

  return (
    <article className="cr-card" style={estilos.card}>
      {/* Pôster estilo Crunchyroll */}
      <div style={estilos.poster}>
        <div style={{ ...estilos.posterBg, background: tema.bg }} />
        <div style={estilos.posterOverlay} />

        {/* Badges superiores */}
        <div style={estilos.posterBadges}>
          <span style={estilos.badgeDub}>DUB | LEG</span>
          <span style={estilos.badgeYear}>{ano || '—'}</span>
        </div>

        {/* Botão de Play */}
        <div className="cr-poster-play" style={estilos.posterPlay} title={`Assistir ${titulo}`}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="6 4 20 12 6 20 6 4" />
          </svg>
        </div>

        <span style={estilos.posterCat}>{tema.icon} {tema.cat}</span>
      </div>

      {/* Corpo do Cartão */}
      <div style={estilos.cardBody}>
        <h3 style={estilos.cardTitle} title={titulo}>
          {titulo || 'Sem Título'}
        </h3>

        <div style={estilos.cardDirector}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{diretor || 'Desconhecido'}</span>
        </div>

        <p style={estilos.cardDesc}>
          {descricao || 'Sem sinopse cadastrada.'}
        </p>

        {/* Ações */}
        <div style={estilos.cardActions}>
          <button 
            type="button" 
            style={estilos.btnEdit}
            onClick={() => onEdit && onEdit({ id, titulo, diretor, ano, descricao })}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
            Editar
          </button>

          <button 
            type="button" 
            style={estilos.btnDelete}
            onClick={() => onDelete && onDelete(id, titulo)}
            title="Excluir do catálogo"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
          </button>
        </div>
      </div>
    </article>
  )
}

const estilos = {
  card: {
    backgroundColor: '#141519',
    borderRadius: '8px',
    overflow: 'hidden',
    border: '1px solid #23252b',
    display: 'flex',
    flexDirection: 'column',
    transition: 'all 0.25s ease',
    textAlign: 'left'
  },
  poster: {
    width: '100%',
    height: '190px',
    position: 'relative',
    overflow: 'hidden',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    userSelect: 'none'
  },
  posterBg: {
    position: 'absolute',
    inset: 0
  },
  posterOverlay: {
    position: 'absolute',
    inset: 0,
    background: 'linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(20,21,25,0.95) 100%)'
  },
  posterBadges: {
    position: 'absolute',
    top: '10px',
    left: '10px',
    right: '10px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    zIndex: 3
  },
  badgeDub: {
    backgroundColor: 'rgba(0, 0, 0, 0.75)',
    border: '1px solid rgba(255, 255, 255, 0.25)',
    color: '#ffffff',
    fontFamily: 'Rubik, sans-serif',
    fontSize: '0.68rem',
    fontWeight: 700,
    padding: '3px 7px',
    borderRadius: '3px',
    textTransform: 'uppercase'
  },
  badgeYear: {
    backgroundColor: '#ff640a',
    color: '#ffffff',
    fontFamily: 'Rubik, sans-serif',
    fontSize: '0.72rem',
    fontWeight: 800,
    padding: '3px 8px',
    borderRadius: '3px'
  },
  posterPlay: {
    position: 'absolute',
    zIndex: 4,
    width: '50px',
    height: '50px',
    backgroundColor: 'rgba(255, 100, 10, 0.95)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    boxShadow: '0 4px 18px rgba(0, 0, 0, 0.5)'
  },
  posterCat: {
    position: 'absolute',
    bottom: '10px',
    left: '12px',
    zIndex: 3,
    fontFamily: 'Rubik, sans-serif',
    fontSize: '0.75rem',
    fontWeight: 800,
    color: '#ff640a',
    textTransform: 'uppercase',
    letterSpacing: '1px'
  },
  cardBody: {
    padding: '1.25rem',
    display: 'flex',
    flexDirection: 'column',
    flex: 1
  },
  cardTitle: {
    fontFamily: 'Rubik, sans-serif',
    fontSize: '1.15rem',
    fontWeight: 700,
    color: '#ffffff',
    marginBottom: '0.4rem',
    lineHeight: 1.35
  },
  cardDirector: {
    fontSize: '0.82rem',
    color: '#a0a0a0',
    marginBottom: '0.75rem',
    display: 'flex',
    alignItems: 'center',
    gap: '6px'
  },
  cardDesc: {
    fontSize: '0.85rem',
    color: '#8c8f99',
    lineHeight: 1.5,
    marginBottom: '1.2rem',
    flex: 1
  },
  cardActions: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    paddingTop: '0.9rem',
    borderTop: '1px solid #23252b',
    marginTop: 'auto'
  },
  btnEdit: {
    flex: 1,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    backgroundColor: '#23252b',
    border: '1px solid #32353e',
    color: '#ffffff',
    padding: '8px 12px',
    borderRadius: '4px',
    fontFamily: 'Rubik, sans-serif',
    fontSize: '0.82rem',
    fontWeight: 600,
    cursor: 'pointer',
    textTransform: 'uppercase'
  },
  btnDelete: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#23252b',
    border: '1px solid #32353e',
    color: '#a0a0a0',
    padding: '8px 12px',
    borderRadius: '4px',
    cursor: 'pointer'
  }
}

export default CartaoFilme