export interface Progress {
  total: number
  complete: number
  skipped: number
  percent: number
}

export interface Project {
  slug: string
  name: string
  phase: string
  current_step: string | null
  current_step_name: string
  progress: Progress
}

export interface Step {
  id: string
  name: string
  description: string
  gate: string | null
  skill: string | null
  status: 'pending' | 'active' | 'complete' | 'skipped' | 'failed'
}

export interface Phase {
  id: string
  label: string
  color: string
  steps: Step[]
}

export interface PipelineData {
  project: {
    name: string
    slug: string
    phase: string
  }
  phases: Phase[]
  current_step: string | null
  progress: Progress
}

export interface StepOutput {
  path: string
  type: 'file' | 'directory'
  size?: number
  count?: number
  files?: string[]
}

export type SSEEvent =
  | { type: 'output'; text: string }
  | { type: 'done'; exit_code: number }
  | { type: 'error'; text: string }
