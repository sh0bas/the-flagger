import { useCallback, useEffect, useRef, useState } from 'react'
import {
    Box,
    Button,
    Typography,
    Divider,
    Paper,
    List,
    ListItem,
    ListItemAvatar,
    Avatar,
    ListItemText,
    Alert,
    Fade,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'
import { useQuiz } from '../../contexts/QuizContext'
import { saveResult, buildSavePayload } from '../../api/flagQuiz'
import confetti from 'canvas-confetti'
import { gradientButtonSx, gradientTextSx } from '../../theme'

export default function Summary() {
    const { state, dispatch } = useQuiz()
    const { config, answers, score, maxStreak, failed, gauntletWon, currentRound } = state
    const savedRef = useRef(false)

    const correctCount = answers.filter((a) => a.correct).length
    const accuracy =
        answers.length > 0 ? Math.round((correctCount / answers.length) * 100) : 0

    useEffect(() => {
        if (gauntletWon) {
            confetti({ particleCount: 180, spread: 90, origin: { y: 0.5 } })
        }
    }, [gauntletWon])

    // Score shown is the server's once the save lands. The client's running
    // total is a display-only mirror, so this is also the drift detector.
    const [savedScore, setSavedScore] = useState<number | null>(null)
    const [saveFailed, setSaveFailed] = useState(false)
    const [saving, setSaving] = useState(false)

    const save = useCallback(() => {
        setSaving(true)
        setSaveFailed(false)
        saveResult(buildSavePayload(answers, config))
            .then((game) => setSavedScore(game.score))
            .catch(() => setSaveFailed(true))
            .finally(() => setSaving(false))
    }, [answers, config])

    useEffect(() => {
        if (savedRef.current) return
        savedRef.current = true
        save()
    }, [save])

    const modeLabel =
        config.mode === 'practice'
            ? 'Practice'
            : config.mode === 'endless'
            ? 'Endless'
            : 'Gauntlet'

    return (
        <Fade in timeout={400}>
            <Box
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 3,
                    py: 6,
                    px: 2,
                }}
            >
                {gauntletWon && (
                    <Alert severity="success" icon={<EmojiEventsIcon />} sx={{ width: '100%', maxWidth: 560 }}>
                        <strong>Gauntlet Complete!</strong> You named every flag without a single mistake.
                    </Alert>
                )}
                {config.mode === 'gauntlet' && failed && (
                    <Alert severity="error" sx={{ width: '100%', maxWidth: 560 }}>
                        <strong>Run failed.</strong> Better luck next time!
                    </Alert>
                )}
                {saveFailed && (
                    <Alert
                        severity="warning"
                        sx={{ width: '100%', maxWidth: 560 }}
                        action={
                            <Button color="inherit" size="small" onClick={save} disabled={saving}>
                                {saving ? 'Retrying…' : 'Retry'}
                            </Button>
                        }
                    >
                        Couldn't save this run. Your answers are still here — retry to keep it.
                    </Alert>
                )}

                <Typography
                    variant="h4"
                    fontWeight={800}
                    sx={{
                        background: gauntletWon
                            ? 'linear-gradient(135deg, #10b981, #06b6d4)'
                            : gradientTextSx.background,
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                    }}
                >
                    {modeLabel} — {gauntletWon ? 'Victory!' : 'Game Over'}
                </Typography>

                {/* Stats */}
                <Paper
                    elevation={0}
                    sx={{
                        p: 3,
                        width: '100%',
                        maxWidth: 560,
                        borderRadius: 3,
                        border: (theme) => `1px solid ${theme.palette.divider}`,
                        borderTop: '3px solid transparent',
                        borderImage: gauntletWon
                            ? 'linear-gradient(135deg, #10b981, #06b6d4) 1'
                            : `${gradientTextSx.background} 1`,
                        borderImageSlice: 1,
                    }}
                >
                    <Box sx={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: 2 }}>
                        <Stat label="Score" value={(savedScore ?? score).toString()} />
                        <Stat label="Accuracy" value={`${accuracy}%`} />
                        <Stat label="Correct" value={`${correctCount} / ${answers.length}`} />
                        <Stat label="Best Streak" value={maxStreak.toString()} />
                        {config.mode === 'practice' && (
                            <Stat label="Rounds" value={currentRound.toString()} />
                        )}
                    </Box>
                </Paper>

                {/* Actions */}
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                        variant="contained"
                        size="large"
                        onClick={() => dispatch({ type: 'START_GAME', pool: state.pool })}
                        sx={{
                            ...gradientButtonSx,
                        }}
                    >
                        Play Again
                    </Button>
                    <Button
                        variant="outlined"
                        size="large"
                        onClick={() => dispatch({ type: 'RESET_TO_LOBBY' })}
                    >
                        Change Settings
                    </Button>
                </Box>

                <Divider sx={{ width: '100%', maxWidth: 560, opacity: 0.6 }} />

                {/* Answer review */}
                <Box sx={{ width: '100%', maxWidth: 560 }}>
                    <Typography variant="h6" fontWeight={700} gutterBottom>
                        Answer Review
                    </Typography>
                    <Paper
                        variant="outlined"
                        sx={{
                            borderRadius: 3,
                            overflow: 'hidden',
                            border: (theme) => `1px solid ${theme.palette.divider}`,
                        }}
                    >
                        <List dense disablePadding>
                            {answers.map((a, i) => (
                                <ListItem
                                    key={i}
                                    divider={i < answers.length - 1}
                                    sx={{
                                        bgcolor: a.correct
                                            ? (theme) =>
                                                  theme.palette.mode === 'dark'
                                                      ? 'rgba(16, 185, 129, 0.10)'
                                                      : 'rgba(16, 185, 129, 0.05)'
                                            : (theme) =>
                                                  theme.palette.mode === 'dark'
                                                      ? 'rgba(239, 68, 68, 0.10)'
                                                      : 'rgba(239, 68, 68, 0.04)',
                                    }}
                                >
                                    <ListItemAvatar>
                                        <Avatar
                                            src={a.flagUrl}
                                            variant="rounded"
                                            sx={{ width: 48, height: 32, mr: 1, bgcolor: 'transparent' }}
                                        />
                                    </ListItemAvatar>
                                    <ListItemText
                                        primary={a.entityName}
                                        secondary={
                                            a.correct
                                                ? `✓ ${a.userAnswer}`
                                                : `✗ You said: "${a.userAnswer}"`
                                        }
                                        secondaryTypographyProps={{
                                            color: a.correct ? 'success.main' : 'error.main',
                                        }}
                                    />
                                    {a.correct ? (
                                        <CheckCircleIcon color="success" fontSize="small" />
                                    ) : (
                                        <CancelIcon color="error" fontSize="small" />
                                    )}
                                </ListItem>
                            ))}
                        </List>
                    </Paper>
                </Box>
            </Box>
        </Fade>
    )
}

function Stat({ label, value }: { label: string; value: string }) {
    return (
        <Box
            sx={{
                textAlign: 'center',
                minWidth: 80,
                p: 1.5,
                borderRadius: 2,
                bgcolor: (theme) =>
                    theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.02)',
            }}
        >
            <Typography variant="h5" fontWeight={700}>
                {value}
            </Typography>
            <Typography variant="caption" color="text.secondary">
                {label}
            </Typography>
        </Box>
    )
}
