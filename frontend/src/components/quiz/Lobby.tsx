import type { ReactNode } from 'react'
import {
    Box,
    Button,
    Card,
    CardActionArea,
    CardContent,
    Chip,
    Divider,
    FormLabel,
    ToggleButton,
    ToggleButtonGroup,
    Typography,
    Slider,
    CircularProgress,
    Alert,
    Fade,
} from '@mui/material'
import FlashOnIcon from '@mui/icons-material/FlashOn'
import SchoolIcon from '@mui/icons-material/School'
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'
import { useQuiz } from '../../contexts/QuizContext'
import type { FlagQuizMode, Region, Difficulty, EntityType } from '../../types'
import { gradientButtonSx, gradientTextSx } from '../../theme'

const REGIONS: { value: Region; label: string }[] = [
    { value: 'americas', label: 'Americas' },
    { value: 'europe', label: 'Europe' },
    { value: 'africa', label: 'Africa' },
    { value: 'asia', label: 'Asia' },
    { value: 'oceania', label: 'Oceania' },
]

const DIFFICULTIES: { value: Difficulty; label: string }[] = [
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' },
]

const ENTITY_TYPES: { value: EntityType; label: string }[] = [
    { value: 'sovereign_state', label: 'Sovereign States' },
    { value: 'territory', label: 'Territories' },
    { value: 'us_state', label: 'US States' },
]

const MODES: { value: FlagQuizMode; label: string; description: string; icon: ReactNode; color: string }[] = [
    {
        value: 'practice',
        label: 'Practice',
        description: 'Learn at your own pace. Incorrect flags carry forward until you nail them all.',
        icon: <SchoolIcon fontSize="large" />,
        color: '#6366f1',
    },
    {
        value: 'endless',
        label: 'Endless',
        description: 'Build the longest streak you can. One wrong answer ends the run.',
        icon: <FlashOnIcon fontSize="large" />,
        color: '#f59e0b',
    },
    {
        value: 'gauntlet',
        label: 'Gauntlet',
        description: 'Name every flag in the pool — in random order — without a single mistake.',
        icon: <EmojiEventsIcon fontSize="large" />,
        color: '#ec4899',
    },
]

// Derived, not re-typed, so a rename/addition to MODES above can't drift out
// of sync with what other views (e.g. History) display.
export const MODE_LABELS: Record<FlagQuizMode, string> = Object.fromEntries(
    MODES.map((m) => [m.value, m.label])
) as Record<FlagQuizMode, string>

const BATCH_MARKS = [
    { value: 5, label: '5' },
    { value: 10, label: '10' },
    { value: 15, label: '15' },
    { value: 20, label: '20' },
]

