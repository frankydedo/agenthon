import { useEffect, useState } from 'react'
import type { Passo } from './api'

/** Segue la traccia di una richiesta in diretta (Server-Sent Events). */
export function usePassi(id: string | null): Passo[] {
  const [passi, setPassi] = useState<Passo[]>([])
  useEffect(() => {
    setPassi([])
    if (!id) return
    const es = new EventSource(`/api/richieste/${id}/stream`)
    es.addEventListener('reset', () => setPassi([]))
    es.addEventListener('passo', (e) => setPassi((p) => [...p, JSON.parse((e as MessageEvent).data)]))
    return () => es.close()
  }, [id])
  return passi
}
