import { useEffect, useState, useCallback } from 'react'
import type { PipelineData, Step } from '../types'
import { getPipeline } from '../api/client'
import { PhaseSection } from '../components/pipeline/PhaseSection'
import { StepModal } from '../components/pipeline/StepModal'

interface Props {
  slug: string
  onBack: () => void
}

export function PipelinePage({ slug, onBack }: Props) {
  const [data, setData] = useState<PipelineData | null>(null)
  const [selectedStep, setSelectedStep] = useState<Step | null>(null)

  const load = useCallback(async () => {
    const pipeline = await getPipeline(slug)
    setData(pipeline)
  }, [slug])

  useEffect(() => { load() }, [load])

  if (!data) {
    return <div className="p-8 text-text-muted">Loading...</div>
  }

  const handleStepClick = (stepId: string) => {
    for (const phase of data.phases) {
      const step = phase.steps.find(s => s.id === stepId)
      if (step) {
        setSelectedStep(step)
        return
      }
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="font-pixel text-[0.875rem] text-accent-gold glow-gold mb-2">
            {data.project.name}
          </h2>
          {/* Progress */}
          <div className="flex items-center gap-3">
            <div className="w-48 h-4 bg-bg-darker border-2 border-text-muted overflow-hidden">
              <div
                className="h-full progress-fill-striped transition-[width] duration-500"
                style={{ width: `${data.progress.percent}%` }}
              />
            </div>
            <span className="font-pixel text-[0.5rem] text-accent-gold">
              {data.progress.percent}%
            </span>
            <span className="text-xs text-text-muted">
              {data.progress.complete}/{data.progress.total} complete
              {data.progress.skipped > 0 && ` (${data.progress.skipped} skipped)`}
            </span>
          </div>
        </div>
        <button
          onClick={onBack}
          className="font-pixel text-[0.4rem] text-text-muted hover:text-accent-gold transition-colors"
        >
          ALL PROJECTS
        </button>
      </div>

      {/* Phases */}
      {data.phases.map(phase => (
        <PhaseSection
          key={phase.id}
          phase={phase}
          currentStepId={data.current_step}
          onStepClick={handleStepClick}
        />
      ))}

      {/* Step modal */}
      {selectedStep && (
        <StepModal
          slug={slug}
          step={selectedStep}
          onClose={() => setSelectedStep(null)}
          onStatusChange={() => {
            load()
            setSelectedStep(null)
          }}
        />
      )}
    </div>
  )
}
