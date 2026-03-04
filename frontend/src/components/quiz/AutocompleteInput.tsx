import React, { useState, useEffect, useRef, useCallback } from 'react'
import {
    Box,
    TextField,
    Paper,
    List,
    ListItemButton,
    ListItemText,
    CircularProgress,
} from '@mui/material'
import { fetchAutocomplete } from '../../api/flagQuiz'
import type { QuizFilters } from '../../types'

interface Props {
    filters: QuizFilters
    onSubmit: (value: string) => void
    disabled?: boolean
    autoFocus?: boolean
}

export default function AutocompleteInput({ filters, onSubmit, disabled = false, autoFocus = true }: Props) {
    const [value, setValue] = useState('')
    const [suggestions, setSuggestions] = useState<string[]>([])
    const [selectedIndex, setSelectedIndex] = useState(0)
    const [open, setOpen] = useState(false)
    const [loading, setLoading] = useState(false)
    const inputRef = useRef<HTMLInputElement>(null)
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    // Auto-focus when enabled
    useEffect(() => {
        if (autoFocus && !disabled) {
            inputRef.current?.focus()
        }
    }, [autoFocus, disabled])

    // Debounced autocomplete fetch
    useEffect(() => {
        if (debounceRef.current) clearTimeout(debounceRef.current)

        if (!value || value.length < 1) {
            setSuggestions([])
            setOpen(false)
            return
        }

        debounceRef.current = setTimeout(async () => {
            setLoading(true)
            try {
                const results = await fetchAutocomplete(value, filters, 8)
                setSuggestions(results)
                setSelectedIndex(0)
                setOpen(results.length > 0)
            } catch {
                setSuggestions([])
                setOpen(false)
            } finally {
                setLoading(false)
            }
        }, 0)

        return () => {
            if (debounceRef.current) clearTimeout(debounceRef.current)
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [value])

    const acceptSuggestion = useCallback(
        (suggestion: string) => {
            setValue(suggestion)
            setSuggestions([])
            setOpen(false)
            inputRef.current?.focus()
        },
        []
    )

    const handleSubmit = useCallback(
        (submitValue: string) => {
            const trimmed = submitValue.trim()
            if (!trimmed) return
            setSuggestions([])
            setOpen(false)
            setValue('')
            onSubmit(trimmed)
        },
        [onSubmit]
    )

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Tab') {
            e.preventDefault()
            if (open && suggestions.length > 0) {
                const suggestion = suggestions[selectedIndex] ?? suggestions[0]
                handleSubmit(suggestion)
            }
            return
        }

        if (e.key === 'Enter') {
            e.preventDefault()
            if (open && suggestions.length > 0 && value !== suggestions[selectedIndex]) {
                // If user hasn't typed the full name, accept the suggestion first
                // (only if it unambiguously matches what they typed)
                // Otherwise submit what they typed
            }
            handleSubmit(value)
            return
        }

        if (e.key === 'ArrowDown') {
            e.preventDefault()
            setSelectedIndex((i) => Math.min(i + 1, suggestions.length - 1))
            return
        }

        if (e.key === 'ArrowUp') {
            e.preventDefault()
            setSelectedIndex((i) => Math.max(i - 1, 0))
            return
        }

        if (e.key === 'Escape') {
            setSuggestions([])
            setOpen(false)
        }
    }

    return (
        <Box sx={{ position: 'relative', width: '100%', maxWidth: 480 }}>
            <TextField
                inputRef={inputRef}
                fullWidth
                variant="outlined"
                placeholder="Type country name…"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="off"
                spellCheck={false}
                InputProps={{
                    endAdornment: loading ? (
                        <CircularProgress size={18} sx={{ mr: 1 }} />
                    ) : null,
                    sx: { fontSize: '1.1rem' },
                }}
            />

            {open && suggestions.length > 0 && (
                <Paper
                    elevation={0}
                    sx={{
                        position: 'absolute',
                        top: '100%',
                        left: 0,
                        right: 0,
                        zIndex: 1300,
                        maxHeight: 280,
                        overflowY: 'auto',
                        mt: 0.5,
                        borderRadius: 3,
                        border: (theme) => `1px solid ${theme.palette.divider}`,
                        backdropFilter: 'blur(16px)',
                        bgcolor: (theme) =>
                            theme.palette.mode === 'dark'
                                ? 'rgba(26,29,46,0.95)'
                                : 'rgba(255,255,255,0.95)',
                        boxShadow: (theme) =>
                            theme.palette.mode === 'dark'
                                ? '0 8px 32px rgba(0,0,0,0.4)'
                                : '0 8px 32px rgba(0,0,0,0.12)',
                    }}
                >
                    <List dense disablePadding>
                        {suggestions.map((s, i) => (
                            <ListItemButton
                                key={s}
                                selected={i === selectedIndex}
                                onMouseDown={(e) => {
                                    e.preventDefault() // prevent blur before click
                                    acceptSuggestion(s)
                                }}
                                sx={{
                                    '&.Mui-selected': {
                                        bgcolor: 'primary.main',
                                        color: 'primary.contrastText',
                                        '&:hover': { bgcolor: 'primary.dark' },
                                    },
                                }}
                            >
                                <ListItemText primary={s} />
                            </ListItemButton>
                        ))}
                    </List>
                </Paper>
            )}
        </Box>
    )
}
