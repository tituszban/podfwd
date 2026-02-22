import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { EmailView } from './pages/EmailView'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/email" replace />} />
        <Route path="email" element={<EmailView />} />
        <Route path="email/:emailId" element={<EmailView />} />
      </Route>
    </Routes>
  )
}

export default App
