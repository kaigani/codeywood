import { useState } from 'react'
import { Header } from './components/layout/Header'
import { ToastContainer } from './components/layout/Toast'
import { ProjectListPage } from './pages/ProjectListPage'
import { PipelinePage } from './pages/PipelinePage'

export default function App() {
  const [currentSlug, setCurrentSlug] = useState<string | null>(null)

  return (
    <div className="min-h-screen">
      <Header
        projectSlug={currentSlug ?? undefined}
        onBack={() => setCurrentSlug(null)}
      />

      {currentSlug ? (
        <PipelinePage slug={currentSlug} onBack={() => setCurrentSlug(null)} />
      ) : (
        <ProjectListPage onSelectProject={setCurrentSlug} />
      )}

      <ToastContainer />
    </div>
  )
}
