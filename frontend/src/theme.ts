import { createTheme } from '@mui/material/styles'

// Create Material-UI theme with modern aesthetics
const theme = createTheme({
    palette: {
        mode: 'light',
        primary: {
            main: '#6366f1', // Modern indigo
            light: '#818cf8',
            dark: '#4f46e5',
        },
        secondary: {
            main: '#ec4899', // Vibrant pink
            light: '#f472b6',
            dark: '#db2777',
        },
        success: {
            main: '#10b981', // Modern green
            light: '#34d399',
            dark: '#059669',
        },
        error: {
            main: '#ef4444', // Modern red
            light: '#f87171',
            dark: '#dc2626',
        },
        background: {
            default: '#f8fafc',
            paper: '#ffffff',
        },
    },
    typography: {
        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
        h1: {
            fontWeight: 700,
        },
        h2: {
            fontWeight: 700,
        },
        h3: {
            fontWeight: 600,
        },
        h4: {
            fontWeight: 600,
        },
        button: {
            textTransform: 'none',
            fontWeight: 600,
        },
    },
    shape: {
        borderRadius: 12,
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    padding: '10px 24px',
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
                },
            },
        },
    },
})

export default theme
