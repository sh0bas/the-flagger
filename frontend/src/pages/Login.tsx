import { useState } from 'react'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import {
    Box,
    TextField,
    Button,
    Typography,
    Link,
    Alert,
    Paper,
} from '@mui/material'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
    const navigate = useNavigate()
    const { login } = useAuth()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            await login({ username, password })
            navigate('/')
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                px: 2,
                background: (theme) =>
                    theme.palette.mode === 'dark'
                        ? 'radial-gradient(ellipse at 30% 20%, rgba(99,102,241,0.12), transparent 50%), radial-gradient(ellipse at 70% 80%, rgba(236,72,153,0.10), transparent 50%)'
                        : 'radial-gradient(ellipse at 30% 20%, rgba(99,102,241,0.07), transparent 50%), radial-gradient(ellipse at 70% 80%, rgba(236,72,153,0.05), transparent 50%)',
            }}
        >
            <Paper
                elevation={0}
                sx={{
                    p: { xs: 3, sm: 5 },
                    width: '100%',
                    maxWidth: 440,
                    borderRadius: 4,
                    border: (theme) => `1px solid ${theme.palette.divider}`,
                }}
            >
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <Typography
                        variant="h4"
                        component="h1"
                        sx={{
                            fontWeight: 800,
                            background: 'linear-gradient(135deg, #6366f1, #ec4899)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            backgroundClip: 'text',
                            mb: 1,
                        }}
                    >
                        Welcome back
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Ready to test your geography knowledge?
                    </Typography>
                </Box>

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit}>
                    <TextField
                        label="Username"
                        fullWidth
                        margin="normal"
                        required
                        autoFocus
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        disabled={loading}
                    />
                    <TextField
                        label="Password"
                        type="password"
                        fullWidth
                        margin="normal"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={loading}
                    />
                    <Button
                        type="submit"
                        variant="contained"
                        fullWidth
                        size="large"
                        disabled={loading}
                        sx={{
                            mt: 3,
                            mb: 2,
                            py: 1.5,
                            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                            '&:hover': {
                                background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
                            },
                            '&.Mui-disabled': {
                                background: (theme) =>
                                    theme.palette.mode === 'dark'
                                        ? 'rgba(255,255,255,0.08)'
                                        : 'rgba(0,0,0,0.06)',
                            },
                        }}
                    >
                        {loading ? 'Logging in...' : 'Login'}
                    </Button>

                    <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2">
                            Don't have an account?{' '}
                            <Link component={RouterLink} to="/register" fontWeight={600}>
                                Register here
                            </Link>
                        </Typography>
                    </Box>
                </Box>
            </Paper>
        </Box>
    )
}
