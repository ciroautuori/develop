import './shared/utils/dom-patch' // MUST BE FIRST IMPORT
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { initConsoleFilter } from './shared/utils/console-filter'

// Filtra errori CORS noti di Google (play.google.com/log)
// Questi errori NON sono bug ma comportamento delle librerie Google
initConsoleFilter()

// Render app only when DOM is fully ready (fixes framer-motion init error)
function renderApp() {
  const root = document.getElementById('root')
  if (root) {
    ReactDOM.createRoot(root).render(<App />)
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', renderApp)
} else {
  renderApp()
}
