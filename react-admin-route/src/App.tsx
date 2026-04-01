import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Home } from './pages/Home'
import './App.css'

const AdminRoute = lazy(() => import('./pages/AdminRoute'))

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="page"><p>Chargement...</p></div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="*" element={<AdminRoute />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
