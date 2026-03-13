import type { Project } from '../../types'

interface Props {
  project: Project
  onClick: () => void
}

export function ProjectCard({ project, onClick }: Props) {
  return (
    <div
      className="pixel-border bg-bg-card p-6 cursor-pointer transition-all hover:border-accent-gold hover:-translate-y-0.5"
      onClick={onClick}
    >
      <h3 className="font-pixel text-[0.7rem] text-accent-gold mb-2">{project.name}</h3>
      <div className="font-pixel text-[0.4rem] text-text-muted uppercase tracking-[0.15em] mb-4">
        {project.phase.replace(/-/g, ' ')}
      </div>
      <div className="text-sm text-text-secondary mb-4">
        Next: <span className="text-accent-gold">{project.current_step_name}</span>
      </div>

      {/* Progress bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-3 bg-bg-darker border-2 border-text-muted overflow-hidden">
          <div
            className="h-full progress-fill-striped transition-[width] duration-500"
            style={{ width: `${project.progress.percent}%` }}
          />
        </div>
        <span className="font-pixel text-[0.5rem] text-accent-gold min-w-[2.5em] text-right">
          {project.progress.percent}%
        </span>
      </div>
    </div>
  )
}
