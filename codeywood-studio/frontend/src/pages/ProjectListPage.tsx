import { useEffect, useState } from 'react'
import type { Project } from '../types'
import { listProjects, assessAll } from '../api/client'
import { ProjectCard } from '../components/project/ProjectCard'
import { NewProjectForm } from '../components/project/NewProjectForm'
import { toast } from '../components/layout/Toast'

interface Props {
  onSelectProject: (slug: string) => void
}

export function ProjectListPage({ onSelectProject }: Props) {
  const [projects, setProjects] = useState<Project[]>([])
  const [showNew, setShowNew] = useState(false)
  const [assessing, setAssessing] = useState(false)

  const load = async () => {
    const data = await listProjects()
    setProjects(data)
  }

  useEffect(() => { load() }, [])

  if (showNew) {
    return (
      <div className="p-8 max-w-5xl mx-auto">
        <NewProjectForm
          onCreated={(slug) => {
            setShowNew(false)
            onSelectProject(slug)
          }}
          onCancel={() => setShowNew(false)}
        />
      </div>
    )
  }

  // Stats
  const total = projects.length
  const active = projects.filter(p => p.progress.percent > 0 && p.progress.percent < 100).length

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <h2 className="font-pixel text-[0.875rem] text-text-primary">
          <span className="text-accent-gold">[</span> PROJECTS <span className="text-accent-gold">]</span>
        </h2>
        <div className="flex gap-3">
          <button
            onClick={async () => {
              setAssessing(true)
              await assessAll()
              await load()
              setAssessing(false)
              toast('All projects assessed', 'success')
            }}
            disabled={assessing}
            className="pixel-border border-accent-blue! bg-bg-card text-accent-blue font-pixel text-[0.45rem] px-4 py-2 hover:bg-accent-blue hover:text-bg-dark transition-all cursor-pointer uppercase tracking-[0.1em] disabled:opacity-40"
          >
            {assessing ? 'Scanning...' : 'Assess All'}
          </button>
          <button
            onClick={() => setShowNew(true)}
            className="pixel-border border-accent-gold! bg-bg-card text-accent-gold font-pixel text-[0.45rem] px-4 py-2 hover:bg-accent-gold hover:text-bg-dark transition-all cursor-pointer uppercase tracking-[0.1em]"
          >
            + New Project
          </button>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <StatCard value={total} label="Total" />
        <StatCard value={active} label="Active" />
        <StatCard value={projects.filter(p => p.progress.percent === 100).length} label="Complete" />
        <StatCard value={projects.filter(p => p.progress.percent === 0).length} label="Not Started" />
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map(p => (
          <ProjectCard key={p.slug} project={p} onClick={() => onSelectProject(p.slug)} />
        ))}
      </div>
    </div>
  )
}

function StatCard({ value, label }: { value: number; label: string }) {
  return (
    <div className="pixel-border bg-bg-card p-4 text-center">
      <span className="font-pixel text-xl text-accent-gold block mb-1">{value}</span>
      <span className="text-xs text-text-muted uppercase tracking-wider">{label}</span>
    </div>
  )
}
