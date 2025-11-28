import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'

function App() {
    return (
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
            <Routes>
                <Route path="/" element={
                    <Box sx={{
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        minHeight: '100vh',
                        flexDirection: 'column',
                        gap: 2
                    }}>
                        <h1>🌍 Flagger</h1>
                        <p>Geography Education Platform</p>
                        <p style={{ fontSize: '14px', color: '#666' }}>Coming soon...</p>
                    </Box>
                } />
            </Routes>
        </Box>
    )
}

export default App
