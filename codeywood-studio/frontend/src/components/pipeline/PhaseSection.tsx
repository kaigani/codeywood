import type { Phase } from '../../types'
import { StepRow } from './StepRow'

interface Props {
  phase: Phase
  currentStepId: string | null
  onStepClick: (stepId: string) => void
}

const PHASE_COLORS: Record<string, string> = {
  'pre-production': 'bg-accent-blue',
  'visual-development': 'bg-accent-pink',
  'production': 'bg-accent-gold',
  'post-production': 'bg-accent-green',
  'delivery': 'bg-text-primary',
}

const PHASE_TEXT_COLORS: Record<string, string> = {
  'pre-production': 'text-accent-blue',
  'visual-development': 'text-accent-pink',
  'production': 'text-accent-gold',
  'post-production': 'text-accent-green',
  'delivery': 'text-text-primary',
}

export function PhaseSection({ phase, currentStepId, onStepClick }: Props) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-3 pb-2 border-b-2 border-text-muted">
        <div className={`w-2 h-2 rounded-full ${PHASE_COLORS[phase.id] || 'bg-text-muted'}`} />
        <h3 className={`font-pixel text-[0.5rem] uppercase tracking-[0.15em] ${PHASE_TEXT_COLORS[phase.id] || 'text-text-muted'}`}>
          {phase.label}
        </h3>
      </div>
      {phase.steps.map(step => (
        <StepRow
          key={step.id}
          step={step}
          isCurrent={step.id === currentStepId}
          onClick={() => onStepClick(step.id)}
        />
      ))}
    </div>
  )
}
