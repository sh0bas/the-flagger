import { useEffect, useRef } from 'react'
import { Box, Chip, Typography, LinearProgress, Tooltip } from '@mui/material'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import PlaceIcon from '@mui/icons-material/Place'
import { useQuiz } from '../../contexts/QuizContext'
import AutocompleteInput from './AutocompleteInput'
import FeedbackOverlay from './FeedbackOverlay'

/**
 * Groups of ISO codes whose flags are visually near-identical.
 * A hint is shown when the current flag belongs to a group that has
 * at least one other member in the active pool.
 */
const CONFUSABLE_GROUPS: string[][] = [
    ['mc', 'id'],           // Monaco / Indonesia — red over white
    ['ro', 'td'],           // Romania / Chad — blue-yellow-red vertical
    ['ie', 'ci'],           // Ireland / Ivory Coast — green-white-orange vertical (mirrored)
    ['nl', 'lu', 'hr'],     // Netherlands / Luxembourg / Croatia — red-white-blue horizontal
    ['no', 'is', 'fo'],     // Norway / Iceland / Faroe Islands — Nordic crosses
    ['au', 'nz'],           // Australia / New Zealand — Southern Cross + Union Jack
    ['ng', 'mg'],           // Nigeria / Madagascar — green-white-green (vertical vs stripes)
    ['gn', 'ml', 'sn'],     // Guinea / Mali / Senegal — red-yellow-green variants
    ['si', 'sk'],           // Slovenia / Slovakia — white-blue-red horizontal + shield
]

const REGION_LABELS: Record<string, string> = {
    americas: 'the Americas',
    europe: 'Europe',
    africa: 'Africa',
    asia: 'Asia',
    oceania: 'Oceania',
}

/** Convert a 2-letter ISO code to a Twemoji flag image URL. */
function isoToTwemoji(iso: string): string {
    const codepoints = iso
        .toUpperCase()
        .split('')
        .map((c) => (0x1f1e6 + c.charCodeAt(0) - 65).toString(16))
        .join('-')
    return `https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/${codepoints}.svg`
}

export default function GameScreen() {
    const { state, dispatch, filteredPool } = useQuiz()
    const { currentEntity, phase, config, streak, score, currentRound, queue, currentIndex, lastAnswer } = state
    const questionStartRef = useRef<number>(Date.now())

    // Reset timer when entity changes
    useEffect(() => {
        questionStartRef.current = Date.now()
    }, [currentEntity?.id])

    if (!currentEntity) return null

    // Show region hint if this flag is confusable with another flag in the active pool
    const poolIsoCodes = new Set(filteredPool.map((e) => e.iso_code.toLowerCase()))
    const currentIso = currentEntity.iso_code.toLowerCase()
    const confusableGroup = CONFUSABLE_GROUPS.find((g) => g.includes(currentIso))
    const showRegionHint =
        confusableGroup !== undefined &&
        confusableGroup.some((iso) => iso !== currentIso && poolIsoCodes.has(iso))

    const handleSubmit = (answer: string) => {
        const responseMs = Date.now() - questionStartRef.current
        dispatch({ type: 'SUBMIT_ANSWER', userAnswer: answer, responseMs })
    }

    const handleFeedbackDone = () => {
        dispatch({ type: 'ADVANCE' })
    }

    // Session info per mode
    const renderSessionInfo = () => {
        if (config.mode === 'practice') {
            return (
                <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center', flexWrap: 'wrap' }}>
                    <Chip label={`Round ${currentRound}`} color="primary" size="small" />
                    <Chip label={`${currentIndex + 1} / ${queue.length}`} size="small" variant="outlined" />
                    <Chip label={`Score: ${score}`} size="small" variant="outlined" />
                </Box>
            )
        }
        if (config.mode === 'endless') {
            return (
                <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                    <Chip label={`Streak: ${streak}`} color="warning" size="small" />
                    <Chip label={`Score: ${score}`} size="small" variant="outlined" />
                </Box>
            )
        }
        // gauntlet
        return (
            <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center', flexWrap: 'wrap' }}>
                <Chip
                    label={`${currentIndex + 1} / ${filteredPool.length}`}
                    color="secondary"
                    size="small"
                />
                <Tooltip title="One mistake ends the run!">
                    <Chip
                        icon={<WarningAmberIcon />}
                        label="No mistakes"
                        color="error"
                        variant="outlined"
                        size="small"
                    />
                </Tooltip>
                <Chip label={`Score: ${score}`} size="small" variant="outlined" />
            </Box>
        )
    }

    // Progress bar for gauntlet
    const gauntletProgress =
        config.mode === 'gauntlet' ? ((currentIndex + 1) / filteredPool.length) * 100 : null

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 3,
                py: 4,
                px: 2,
                minHeight: '70vh',
            }}
        >
            {/* Session info bar */}
            <Box sx={{ width: '100%', maxWidth: 640 }}>{renderSessionInfo()}</Box>

            {/* Gauntlet progress bar */}
            {gauntletProgress !== null && (
                <Box sx={{ width: '100%', maxWidth: 640 }}>
                    <LinearProgress
                        variant="determinate"
                        value={gauntletProgress}
                        color="secondary"
                        sx={{ height: 6, borderRadius: 3 }}
                    />
                </Box>
            )}

            {/* Flag image area */}
            <Box
                sx={{
                    position: 'relative',
                    width: '100%',
                    maxWidth: 480,
                    borderRadius: 3,
                    overflow: 'hidden',
                    boxShadow: (theme) =>
                        theme.palette.mode === 'dark'
                            ? '0 4px 32px rgba(0,0,0,0.45)'
                            : '0 4px 24px rgba(0,0,0,0.12)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                }}
            >
                <Box
                    component="img"
                    src={isoToTwemoji(currentEntity.iso_code)}
                    alt="Flag"
                    sx={{
                        width: '100%',
                        height: 'auto',
                        display: 'block',
                    }}
                />

                {/* Feedback overlay */}
                {phase === 'feedback' && lastAnswer && (
                    <FeedbackOverlay answer={lastAnswer} onDone={handleFeedbackDone} />
                )}
            </Box>

            {/* Region hint for visually confusable flags */}
            {showRegionHint && (
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.75,
                        px: 2,
                        py: 0.75,
                        borderRadius: 99,
                        border: (theme) => `1px solid ${theme.palette.divider}`,
                        bgcolor: (theme) =>
                            theme.palette.mode === 'dark'
                                ? 'rgba(255,255,255,0.06)'
                                : 'rgba(0,0,0,0.04)',
                        mt: -1,
                    }}
                >
                    <PlaceIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="caption" color="text.secondary" fontWeight={500}>
                        This country is in {REGION_LABELS[currentEntity.region] ?? currentEntity.region}
                    </Typography>
                </Box>
            )}

            {/* Input */}
            <AutocompleteInput
                filters={config.filters}
                onSubmit={handleSubmit}
                disabled={phase === 'feedback'}
                autoFocus
            />

            <Typography variant="body2" color="text.secondary" sx={{ mt: -1 }}>
                Tab to autocomplete &amp; submit · Enter to submit
            </Typography>
        </Box>
    )
}
