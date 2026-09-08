import { useEffect, useMemo, useRef, useState } from 'react'
import { Autocomplete, TextField } from '@mui/material'
import { normalizeForComparison } from '../../hooks/useQuizReducer'

interface Props {
    /** Every acceptable answer in the current pool, plus aliases. */
    options: string[]
    onSubmit: (value: string) => void
    disabled?: boolean
    autoFocus?: boolean
}

const MAX_SUGGESTIONS = 8

/**
 * Rank matches: exact, then prefix, then word-boundary, then substring.
 *
 * Ported from the backend's _prioritize_matches. Suggestions are computed from
 * the catalog already in memory rather than fetched — the previous version made
 * one uncached request per keystroke.
 */
function rank(query: string, items: string[]): string[] {
    const q = normalizeForComparison(query)
    if (!q) return []

    const exact: string[] = []
    const prefix: string[] = []
    const word: string[] = []
    const substring: string[] = []

    for (const item of items) {
        const n = normalizeForComparison(item)
        if (n === q) exact.push(item)
        else if (n.startsWith(q)) prefix.push(item)
        else if (n.split(' ').some((w) => w.startsWith(q))) word.push(item)
        else if (n.includes(q)) substring.push(item)
    }

    const sort = (a: string[]) => a.sort((x, y) => x.localeCompare(y))
    return [...sort(exact), ...sort(prefix), ...sort(word), ...sort(substring)]
}

export default function AutocompleteInput({
    options,
    onSubmit,
    disabled = false,
    autoFocus = true,
}: Props) {
    const [value, setValue] = useState('')
    const [highlighted, setHighlighted] = useState<string | null>(null)
    const inputRef = useRef<HTMLInputElement>(null)

    // Re-focus when the feedback overlay releases the input.
    useEffect(() => {
        if (autoFocus && !disabled) inputRef.current?.focus()
    }, [autoFocus, disabled])

    const submit = (v: string) => {
        const trimmed = v.trim()
        if (!trimmed || disabled) return
        setValue('')
        setHighlighted(null)
        onSubmit(trimmed)
    }

    const filterOptions = useMemo(
        () => (opts: string[], { inputValue }: { inputValue: string }) =>
            rank(inputValue, opts).slice(0, MAX_SUGGESTIONS),
        []
    )

    return (
        <Autocomplete
            freeSolo
            autoHighlight
            disabled={disabled}
            options={options}
            filterOptions={filterOptions}
            inputValue={value}
            onInputChange={(_, v, reason) => {
                if (reason !== 'reset') setValue(v)
            }}
            // Selecting the highlighted option submits it directly. The old
            // hand-rolled version submitted the typed text instead, ignoring
            // whatever the arrow keys had highlighted.
            onChange={(_, v, reason) => {
                if (reason === 'selectOption' && typeof v === 'string') submit(v)
            }}
            onHighlightChange={(_, option) => setHighlighted(typeof option === 'string' ? option : null)}
            sx={{ width: '100%', maxWidth: 480 }}
            renderInput={(params) => (
                <TextField
                    {...params}
                    inputRef={inputRef}
                    placeholder="Type the country name…"
                    autoComplete="off"
                    onKeyDown={(e) => {
                        // Enter with nothing highlighted submits what was typed;
                        // MUI handles the highlighted case via onChange above.
                        if (e.key === 'Enter' && !(e.target as HTMLInputElement).getAttribute('aria-activedescendant')) {
                            e.preventDefault()
                            submit(value)
                        } else if (e.key === 'Tab') {
                            // Tab doesn't natively confirm an Autocomplete's highlighted
                            // option (that's Enter); wire it up explicitly rather than
                            // rely on autoSelect+blur, which would also fire on any
                            // unrelated focus loss (window switch, clicking elsewhere).
                            e.preventDefault()
                            submit(highlighted ?? value)
                        }
                    }}
                />
            )}
        />
    )
}
