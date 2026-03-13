import type { Step } from '../../types'

interface Props {
  step: Step
  isCurrent: boolean
  onClick: () => void
}

const STATUS_SYMBOLS: Record<string, string> = {
  pending: '[ ]',
  active: '[~]',
  complete: '[x]',
  skipped: '[-]',
  failed: '[!]',
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'text-text-muted',
  active: 'text-status-progress',
  complete: 'text-status-complete',
  skipped: 'text-text-muted opacity-50',
  failed: 'text-status-blocked',
}

export function StepRow({ step, isCurrent, onClick }: Props) {
  return (
    <div
      className={`flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-all hover:bg-bg-card-hover ${
        isCurrent ? 'bg-bg-card border-l-4 border-l-accent-gold' : 'border-l-4 border-l-transparent'
      }`}
      onClick={onClick}
    >
      <span className={`font-mono text-sm w-8 shrink-0 ${STATUS_COLORS[step.status]}`}>
        {STATUS_SYMBOLS[step.status]}
      </span>
      <div className="flex-1 min-w-0">
        <div className={`text-base ${step.status === 'skipped' ? 'text-text-muted line-through' : 'text-text-primary'}`}>
          {step.name}
        </div>
        <div className="text-sm text-text-muted truncate">{step.description}</div>
      </div>
      {step.gate && (
        <span className="font-pixel text-[0.35rem] px-2 py-1 border-2 border-text-muted text-text-muted uppercase tracking-wider shrink-0">
          Gate {step.gate.split('_')[1]}
        </span>
      )}
    </div>
  )
}
