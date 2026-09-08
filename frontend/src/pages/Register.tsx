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
import { errorMessage } from '../api/client'
import { useAuth } from '../contexts/AuthContext'
import { gradientButtonSx, gradientTextSx } from '../theme'

export default function Register() {
    const navigate = useNavigate()
    const { register } = useAuth()
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [displayName, setDisplayName] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (password !== confirmPassword) {
            setError('Passwords do not match')
            return
        }

        if (password.length < 8) {
            setError('Password must be at least 8 characters')
            return
        }

        setLoading(true)

        try {
            await register({
                username,
                email,
                password,
                display_name: displayName || undefined,
            })
            navigate('/')
        } catch (err) {
            setError(errorMessage(err, 'Registration failed. Please try again.'))
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
                py: 4,
                background: (theme) =>
                    theme.palette.mode === 'dark'
                        ? 'radial-gradient(ellipse at 70% 20%, rgba(236,72,153,0.10), transparent 50%), radial-gradient(ellipse at 30% 80%, rgba(99,102,241,0.12), transparent 50%)'
                        : 'radial-gradient(ellipse at 70% 20%, rgba(236,72,153,0.05), transparent 50%), radial-gradient(ellipse at 30% 80%, rgba(99,102,241,0.07), transparent 50%)',
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
                            ...gradientTextSx,
                            mb: 1,
                        }}
                    >
                        Join Flagger
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Create an account to start playing and track your progress
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
                        helperText="Unique identifier for your account"
                    />
                    <TextField
                        label="Email"
                        type="email"
                        fullWidth
                        margin="normal"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        disabled={loading}
                    />
                    <TextField
                        label="Display Name (Optional)"
                        fullWidth
                        margin="normal"
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        disabled={loading}
                        helperText="How you'll appear in the app"
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
                        helperText="At least 8 characters"
                    />
                    <TextField
                        label="Confirm Password"
                        type="password"
                        fullWidth
                        margin="normal"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
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
                            ...gradientButtonSx,
                            '&.Mui-disabled': {
                                background: (theme) =>
                                    theme.palette.mode === 'dark'
                                        ? 'rgba(255,255,255,0.08)'
                                        : 'rgba(0,0,0,0.06)',
                            },
                        }}
                    >
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </Button>

                    <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2">
                            Already have an account?{' '}
                            <Link component={RouterLink} to="/login" fontWeight={600}>
                                Login here
                            </Link>
                        </Typography>
                    </Box>
                </Box>
            </Paper>
        </Box>
    )
}
