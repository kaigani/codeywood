import { useState, useEffect, useRef } from 'react'
import type { Step, StepOutput } from '../../types'
import { getStepPrompt, getStepOutputs, updateStepStatus, runStep as apiRunStep } from '../../api/client'
import { useSSE } from '../../hooks/useSSE'
import { toast } from '../layout/Toast'

interface Props {
  slug: string
  step: Step
  onClose: () => void
  onStatusChange: () => void
}

const STATUS_BADGE: Record<string, string> = {
  pending: 'border-text-muted text-text-muted',
  active: 'border-status-progress text-status-progress',
  complete: 'border-status-complete text-status-complete',
  skipped: 'border-text-muted text-text-muted',
  failed: 'border-status-blocked text-status-blocked',
}

export function StepModal({ slug, step, onClose, onStatusChange }: Props) {
  const [context, setContext] = useState('')
  const [prompt, setPrompt] = useState<string | null>(null)
  const [outputs, setOutputs] = useState<StepOutput[]>([])
  const { lines, isRunning, exitCode, start, clear } = useSSE()
  const outputRef = useRef<HTMLPreElement>(null)

  useEffect(() => {
    getStepOutputs(slug, step.id).then(r => setOutputs(r.outputs))
  }, [slug, step.id])

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [lines])

  useEffect(() => {
    if (exitCode !== null) {
      const status = exitCode === 0 ? 'complete' : 'failed'
      updateStepStatus(slug, step.id, status).then(onStatusChange)
      toast(`Step ${status}`, exitCode === 0 ? 'success' : 'error')
    }
  }, [exitCode, slug, step.id, onStatusChange])

  const handlePreview = async () => {
    const r = await getStepPrompt(slug, step.id, context)
    setPrompt(r.prompt)
  }

  const handleRun = async () => {
    clear()
    const response = await apiRunStep(slug, step.id, context)
    start(response)
  }

  const handleStatus = async (status: string) => {
    await updateStepStatus(slug, step.id, status)
    toast(`${step.name}: ${status}`, 'success')
    onStatusChange()
    onClose()
  }

  return (
    <div className="fixed inset-0 z-[200] flex items-start justify-center pt-16">
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-[90%] max-w-2xl max-h-[80vh] bg-bg-card pixel-border-gold overflow-y-auto">

        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-bg-card border-b-4 border-text-muted">
          <h3 className="font-pixel text-[0.7rem] text-accent-gold">{step.name}</h3>
          <button onClick={onClose} className="text-text-muted hover:text-accent-gold text-2xl leading-none">&times;</button>
        </div>

        {/* Body */}
        <div className="p-6">
          {/* Meta */}
          <div className="flex gap-2 flex-wrap mb-4">
            <span className={`font-pixel text-[0.35rem] px-2 py-1 border-2 uppercase tracking-wider ${STATUS_BADGE[step.status]}`}>
              {step.status}
            </span>
            {step.gate && (
              <span className="font-pixel text-[0.35rem] px-2 py-1 border-2 border-accent-purple text-accent-purple uppercase">
                Gate {step.gate.split('_')[1]}
              </span>
            )}
            {step.skill && (
              <span className="font-pixel text-[0.35rem] px-2 py-1 border-2 border-accent-blue text-accent-blue uppercase">
                {step.skill}
              </span>
            )}
          </div>

          <p className="text-text-secondary mb-6">{step.description}</p>

          {/* Context input */}
          <div className="mb-6">
            <label className="font-pixel text-[0.4rem] text-text-muted uppercase tracking-[0.1em] mb-2 block">
              Additional Context
            </label>
            <textarea
              value={context}
              onChange={e => setContext(e.target.value)}
              rows={3}
              placeholder="Optional: specific instructions, scenes to focus on..."
              className="w-full px-4 py-3 bg-bg-darker border-4 border-text-muted text-text-primary font-terminal text-base focus:border-accent-gold focus:outline-none transition-colors resize-y"
            />
          </div>

          {/* Actions */}
          <div className="flex gap-2 flex-wrap mb-6">
            {(step.status === 'pending' || step.status === 'failed') && (
              <>
                <ActionBtn onClick={handlePreview} color="gold">Preview Prompt</ActionBtn>
                <ActionBtn onClick={handleRun} color="green" disabled={isRunning}>
                  {isRunning ? 'Running...' : 'Run with Claude'}
                </ActionBtn>
                <ActionBtn onClick={() => handleStatus('skipped')} color="muted">Skip</ActionBtn>
                <ActionBtn onClick={() => handleStatus('complete')} color="muted">Mark Complete</ActionBtn>
              </>
            )}
            {step.status === 'active' && (
              <>
                <ActionBtn onClick={() => handleStatus('complete')} color="green">Mark Complete</ActionBtn>
                <ActionBtn onClick={() => handleStatus('failed')} color="red">Mark Failed</ActionBtn>
                <ActionBtn onClick={handleRun} color="gold" disabled={isRunning}>Re-run</ActionBtn>
              </>
            )}
            {step.status === 'complete' && (
              <>
                <ActionBtn onClick={handlePreview} color="gold">Preview Prompt</ActionBtn>
                <ActionBtn onClick={handleRun} color="muted" disabled={isRunning}>Re-run</ActionBtn>
                <ActionBtn onClick={() => handleStatus('pending')} color="muted">Reset</ActionBtn>
              </>
            )}
            {step.status === 'skipped' && (
              <>
                <ActionBtn onClick={() => handleStatus('pending')} color="gold">Unskip</ActionBtn>
                <ActionBtn onClick={handleRun} color="muted" disabled={isRunning}>Run Anyway</ActionBtn>
              </>
            )}
          </div>

          {/* Prompt preview */}
          {prompt && (
            <div className="mb-6 border-t-2 border-text-muted pt-4">
              <h4 className="font-pixel text-[0.4rem] text-text-muted uppercase tracking-[0.1em] mb-3">Claude Prompt</h4>
              <pre className="bg-bg-darker pixel-border p-4 font-mono text-xs leading-relaxed text-text-secondary whitespace-pre-wrap break-words max-h-60 overflow-y-auto">
                {prompt}
              </pre>
            </div>
          )}

          {/* Claude output */}
          {lines.length > 0 && (
            <div className="mb-6 border-t-2 border-text-muted pt-4">
              <h4 className="font-pixel text-[0.4rem] text-text-muted uppercase tracking-[0.1em] mb-3">
                Claude Output {isRunning && <span className="text-status-progress animate-pulse">RUNNING</span>}
              </h4>
              <pre
                ref={outputRef}
                className="bg-bg-darker pixel-border p-4 font-mono text-xs leading-relaxed text-text-secondary whitespace-pre-wrap break-words max-h-72 overflow-y-auto"
              >
                {lines.join('')}
                {exitCode !== null && (
                  <span className={exitCode === 0 ? 'text-status-complete' : 'text-status-blocked'}>
                    {`\n--- ${exitCode === 0 ? 'COMPLETE' : 'FAILED'} (exit ${exitCode}) ---\n`}
                  </span>
                )}
              </pre>
            </div>
          )}

          {/* Outputs */}
          {outputs.length > 0 && (
            <div className="border-t-2 border-text-muted pt-4">
              <h4 className="font-pixel text-[0.4rem] text-text-muted uppercase tracking-[0.1em] mb-3">Outputs</h4>
              {outputs.map((o, i) => (
                <div key={i} className="flex items-center gap-2 py-1 text-sm">
                  <span className="text-status-complete">{o.type === 'file' ? '\u2713' : '\u{1F4C1}'}</span>
                  <span className="font-mono text-xs text-text-secondary">{o.path}{o.type === 'directory' && '/'}</span>
                  <span className="text-text-muted text-xs">
                    {o.type === 'file' && o.size != null ? formatSize(o.size) : `${o.count} files`}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ActionBtn({ onClick, color, disabled, children }: {
  onClick: () => void
  color: 'gold' | 'green' | 'red' | 'muted'
  disabled?: boolean
  children: React.ReactNode
}) {
  const colors = {
    gold: 'border-accent-gold text-accent-gold hover:bg-accent-gold hover:text-bg-dark',
    green: 'border-accent-green text-accent-green hover:bg-accent-green hover:text-bg-dark',
    red: 'border-accent-red text-accent-red hover:bg-accent-red hover:text-white',
    muted: 'border-text-muted text-text-muted hover:border-accent-gold hover:text-accent-gold',
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`font-pixel text-[0.4rem] px-3 py-2 border-2 uppercase tracking-wider transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed ${colors[color]}`}
    >
      {children}
    </button>
  )
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