export default function Lobby() {
    const { state, dispatch, filteredPool, catalogLoading, catalogError } = useQuiz()
    const { config } = state
    const { filters, mode, batchSize } = config

    const setMode = (m: FlagQuizMode) =>
        dispatch({ type: 'SET_CONFIG', config: { ...config, mode: m } })

    const toggleRegion = (r: Region) => {
        const next = filters.regions.includes(r)
            ? filters.regions.filter((x) => x !== r)
            : [...filters.regions, r]
        dispatch({ type: 'SET_CONFIG', config: { ...config, filters: { ...filters, regions: next } } })
    }

    const setDifficulties = (_: unknown, val: Difficulty[]) => {
        dispatch({
            type: 'SET_CONFIG',
            config: { ...config, filters: { ...filters, difficulties: val } },
        })
    }

    const toggleEntityType = (et: EntityType) => {
        const next = filters.entityTypes.includes(et)
            ? filters.entityTypes.filter((x) => x !== et)
            : [...filters.entityTypes, et]
        dispatch({ type: 'SET_CONFIG', config: { ...config, filters: { ...filters, entityTypes: next } } })
    }

    const setBatchSize = (_: Event, val: number | number[]) =>
        dispatch({ type: 'SET_CONFIG', config: { ...config, batchSize: val as number } })

    const handleStart = () => {
        if (filteredPool.length === 0) return
        dispatch({ type: 'START_GAME', pool: filteredPool })
    }

    const poolSize = filteredPool.length
    const canStart = poolSize > 0

    return (
        <Fade in timeout={400}>
            <Box sx={{ maxWidth: 720, mx: 'auto', py: 6, px: 2, display: 'flex', flexDirection: 'column', gap: 4 }}>
                {/* Heading */}
                <Box sx={{ textAlign: 'center' }}>
                    <Typography
                        variant="h3"
                        fontWeight={800}
                        sx={{
                            ...gradientTextSx,
                        }}
                    >
                        Flag Quiz
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mt: 0.5 }}>
                        Choose a mode and set your filters to get started
                    </Typography>
                </Box>

                {catalogError && (
                    <Alert severity="error">Failed to load flag catalog. Please refresh the page.</Alert>
                )}

                {/* Mode selection */}
                <Box>
                    <Typography variant="overline" color="text.secondary" letterSpacing={1.2}>
                        Game Mode
                    </Typography>
                    <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 2, mt: 1 }}>
                        {MODES.map((m) => {
                            const selected = mode === m.value
                            return (
                                <Card
                                    key={m.value}
                                    sx={{
                                        border: '2px solid',
                                        borderColor: selected ? m.color : 'divider',
                                        transition: 'all 0.2s ease',
                                        boxShadow: selected
                                            ? (theme) =>
                                                  `0 0 0 1px ${m.color}, 0 4px 20px ${
                                                      theme.palette.mode === 'dark'
                                                          ? 'rgba(0,0,0,0.3)'
                                                          : 'rgba(0,0,0,0.08)'
                                                  }`
                                            : undefined,
                                        '&:hover': {
                                            borderColor: m.color,
                                            transform: 'translateY(-3px)',
                                        },
                                    }}
                                >
                                    {/* CardActionArea renders a real <button>: focus ring, Enter/Space,
                                        and aria-pressed state — none of which a <Card onClick> has. */}
                                    <CardActionArea
                                        onClick={() => setMode(m.value)}
                                        aria-pressed={selected}
                                        sx={{ height: '100%' }}
                                    >
                                    <CardContent sx={{ textAlign: 'center', p: 2.5, '&:last-child': { pb: 2.5 } }}>
                                        <Box
                                            sx={{
                                                color: selected ? m.color : 'text.secondary',
                                                mb: 1,
                                                transition: 'color 0.2s ease',
                                            }}
                                        >
                                            {m.icon}
                                        </Box>
                                        <Typography variant="subtitle1" fontWeight={700}>
                                            {m.label}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.4 }}>
                                            {m.description}
                                        </Typography>
                                    </CardContent>
                                    </CardActionArea>
                                </Card>
                            )
                        })}
                    </Box>
                </Box>

                <Divider sx={{ opacity: 0.6 }} />

                {/* Filters */}
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                    <Typography variant="overline" color="text.secondary" letterSpacing={1.2}>
                        Filters
                    </Typography>

                    {/* Region */}
                    <Box>
                        <FormLabel sx={{ fontSize: '0.85rem', mb: 1, display: 'block' }}>Region</FormLabel>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {REGIONS.map((r) => (
                                <Chip
                                    key={r.value}
                                    label={r.label}
                                    clickable
                                    onClick={() => toggleRegion(r.value)}
                                    color={filters.regions.includes(r.value) ? 'primary' : 'default'}
                                    variant={filters.regions.includes(r.value) ? 'filled' : 'outlined'}
                                />
                            ))}
                            <Chip
                                label="All"
                                clickable
                                onClick={() =>
                                    dispatch({
                                        type: 'SET_CONFIG',
                                        config: { ...config, filters: { ...filters, regions: [] } },
                                    })
                                }
                                variant={filters.regions.length === 0 ? 'filled' : 'outlined'}
                                color={filters.regions.length === 0 ? 'primary' : 'default'}
                            />
                        </Box>
                    </Box>

                    {/* Difficulty */}
                    <Box>
                        <FormLabel sx={{ fontSize: '0.85rem', mb: 1, display: 'block' }}>Difficulty</FormLabel>
                        <ToggleButtonGroup
                            value={filters.difficulties}
                            onChange={setDifficulties}
                            size="small"
                            sx={{ borderRadius: 2 }}
                        >
                            {DIFFICULTIES.map((d) => (
                                <ToggleButton key={d.value} value={d.value} sx={{ borderRadius: '8px !important', px: 2 }}>
                                    {d.label}
                                </ToggleButton>
                            ))}
                        </ToggleButtonGroup>
                        {filters.difficulties.length === 0 && (
                            <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                (all difficulties)
                            </Typography>
                        )}
                    </Box>

                    {/* Entity type */}
                    <Box>
                        <FormLabel sx={{ fontSize: '0.85rem', mb: 1, display: 'block' }}>Type</FormLabel>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {ENTITY_TYPES.map((et) => (
                                <Chip
                                    key={et.value}
                                    label={et.label}
                                    clickable
                                    onClick={() => toggleEntityType(et.value)}
                                    color={filters.entityTypes.includes(et.value) ? 'secondary' : 'default'}
                                    variant={filters.entityTypes.includes(et.value) ? 'filled' : 'outlined'}
                                />
                            ))}
                        </Box>
                    </Box>

                    {/* Batch size — practice only */}
                    {mode === 'practice' && (
                        <Box>
                            <FormLabel sx={{ fontSize: '0.85rem', mb: 1, display: 'block' }}>
                                Batch size (flags per round)
                            </FormLabel>
                            <Box sx={{ px: 1, maxWidth: 320 }}>
                                <Slider
                                    value={batchSize}
                                    onChange={setBatchSize}
                                    step={null}
                                    marks={BATCH_MARKS}
                                    min={5}
                                    max={20}
                                    valueLabelDisplay="auto"
                                />
                            </Box>
                        </Box>
                    )}
                </Box>

                <Divider sx={{ opacity: 0.6 }} />

                {/* Pool indicator + start */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                    {catalogLoading ? (
                        <CircularProgress size={20} />
                    ) : (
                        <Typography variant="body2" color={poolSize === 0 ? 'error' : 'text.secondary'}>
                            {poolSize === 0
                                ? 'No flags match your filters.'
                                : `${poolSize} flag${poolSize !== 1 ? 's' : ''} in pool`}
                        </Typography>
                    )}

                    <Button
                        variant="contained"
                        size="large"
                        disabled={!canStart || catalogLoading}
                        onClick={handleStart}
                        sx={{
                            ml: 'auto',
                            minWidth: 140,
                            ...gradientButtonSx,
                            '&.Mui-disabled': {
                                background: (theme) =>
                                    theme.palette.mode === 'dark'
                                        ? 'rgba(255,255,255,0.08)'
                                        : 'rgba(0,0,0,0.06)',
                            },
                        }}
                    >
                        Start Game
                    </Button>
                </Box>
            </Box>
        </Fade>
    )
}
