import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Box, Button, Typography } from '@mui/material'

/**
 * Last line of defence against a white screen mid-run.
 *
 * This app uses <Routes>, not a data router, so react-router's errorElement
 * isn't available — a class component is still the only way to catch a render
 * throw in React 18.
 */
export default class ErrorBoundary extends Component<
    { children: ReactNode },
    { hasError: boolean }
> {
    state = { hasError: false }

    static getDerivedStateFromError() {
        return { hasError: true }
    }

    componentDidCatch(error: Error, info: ErrorInfo) {
        console.error('Unhandled render error:', error, info.componentStack)
    }

    render() {
        if (!this.state.hasError) return this.props.children
        return (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, py: 12 }}>
                <Typography variant="h5" fontWeight={700}>
                    Something went wrong
                </Typography>
                <Button variant="contained" onClick={() => window.location.reload()}>
                    Reload
                </Button>
            </Box>
        )
    }
}
