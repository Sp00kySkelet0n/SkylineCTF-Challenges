import { useLocation, Navigate } from 'react-router-dom'
import { getPlaceholder, getPadding } from './lazy/prefix'
import { adminPath } from './lazy/path'
import Admin from './Admin'
import { formatError, getDataSlice } from './lazy/suffix'
void getPlaceholder(0)
void getPadding()
void formatError('E000')
void getDataSlice(0, 1)

export default function AdminRoute() {
  const { pathname } = useLocation()
  if (pathname !== adminPath) return <Navigate to="/" replace />
  return <Admin />
}
