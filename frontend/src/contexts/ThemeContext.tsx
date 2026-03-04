import { createContext, useContext, useState, useMemo, type ReactNode } from 'react'
import { ThemeProvider as MuiThemeProvider, CssBaseline } from '@mui/material'
import { buildTheme } from '../theme'

type ThemeMode = 'light' | 'dark'

interface ThemeContextValue {
    mode: ThemeMode
    toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

export function useThemeMode() {
    const ctx = useContext(ThemeContext)
    if (!ctx) throw new Error('useThemeMode must be used within AppThemeProvider')
    return ctx
}

export function AppThemeProvider({ children }: { children: ReactNode }) {
    const [mode, setMode] = useState<ThemeMode>(() => {
        const stored = localStorage.getItem('themeMode')
        return stored === 'dark' ? 'dark' : 'light'
    })

    const toggleTheme = () => {
        setMode((prev) => {
            const next = prev === 'light' ? 'dark' : 'light'
            localStorage.setItem('themeMode', next)
            return next
        })
    }

    const theme = useMemo(() => buildTheme(mode), [mode])

    return (
        <ThemeContext.Provider value={{ mode, toggleTheme }}>
            <MuiThemeProvider theme={theme}>
                <CssBaseline />
                {children}
            </MuiThemeProvider>
        </ThemeContext.Provider>
    )
}
