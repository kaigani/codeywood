interface HeaderProps {
  projectSlug?: string
  onBack?: () => void
}

export function Header({ projectSlug, onBack }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-6 py-4 bg-bg-sidebar border-b-4 border-accent-gold-dim">
      <div className="flex items-center gap-4">
        <h1
          className="font-pixel text-[0.75rem] text-accent-gold glow-gold cursor-pointer hover:text-accent-blue transition-colors"
          onClick={onBack}
        >
          CODEYWOOD STUDIO
        </h1>
      </div>
      <div className="flex items-center gap-3">
        {projectSlug && (
          <span className="font-pixel text-[0.45rem] px-3 py-1 border-2 border-accent-blue text-accent-blue uppercase tracking-wider">
            {projectSlug}
          </span>
        )}
      </div>
    </header>
  )
}
