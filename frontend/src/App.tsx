import { Routes, Route } from 'react-router-dom'
import { Box, Container, Typography } from '@mui/material'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Play from './pages/Play'
import { QuizProvider } from './contexts/QuizContext'

const PlaceholderPage = ({ title }: { title: string }) => (
    <Container sx={{ py: 8 }}>
        <Typography variant="h3" align="center">
            {title}
        </Typography>
        <Typography variant="body1" align="center" color="text.secondary" sx={{ mt: 2 }}>
            Coming soon...
        </Typography>
    </Container>
)

function App() {
    return (
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
            <Navbar />
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <Home />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/play"
                    element={
                        <ProtectedRoute>
                            <QuizProvider>
                                <Play />
                            </QuizProvider>
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/leaderboard"
                    element={
                        <ProtectedRoute>
                            <PlaceholderPage title="Leaderboard" />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/history"
                    element={
                        <ProtectedRoute>
                            <PlaceholderPage title="Game History" />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/profile"
                    element={
                        <ProtectedRoute>
                            <PlaceholderPage title="Profile" />
                        </ProtectedRoute>
                    }
                />
            </Routes>
        </Box>
    )
}

export default App
