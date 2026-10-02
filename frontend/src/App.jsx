import { useState, useEffect } from 'react'
import './App.css'
import CartaoFilme from './components/CartaoFilme'

function App() {
  // 1. A MEMÓRIA (useState): Guarda a lista de filmes que vem do banco de dados e o texto de busca
  const [filmes, setFilmes] = useState([])
  const [pesquisa, setPesquisa] = useState('')

  // 2. O MENSAGEIRO (useEffect): Vai buscar os filmes quando o site abre
  useEffect(() => {
    const carregarFilmes = async () => {
      try {
        let resposta
        try {
          resposta = await fetch('https://filmes-e-seriesana.onrender.com/filmes')
          if (!resposta.ok) throw new Error('Erro ao buscar do Render')
        } catch {
          resposta = await fetch('http://127.0.0.1:5000/filmes')
        }
        const dados = await resposta.json()
        setFilmes(dados)
      } catch (erro) {
        console.error("Erro ao buscar filmes:", erro)
      }
    }

    carregarFilmes()
  }, []) // Os colchetes vazios significam: "Faça isso apenas uma vez ao abrir o site"

  // Filtra os filmes por título ou descrição conforme o usuário digita na busca
  const filmesFiltrados = filmes.filter((filme) => {
    const termo = pesquisa.toLowerCase().trim()
    const tituloMatch = filme.titulo && filme.titulo.toLowerCase().includes(termo)
    const descMatch = filme.descricao && filme.descricao.toLowerCase().includes(termo)
    const diretorMatch = filme.diretor && filme.diretor.toLowerCase().includes(termo)
    return tituloMatch || descMatch || diretorMatch
  })

  return (
    <div>
      <h1>🎬 Meu Catálogo de Filmes</h1>
      <p>Puxando dados reais direto da nuvem!</p>

      {/* Barra de Pesquisa */}
      <div style={{ maxWidth: '400px', margin: '20px auto 10px auto', padding: '0 10px' }}>
        <input
          type="text"
          placeholder="🔍 Pesquisar por título ou descrição..."
          value={pesquisa}
          onChange={(e) => setPesquisa(e.target.value)}
          style={{
            width: '100%',
            padding: '12px 16px',
            fontSize: '1rem',
            border: '2px solid #8209df',
            borderRadius: '8px',
            outline: 'none',
            boxSizing: 'border-box'
          }}
        />
      </div>

      {/* 3. A MÁQUINA DE CLONAGEM (.map): Para cada filme no banco, cria uma peça de LEGO */}
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {filmes.length === 0 ? (
          <p>Carregando filmes da nuvem...</p>
        ) : filmesFiltrados.length === 0 ? (
          <p>Nenhum filme encontrado para "{pesquisa}".</p>
        ) : (
          filmesFiltrados.map((filme) => (
            <CartaoFilme 
              key={filme.id} // O React precisa de um ID único para organizar as peças
              titulo={filme.titulo} 
              diretor={filme.diretor} 
              ano={filme.ano} 
              descricao={filme.descricao}
            />
          ))
        )}
      </div>
    </div>
  )
}

export default App