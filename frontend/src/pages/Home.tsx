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
    PlayArrow as PlayIcon,
    History as HistoryIcon,
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import { gradientButtonSx, gradientTextSx } from '../theme'

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
            iconColor: '#42C281',
            gradientFrom: 'rgba(66,194,129,0.12)',
            gradientTo: 'rgba(47,160,106,0.10)',
        },
        {
            icon: <HistoryIcon sx={{ fontSize: 36 }} />,
            title: 'Game History',
            description: 'Review your past games and scores',
            buttonLabel: 'View History',
            buttonVariant: 'outlined',
            route: '/history',
            iconColor: '#6b7280',
            gradientFrom: 'rgba(107,114,128,0.12)',
            gradientTo: 'rgba(75,85,99,0.10)',
        },
    ]

    return (
        <Box
            sx={{
                minHeight: { xs: 'calc(100vh - 56px)', sm: 'calc(100vh - 64px)' },
                background: (theme) =>
                    theme.palette.mode === 'dark'
                        ? 'radial-gradient(ellipse at 50% -10%, rgba(66,194,129,0.18), transparent 60%)'
                        : 'radial-gradient(ellipse at 50% -10%, rgba(66,194,129,0.10), transparent 60%)',
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
                                    ...gradientTextSx,
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
                                Test your geography knowledge, one flag at a time
                            </Typography>
                        </Box>

                        {/* Cards */}
                        <Grid container spacing={3}>
                            {cards.map((card) => (
                                <Grid item xs={12} md={4} key={card.title}>
                                    <Card
                                        sx={{
                                            height: '100%',
                                            display: 'flex',
                                            flexDirection: 'column',
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
                                                onClick={() => navigate(card.route)}
                                                sx={
                                                    card.buttonVariant === 'contained'
                                                        ? {
                                                              ...gradientButtonSx,
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
