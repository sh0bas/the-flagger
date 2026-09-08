import { createTheme } from '@mui/material/styles'
import type { PaletteMode } from '@mui/material'

export function buildTheme(mode: PaletteMode) {
    const isDark = mode === 'dark'

    return createTheme({
        palette: {
            mode,
            primary: {
                main: isDark ? '#2A2F37' : '#20242B',
                light: isDark ? '#3F4550' : '#343940',
                dark: isDark ? '#1B1F24' : '#121417',
            },
            secondary: {
                main: '#42C281',
                light: '#6ED6A1',
                dark: '#2FA06A',
            },
            success: {
                main: '#42C281',
                light: '#6ED6A1',
                dark: '#2FA06A',
            },
            error: {
                main: '#ef4444',
                light: '#f87171',
                dark: '#dc2626',
            },
            warning: {
                main: '#f59e0b',
                light: '#fbbf24',
                dark: '#d97706',
            },
            background: {
                default: isDark ? '#0f1117' : '#f4f6fb',
                paper: isDark ? '#1a1d2e' : '#ffffff',
            },
            text: {
                primary: isDark ? '#e2e8f0' : '#0f172a',
                secondary: isDark ? '#94a3b8' : '#64748b',
            },
            divider: isDark ? 'rgba(148, 163, 184, 0.12)' : 'rgba(15, 23, 42, 0.08)',
        },
        typography: {
            // ponytail: system stack, not a webfont. Nothing here ships Inter, so naming it
            // just cost a fallback hop. Add @fontsource/inter if the brand needs it.
            fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
            h1: { fontWeight: 800, letterSpacing: '-0.02em' },
            h2: { fontWeight: 700, letterSpacing: '-0.01em' },
            h3: { fontWeight: 700 },
            h4: { fontWeight: 700 },
            h5: { fontWeight: 600 },
            h6: { fontWeight: 600 },
            button: {
                textTransform: 'none',
                fontWeight: 600,
            },
        },
        shape: {
            borderRadius: 12,
        },
        components: {
            MuiCssBaseline: {
                styleOverrides: {
                    body: {
                        transition: 'background-color 0.3s ease, color 0.3s ease',
                        // Always reserve scrollbar width to prevent layout shift when
                        // dropdown content makes the page taller than the viewport.
                        overflowY: 'scroll',
                    },
                    // Honour the OS reduce-motion setting for every MUI Fade,
                    // hover transform and transition in one place.
                    '@media (prefers-reduced-motion: reduce)': {
                        '*, *::before, *::after': {
                            animationDuration: '0.01ms !important',
                            transitionDuration: '0.01ms !important',
                            scrollBehavior: 'auto !important',
                        },
                    },
                    '*::-webkit-scrollbar': { width: 8 },
                    '*::-webkit-scrollbar-track': { background: 'transparent' },
                    '*::-webkit-scrollbar-thumb': {
                        background: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.15)',
                        borderRadius: 4,
                    },
                },
            },
            MuiAppBar: {
                styleOverrides: {
                    root: {
                        backgroundImage: 'none',
                        backgroundColor: isDark ? 'rgba(15, 17, 23, 0.85)' : 'rgba(255, 255, 255, 0.85)',
                        backdropFilter: 'blur(16px)',
                        borderBottom: `1px solid ${isDark ? 'rgba(148, 163, 184, 0.12)' : 'rgba(15, 23, 42, 0.08)'}`,
                        color: isDark ? '#e2e8f0' : '#0f172a',
                        boxShadow: 'none',
                    },
                },
            },
            MuiButton: {
                styleOverrides: {
                    root: {
                        borderRadius: 10,
                        padding: '10px 24px',
                        fontWeight: 600,
                        textTransform: 'none' as const,
                        transition: 'all 0.2s ease',
                        '&:active': {
                            transform: 'scale(0.98)',
                        },
                    },
                    contained: {
                        boxShadow: '0 2px 8px rgba(66, 194, 129, 0.25)',
                        '&:hover': {
                            boxShadow: '0 4px 16px rgba(66, 194, 129, 0.35)',
                            transform: 'translateY(-1px)',
                        },
                    },
                },
            },
            MuiCard: {
                styleOverrides: {
                    root: {
                        borderRadius: 16,
                        border: `1px solid ${isDark ? 'rgba(148, 163, 184, 0.12)' : 'rgba(15, 23, 42, 0.08)'}`,
                        boxShadow: isDark
                            ? '0 4px 24px rgba(0,0,0,0.3)'
                            : '0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)',
                        backdropFilter: 'blur(12px)',
                        backgroundColor: isDark ? 'rgba(26, 29, 46, 0.8)' : 'rgba(255, 255, 255, 0.8)',
                        backgroundImage: 'none',
                        transition: 'all 0.25s ease',
                    },
                },
            },
            MuiPaper: {
                styleOverrides: {
                    root: {
                        backgroundImage: 'none',
                        ...(isDark && {
                            backgroundColor: 'rgba(26, 29, 46, 0.9)',
                            backdropFilter: 'blur(12px)',
                        }),
                    },
                },
            },
            MuiTextField: {
                styleOverrides: {
                    root: {
                        '& .MuiOutlinedInput-root': {
                            borderRadius: 12,
                            transition: 'all 0.2s ease',
                        },
                    },
                },
            },
            MuiChip: {
                styleOverrides: {
                    root: {
                        borderRadius: 8,
                        fontWeight: 500,
                        transition: 'all 0.2s ease',
                    },
                },
            },
            MuiMenu: {
                styleOverrides: {
                    paper: {
                        backgroundImage: 'none',
                        backdropFilter: 'blur(16px)',
                        backgroundColor: isDark ? 'rgba(26, 29, 46, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                        border: `1px solid ${isDark ? 'rgba(148, 163, 184, 0.12)' : 'rgba(15, 23, 42, 0.08)'}`,
                        boxShadow: isDark
                            ? '0 8px 32px rgba(0,0,0,0.4)'
                            : '0 8px 32px rgba(0,0,0,0.12)',
                    },
                },
            },
            MuiAlert: {
                styleOverrides: {
                    root: {
                        borderRadius: 12,
                    },
                },
            },
            MuiLinearProgress: {
                styleOverrides: {
                    root: {
                        borderRadius: 4,
                    },
                },
            },
        },
    })
}

// Brand colors. These literals were copy-pasted across eight files; kept
// here as the single source of truth.
export const BRAND = {
    charcoal: '#20242B',
    charcoalDark: '#121417',
    green: '#42C281',
    greenLight: '#6ED6A1',
    greenDark: '#2FA06A',
} as const

/** Gradient-filled heading text. */
export const gradientTextSx = {
    background: `linear-gradient(135deg, ${BRAND.green}, ${BRAND.greenLight})`,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
} as const

/** Primary call-to-action button. */
export const gradientButtonSx = {
    background: `linear-gradient(135deg, ${BRAND.green}, ${BRAND.greenDark})`,
    '&:hover': {
        background: `linear-gradient(135deg, ${BRAND.greenDark}, ${BRAND.green})`,
    },
} as const
