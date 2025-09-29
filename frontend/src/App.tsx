import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Layout from './components/Layout.tsx'
import Dashboard from './pages/Dashboard.tsx'
import Documents from './pages/Documents.tsx'
import Chat from './pages/Chat.tsx'
import Analytics from './pages/Analytics.tsx'
import Settings from './pages/Settings.tsx'

function App() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen bg-secondary-950"
    >
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </motion.div>
  )
}

export default App