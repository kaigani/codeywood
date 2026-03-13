import type { Project, PipelineData, StepOutput } from '../types'

const BASE = '/api'

async function json<T>(url: string, opts?: RequestInit): Promise<T> {
  const resp = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  return resp.json()
}

// Projects
export const listProjects = () => json<Project[]>(`${BASE}/projects`)

export const createProject = (name: string, slug: string) =>
  json<{ slug: string; path: string } | { error: string }>(`${BASE}/projects`, {
    method: 'POST',
    body: JSON.stringify({ name, slug }),
  })

// Pipeline
export const getPipeline = (slug: string) =>
  json<PipelineData>(`${BASE}/projects/${slug}/pipeline`)

export const updateStepStatus = (slug: string, stepId: string, status: string) =>
  json<{ ok: boolean }>(`${BASE}/projects/${slug}/steps/${stepId}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  })

export const getStepPrompt = (slug: string, stepId: string, context: string = '') =>
  json<{ prompt: string }>(`${BASE}/projects/${slug}/steps/${stepId}/prompt?context=${encodeURIComponent(context)}`)

export const getStepOutputs = (slug: string, stepId: string) =>
  json<{ outputs: StepOutput[] }>(`${BASE}/projects/${slug}/steps/${stepId}/outputs`)

// Ingest
export const getIngestFiles = (slug: string) =>
  json<{ files: string[] }>(`${BASE}/projects/${slug}/ingest`)

export const openIngestFolder = (slug: string) =>
  json<{ ok: boolean }>(`${BASE}/projects/${slug}/ingest/open`, {
    method: 'POST',
    body: JSON.stringify({}),
  })

export const copyToIngest = (slug: string, path: string) =>
  json<{ copied: number } | { error: string }>(`${BASE}/projects/${slug}/ingest/copy`, {
    method: 'POST',
    body: JSON.stringify({ path }),
  })

// Assess
export const assessProject = (slug: string) =>
  json<{ pipeline: Record<string, string>; phase: string }>(`${BASE}/projects/${slug}/assess`, { method: 'POST' })

export const assessAll = () =>
  json<Record<string, { pipeline: Record<string, string>; phase: string }>>(`${BASE}/assess-all`, { method: 'POST' })

// Run step (returns Response for SSE streaming)
export const runStep = (slug: string, stepId: string, context: string = '') =>
  fetch(`${BASE}/projects/${slug}/steps/${stepId}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ context }),
  })
