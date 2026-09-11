import { useState, useEffect } from 'react'
import './App.css'
import CartaoFilme from './components/CartaoFilme'

function App() {
  // 1. A MEMÓRIA (useState): Guarda a lista de filmes que vem do banco de dados
  const [filmes, setFilmes] = useState([])

  // 2. O MENSAGEIRO (useEffect): Vai lá no Render buscar os filmes quando o site abre
  useEffect(() => {
    // ATENÇÃO: Substitua a URL abaixo pelo link do seu servidor no Render!
    // Não esqueça de manter o /filmes no final.
    fetch('https://filmes-e-seriesana.onrender.com/filmes')
      .then(resposta => resposta.json())
      .then(dados => setFilmes(dados))
      .catch(erro => console.error("Erro ao buscar filmes:", erro))
  }, []) // Os colchetes vazios significam: "Faça isso apenas uma vez ao abrir o site"

  return (
    <div>
      <h1>🎬 Meu Catálogo de Filmes</h1>
      <p>Puxando dados reais direto da nuvem!</p>

      {/* 3. A MÁQUINA DE CLONAGEM (.map): Para cada filme no banco, cria uma peça de LEGO */}
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {filmes.length === 0 ? (
          <p>Carregando filmes da nuvem...</p>
        ) : (
          filmes.map((filme) => (
            <CartaoFilme 
              key={filme.id} // O React precisa de um ID único para organizar as peças
              titulo={filme.titulo} 
              diretor={filme.diretor} 
              ano={filme.ano} 
            />
          ))
        )}
      </div>
    </div>
  )
}

export default App