import { useNavigate } from 'react-router-dom'
import {
    Box,
    Container,
    Typography,
    Button,
    Card,
    CardContent,
    Grid,
    Fade,
} from '@mui/material'
import {
    EmojiEvents as TrophyIcon,
    PlayArrow as PlayIcon,
    History as HistoryIcon,
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'

interface ActionCard {
    icon: React.ReactNode
    title: string
    description: string
    buttonLabel: string
    buttonVariant: 'contained' | 'outlined'
    route: string
    iconColor: string
    gradientFrom: string
    gradientTo: string
}

export default function Home() {
    const navigate = useNavigate()
    const { user } = useAuth()

    const cards: ActionCard[] = [
        {
            icon: <PlayIcon sx={{ fontSize: 36 }} />,
            title: 'Play Game',
            description: 'Choose a game mode and test your skills',
            buttonLabel: 'Start Playing',
            buttonVariant: 'contained',
            route: '/play',
            iconColor: '#6366f1',
            gradientFrom: 'rgba(99,102,241,0.12)',
            gradientTo: 'rgba(139,92,246,0.12)',
        },
        {
            icon: <TrophyIcon sx={{ fontSize: 36 }} />,
            title: 'Leaderboard',
            description: 'See how you rank against other players',
            buttonLabel: 'View Rankings',
            buttonVariant: 'outlined',
            route: '/leaderboard',
            iconColor: '#f59e0b',
            gradientFrom: 'rgba(245,158,11,0.12)',
            gradientTo: 'rgba(251,191,36,0.10)',
        },
        {
            icon: <HistoryIcon sx={{ fontSize: 36 }} />,
            title: 'Game History',
            description: 'Review your past games and scores',
            buttonLabel: 'View History',
            buttonVariant: 'outlined',
            route: '/history',
            iconColor: '#06b6d4',
            gradientFrom: 'rgba(6,182,212,0.12)',
            gradientTo: 'rgba(14,165,233,0.10)',
        },
    ]

    return (
        <Box
            sx={{
                minHeight: 'calc(100vh - 64px)',
                background: (theme) =>
                    theme.palette.mode === 'dark'
                        ? 'radial-gradient(ellipse at 50% -10%, rgba(99,102,241,0.18), transparent 60%)'
                        : 'radial-gradient(ellipse at 50% -10%, rgba(99,102,241,0.10), transparent 60%)',
            }}
        >
            <Container maxWidth="lg">
                <Fade in timeout={500}>
                    <Box sx={{ pt: { xs: 8, md: 12 }, pb: 10 }}>
                        {/* Hero */}
                        <Box sx={{ textAlign: 'center', mb: 8 }}>
                            <Typography
                                variant="h2"
                                component="h1"
                                sx={{
                                    fontWeight: 800,
                                    background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                    backgroundClip: 'text',
                                    mb: 2,
                                }}
                            >
                                Welcome{user?.display_name ? `, ${user.display_name}` : ''}!
                            </Typography>
                            <Typography
                                variant="h6"
                                color="text.secondary"
                                sx={{ fontWeight: 400, maxWidth: 480, mx: 'auto' }}
                            >
                                Test your geography knowledge and climb the leaderboard
                            </Typography>
                        </Box>

                        {/* Cards */}
                        <Grid container spacing={3}>
                            {cards.map((card) => (
                                <Grid item xs={12} md={4} key={card.title}>
                                    <Card
                                        onClick={() => navigate(card.route)}
                                        sx={{
                                            height: '100%',
                                            display: 'flex',
                                            flexDirection: 'column',
                                            cursor: 'pointer',
                                            '&:hover': {
                                                transform: 'translateY(-6px)',
                                                boxShadow: (theme) =>
                                                    theme.palette.mode === 'dark'
                                                        ? `0 12px 40px rgba(0,0,0,0.4)`
                                                        : `0 12px 40px rgba(0,0,0,0.12)`,
                                            },
                                        }}
                                    >
                                        <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 4 }}>
                                            {/* Icon circle */}
                                            <Box
                                                sx={{
                                                    width: 72,
                                                    height: 72,
                                                    mx: 'auto',
                                                    mb: 2.5,
                                                    borderRadius: '50%',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    background: `linear-gradient(135deg, ${card.gradientFrom}, ${card.gradientTo})`,
                                                    color: card.iconColor,
                                                }}
                                            >
                                                {card.icon}
                                            </Box>
                                            <Typography variant="h5" gutterBottom fontWeight={700}>
                                                {card.title}
                                            </Typography>
                                            <Typography color="text.secondary" sx={{ mb: 3 }}>
                                                {card.description}
                                            </Typography>
                                            <Button
                                                variant={card.buttonVariant}
                                                size="large"
                                                onClick={(e) => {
                                                    e.stopPropagation()
                                                    navigate(card.route)
                                                }}
                                                sx={
                                                    card.buttonVariant === 'contained'
                                                        ? {
                                                              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                                                              '&:hover': {
                                                                  background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
                                                              },
                                                          }
                                                        : {}
                                                }
                                            >
                                                {card.buttonLabel}
                                            </Button>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                </Fade>
            </Container>
        </Box>
    )
}
