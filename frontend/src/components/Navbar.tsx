import { useState } from 'react'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box,
    IconButton,
    Menu,
    MenuItem,
    Avatar,
    Tooltip,
} from '@mui/material'
import { AccountCircle, DarkMode, LightMode } from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import { useThemeMode } from '../contexts/ThemeContext'
import { gradientTextSx } from '../theme'

export default function Navbar() {
    const navigate = useNavigate()
    const { user, logout, isAuthenticated } = useAuth()
    const { mode, toggleTheme } = useThemeMode()
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget)
    }

    const handleMenuClose = () => {
        setAnchorEl(null)
    }

    const handleLogout = () => {
        logout()
        handleMenuClose()
        navigate('/login')
    }


    return (
        <AppBar position="sticky">
            <Toolbar>
                <Typography
                    variant="h6"
                    component={RouterLink}
                    to="/"
                    sx={{
                        flexGrow: 1,
                        textDecoration: 'none',
                        fontWeight: 800,
                        fontSize: '1.35rem',
                        ...gradientTextSx,
                    }}
                >
                    Flagger
                </Typography>

                {isAuthenticated ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {(['Play', 'History'] as const).map((label) => (
                            <Button
                                key={label}
                                color="inherit"
                                component={RouterLink}
                                to={`/${label.toLowerCase()}`}
                                sx={{
                                    position: 'relative',
                                    fontWeight: 500,
                                    '&::after': {
                                        content: '""',
                                        position: 'absolute',
                                        bottom: 4,
                                        left: '50%',
                                        transform: 'translateX(-50%) scaleX(0)',
                                        width: '60%',
                                        height: 2,
                                        bgcolor: 'primary.main',
                                        borderRadius: 1,
                                        transition: 'transform 0.2s ease',
                                    },
                                    '&:hover::after': {
                                        transform: 'translateX(-50%) scaleX(1)',
                                    },
                                }}
                            >
                                {label}
                            </Button>
                        ))}

                        <Tooltip title={mode === 'dark' ? 'Light mode' : 'Dark mode'}>
                            <IconButton onClick={toggleTheme} color="inherit" sx={{ ml: 0.5 }}>
                                {mode === 'dark' ? <LightMode fontSize="small" /> : <DarkMode fontSize="small" />}
                            </IconButton>
                        </Tooltip>

                        <IconButton
                            onClick={handleMenuOpen}
                            color="inherit"
                            aria-label="Account menu"
                            aria-haspopup="true"
                            sx={{ ml: 0.5 }}
                        >
                            {user?.avatar_url ? (
                                <Avatar
                                    src={user.avatar_url}
                                    alt={user.display_name || user.username}
                                    sx={{ width: 32, height: 32 }}
                                />
                            ) : (
                                <AccountCircle />
                            )}
                        </IconButton>

                        <Menu
                            anchorEl={anchorEl}
                            open={Boolean(anchorEl)}
                            onClose={handleMenuClose}
                            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                        >
                            <MenuItem disabled>
                                <Typography variant="body2" color="text.secondary">
                                    {user?.display_name || user?.username}
                                </Typography>
                            </MenuItem>
                            <MenuItem onClick={handleLogout}>Logout</MenuItem>
                        </Menu>
                    </Box>
                ) : (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Tooltip title={mode === 'dark' ? 'Light mode' : 'Dark mode'}>
                            <IconButton onClick={toggleTheme} color="inherit">
                                {mode === 'dark' ? <LightMode fontSize="small" /> : <DarkMode fontSize="small" />}
                            </IconButton>
                        </Tooltip>
                        <Button color="inherit" component={RouterLink} to="/login">
                            Login
                        </Button>
                        <Button
                            color="inherit"
                            component={RouterLink}
                            to="/register"
                            variant="outlined"
                            sx={{
                                borderColor: 'currentColor',
                                '&:hover': { borderColor: 'primary.main', color: 'primary.main' },
                            }}
                        >
                            Register
                        </Button>
                    </Box>
                )}
            </Toolbar>
        </AppBar>
    )
}
