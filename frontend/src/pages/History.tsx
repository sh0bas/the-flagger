import { useQuery } from '@tanstack/react-query'
import {
    Alert,
    Box,
    Chip,
    CircularProgress,
    Container,
    Divider,
    Fade,
    List,
    ListItem,
    ListItemText,
    Typography,
} from '@mui/material'
import { fetchHistory } from '../api/flagQuiz'
import { MODE_LABELS } from '../components/quiz/Lobby'

export default function History() {
    const { data, isLoading, isError } = useQuery({
        queryKey: ['history'],
        queryFn: () => fetchHistory(),
    })

    return (
        <Container maxWidth="sm" sx={{ py: 6 }}>
            <Typography variant="h4" component="h1" fontWeight={800} gutterBottom>
                Game History
            </Typography>

            {isLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                    <CircularProgress />
                </Box>
            )}

            {isError && <Alert severity="error">Couldn't load your history.</Alert>}

            {data && data.length === 0 && (
                <Typography color="text.secondary" sx={{ py: 4 }}>
                    No games yet — finish a round and it'll show up here.
                </Typography>
            )}

            {data && data.length > 0 && (
                <Fade in timeout={400}>
                    <List disablePadding>
                        {data.map((g, i) => {
                            const accuracy = g.questions_count
                                ? Math.round((g.correct_count / g.questions_count) * 100)
                                : 0
                            return (
                                <Box key={g.id}>
                                    {i > 0 && <Divider component="li" />}
                                    <ListItem
                                        sx={{ px: 0, gap: 2 }}
                                        secondaryAction={
                                            <Typography variant="h6" fontWeight={700}>
                                                {g.score}
                                            </Typography>
                                        }
                                    >
                                        <ListItemText
                                            primary={
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Chip
                                                        label={(MODE_LABELS as Record<string, string>)[g.game_mode] ?? g.game_mode}
                                                        size="small"
                                                    />
                                                    <Typography variant="body2" color="text.secondary">
                                                        {new Date(g.played_at).toLocaleDateString()}
                                                    </Typography>
                                                </Box>
                                            }
                                            secondary={`${g.correct_count}/${g.questions_count} correct · ${accuracy}% · best streak ${g.max_streak}`}
                                            sx={{ my: 0 }}
                                        />
                                    </ListItem>
                                </Box>
                            )
                        })}
                    </List>
                </Fade>
            )}
        </Container>
    )
}
