import { useEffect, useState } from 'react'
import { adminPath } from './lazy/path'

export default function Admin() {
  const [coucou, setCoucou] = useState<string | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch(adminPath)
      .then((r) => r.json())
      .then((d) => setCoucou(d.coucou))
      .catch(() => setError(true))
  }, [])

  if (error) return <div className="page"><p>Erreur de chargement.</p></div>
  if (!coucou) return <div className="page"><p>Chargement...</p></div>

  return (
    <div className="page">
      <h1>Zone Admin</h1>
      <p>Acces autorise. Voici le :</p>
      <code className="autre">{coucou}</code>
    </div>
  )
}
