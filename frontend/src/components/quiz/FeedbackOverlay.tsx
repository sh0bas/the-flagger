import { useEffect } from 'react'
import { Box, Typography, Fade } from '@mui/material'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined'
import type { QuizAnswer } from '../../types'

interface Props {
    answer: QuizAnswer
    onDone: () => void
}

const CORRECT_DELAY = 900
const INCORRECT_DELAY = 2200

export default function FeedbackOverlay({ answer, onDone }: Props) {
    useEffect(() => {
        const timer = setTimeout(onDone, answer.correct ? CORRECT_DELAY : INCORRECT_DELAY)
        return () => clearTimeout(timer)
    }, [answer, onDone])

    const isCorrect = answer.correct

    return (
        <Fade in timeout={200}>
            <Box
                role="status"
                aria-live="polite"
                sx={{
                    position: 'absolute',
                    inset: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: 3,
                    zIndex: 10,
                    gap: 1.5,
                    px: 3,
                    textAlign: 'center',
                    // Gradient background instead of flat colour
                    background: isCorrect
                        ? 'linear-gradient(135deg, rgba(47,160,106,0.95) 0%, rgba(66,194,129,0.88) 100%)'
                        : 'linear-gradient(135deg, rgba(185,28,28,0.95) 0%, rgba(239,68,68,0.88) 100%)',
                    backdropFilter: 'blur(8px)',
                    // Coloured glow ring around the whole overlay
                    boxShadow: isCorrect
                        ? 'inset 0 0 60px rgba(66,194,129,0.3), 0 0 40px rgba(66,194,129,0.4)'
                        : 'inset 0 0 60px rgba(239,68,68,0.3), 0 0 40px rgba(239,68,68,0.4)',
                }}
            >
                {/* Icon with glow halo */}
                <Box
                    sx={{
                        position: 'relative',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        '&::before': {
                            content: '""',
                            position: 'absolute',
                            width: 96,
                            height: 96,
                            borderRadius: '50%',
                            background: isCorrect
                                ? 'radial-gradient(circle, rgba(110,214,161,0.5) 0%, transparent 70%)'
                                : 'radial-gradient(circle, rgba(248,113,113,0.5) 0%, transparent 70%)',
                        },
                    }}
                >
                    {isCorrect ? (
                        <CheckCircleOutlineIcon
                            sx={{
                                fontSize: 72,
                                color: '#fff',
                                filter: 'drop-shadow(0 0 12px rgba(110,214,161,0.8))',
                            }}
                        />
                    ) : (
                        <CancelOutlinedIcon
                            sx={{
                                fontSize: 72,
                                color: '#fff',
                                filter: 'drop-shadow(0 0 12px rgba(248,113,113,0.8))',
                            }}
                        />
                    )}
                </Box>

                <Typography
                    variant="h4"
                    fontWeight={800}
                    sx={{
                        color: '#fff',
                        textShadow: isCorrect
                            ? '0 0 20px rgba(110,214,161,0.6)'
                            : '0 0 20px rgba(248,113,113,0.6)',
                        letterSpacing: '-0.01em',
                    }}
                >
                    {isCorrect ? 'Correct!' : 'Incorrect'}
                </Typography>

                {!isCorrect && (
                    <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.95)', fontWeight: 600 }}>
                        That was: <strong>{answer.entityName}</strong>
                    </Typography>
                )}

                {!isCorrect && answer.userAnswer && (
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        You guessed: {answer.userAnswer}
                    </Typography>
                )}
            </Box>
        </Fade>
    )
}
