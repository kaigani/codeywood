import { useState } from 'react'
import { createProject } from '../../api/client'
import { toast } from '../layout/Toast'

interface Props {
  onCreated: (slug: string) => void
  onCancel: () => void
}

export function NewProjectForm({ onCreated, onCancel }: Props) {
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')

  const autoSlug = (val: string) => {
    setName(val)
    setSlug(val.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await createProject(name, slug)
    if ('error' in result) {
      toast(result.error, 'error')
      return
    }
    toast(`Created: ${name}`, 'success')
    onCreated(result.slug)
  }

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-4 mb-8">
        <h2 className="font-pixel text-[0.875rem] text-text-primary">
          <span className="text-accent-gold">[</span> NEW PROJECT <span className="text-accent-gold">]</span>
        </h2>
        <button onClick={onCancel} className="font-pixel text-[0.4rem] text-text-muted hover:text-accent-gold transition-colors">
          CANCEL
        </button>
      </div>

      <form onSubmit={handleSubmit} className="pixel-border bg-bg-card p-8 flex flex-col gap-6">
        <div>
          <label className="font-pixel text-[0.4rem] text-text-muted uppercase tracking-[0.1em] mb-2 block">
            Project Name
          </label>
          <input
            type="text"
            value={name}
            onChange={e => autoSlug(e.target.value)}
            placeholder="My New Story"
            required
            className="w-full px-4 py-3 bg-bg-darker border-4 border-text-muted text-text-primary font-terminal text-lg focus:border-accent-gold focus:outline-none transition-colors"
          />
        </div>
        <div>
          <label className="font-pixel text-[0.4rem] text-text-muted uppercase tracking-[0.1em] mb-2 block">
            Slug
          </label>
          <input
            type="text"
            value={slug}
            onChange={e => setSlug(e.target.value)}
            placeholder="my-new-story"
            required
            className="w-full px-4 py-3 bg-bg-darker border-4 border-text-muted text-text-primary font-mono text-sm focus:border-accent-gold focus:outline-none transition-colors"
          />
        </div>
        <button
          type="submit"
          className="pixel-border border-accent-gold! bg-bg-card text-accent-gold font-pixel text-[0.5rem] px-6 py-3 hover:bg-accent-gold hover:text-bg-dark transition-all cursor-pointer uppercase tracking-[0.1em]"
        >
          Create Project
        </button>
      </form>
    </div>
  )
}
