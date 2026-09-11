import React from 'react';

// Esta é a nossa "máquina de fazer cartões".
// Ela recebe "props" (propriedades), que são como as informações do filme.
function CartaoFilme(props) {
  return (
    // Reparou? No React, usamos "className" em vez de "class"!
    <div style={estiloCartao}>
      <h3 style={estiloTitulo}>{props.titulo}</h3>
      <p style={estiloDetalhe}><strong>Diretor:</strong> {props.diretor}</p>
      <p style={estiloDetalhe}><strong>Ano:</strong> {props.ano}</p>
    </div>
  );
}

// -- UM POUCO DE ESTILO RÁPIDO SÓ PARA VERMOS DIFERENTE --
const estiloCartao = {
  border: '2px solid #646cff', // O roxo do React
  borderRadius: '12px',
  padding: '1.5rem',
  margin: '1rem',
  backgroundColor: '#f9f9f9',
  boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
  maxWidth: '300px'
}

const estiloTitulo = {
  color: '#213547',
  marginTop: '0',
  marginBottom: '0.5rem',
  fontSize: '1.5rem',
}

const estiloDetalhe = {
  margin: '0.2rem 0',
  color: '#555',
}
// -----------------------------------------------------

export default CartaoFilme;