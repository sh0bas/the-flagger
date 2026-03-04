import { useReducer } from 'react'
import type { FlagEntity, QuizAnswer, QuizConfig, QuizState } from '../types'

// ── helpers ──────────────────────────────────────────────────────────────────

export function normalizeForComparison(s: string): string {
    return s
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/[''`]/g, "'")
        .trim()
}

function isCorrectAnswer(userAnswer: string, entity: FlagEntity): boolean {
    const norm = normalizeForComparison(userAnswer)
    const targets = [entity.name, ...(entity.alt_names ?? [])].map(normalizeForComparison)
    return targets.includes(norm)
}

function shuffle<T>(arr: T[]): T[] {
    const a = [...arr]
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        ;[a[i], a[j]] = [a[j], a[i]]
    }
    return a
}

function calcScore(responseMs: number, streak: number): number {
    let pts = 100
    if (responseMs < 5000) pts += 50
    else if (responseMs < 10000) pts += 25
    if (streak >= 3) pts += streak * 10
    return pts
}

// ── actions ───────────────────────────────────────────────────────────────────

export type QuizAction =
    | { type: 'SET_CONFIG'; config: QuizConfig }
    | { type: 'START_GAME'; pool: FlagEntity[] }
    | { type: 'SUBMIT_ANSWER'; userAnswer: string; responseMs: number }
    | { type: 'ADVANCE' }   // called after feedback delay
    | { type: 'RESET_TO_LOBBY' }

// ── initial state ─────────────────────────────────────────────────────────────

const DEFAULT_CONFIG: QuizConfig = {
    mode: 'practice',
    filters: { regions: [], difficulties: [], entityTypes: ['sovereign_state'] },
    batchSize: 20,
}

export const initialState: QuizState = {
    phase: 'lobby',
    config: DEFAULT_CONFIG,
    pool: [],
    queue: [],
    currentIndex: 0,
    currentEntity: null,
    lastAnswer: null,
    answers: [],
    streak: 0,
    maxStreak: 0,
    score: 0,
    incorrectCarryForward: [],
    currentRound: 1,
    slidingHistory: [],
    failed: false,
    gauntletWon: false,
}

// ── endless: pick next flag honouring 30-flag sliding window ──────────────────

function pickNextEndless(pool: FlagEntity[], slidingHistory: number[]): FlagEntity | null {
    if (pool.length === 0) return null
    const available = pool.filter((e) => !slidingHistory.includes(e.id))
    const source = available.length > 0 ? available : pool
    return source[Math.floor(Math.random() * source.length)]
}

// ── reducer ───────────────────────────────────────────────────────────────────

function quizReducer(state: QuizState, action: QuizAction): QuizState {
    switch (action.type) {
        case 'SET_CONFIG':
            return { ...state, config: action.config }

        case 'START_GAME': {
            const { config } = state
            const pool = action.pool

            if (pool.length === 0) return state

            if (config.mode === 'practice') {
                const batchSize = Math.min(config.batchSize, pool.length)
                const queue = shuffle(pool).slice(0, batchSize)
                return {
                    ...initialState,
                    config,
                    pool,
                    queue,
                    currentEntity: queue[0],
                    currentIndex: 0,
                    phase: 'playing',
                    currentRound: 1,
                }
            }

            if (config.mode === 'gauntlet') {
                const queue = shuffle(pool)
                return {
                    ...initialState,
                    config,
                    pool,
                    queue,
                    currentEntity: queue[0],
                    currentIndex: 0,
                    phase: 'playing',
                }
            }

            // endless
            const first = pickNextEndless(pool, [])!
            return {
                ...initialState,
                config,
                pool,
                queue: [],
                currentEntity: first,
                currentIndex: 0,
                phase: 'playing',
            }
        }

        case 'SUBMIT_ANSWER': {
            if (!state.currentEntity || state.phase !== 'playing') return state

            const { userAnswer, responseMs } = action
            const entity = state.currentEntity
            const correct = isCorrectAnswer(userAnswer, entity)

            const newStreak = correct ? state.streak + 1 : 0
            const maxStreak = Math.max(state.maxStreak, newStreak)
            const pts = correct ? calcScore(responseMs, newStreak) : 0
            const newScore = state.score + pts

            const answer: QuizAnswer = {
                entityId: entity.id,
                entityName: entity.name,
                userAnswer,
                correct,
                responseMs,
                flagUrl: entity.flag_url,
            }

            const newAnswers = [...state.answers, answer]

            // Gauntlet: one wrong = fail
            if (state.config.mode === 'gauntlet' && !correct) {
                return {
                    ...state,
                    streak: 0,
                    maxStreak,
                    score: newScore,
                    answers: newAnswers,
                    lastAnswer: answer,
                    failed: true,
                    phase: 'feedback',
                }
            }

            // Endless: one wrong = game over
            if (state.config.mode === 'endless' && !correct) {
                return {
                    ...state,
                    streak: 0,
                    maxStreak,
                    score: newScore,
                    answers: newAnswers,
                    lastAnswer: answer,
                    phase: 'feedback',
                }
            }

            // Practice: track incorrect for carry-forward
            const incorrectCarryForward =
                state.config.mode === 'practice' && !correct
                    ? [...state.incorrectCarryForward, entity]
                    : state.incorrectCarryForward

            return {
                ...state,
                streak: newStreak,
                maxStreak,
                score: newScore,
                answers: newAnswers,
                lastAnswer: answer,
                incorrectCarryForward,
                phase: 'feedback',
            }
        }

        case 'ADVANCE': {
            const { config, currentIndex, queue, pool, incorrectCarryForward, failed, lastAnswer } =
                state

            // Gauntlet: fail terminates
            if (config.mode === 'gauntlet' && failed) {
                return { ...state, phase: 'summary' }
            }

            // Endless: wrong answer terminates
            if (config.mode === 'endless' && lastAnswer && !lastAnswer.correct) {
                return { ...state, phase: 'summary' }
            }

            if (config.mode === 'endless') {
                const newHistory = [
                    ...state.slidingHistory.slice(-29),
                    state.currentEntity!.id,
                ]
                const next = pickNextEndless(pool, newHistory)
                if (!next) return { ...state, phase: 'summary' }
                return {
                    ...state,
                    currentEntity: next,
                    currentIndex: state.currentIndex + 1,
                    slidingHistory: newHistory,
                    lastAnswer: null,
                    phase: 'playing',
                }
            }

            // Practice / Gauntlet advance through queue
            const nextIndex = currentIndex + 1

            if (config.mode === 'gauntlet') {
                if (nextIndex >= queue.length) {
                    // All flags done — win!
                    return { ...state, phase: 'summary', gauntletWon: true }
                }
                return {
                    ...state,
                    currentIndex: nextIndex,
                    currentEntity: queue[nextIndex],
                    lastAnswer: null,
                    phase: 'playing',
                }
            }

            // Practice
            if (nextIndex >= queue.length) {
                // End of batch
                if (incorrectCarryForward.length === 0) {
                    // No mistakes — done!
                    return { ...state, phase: 'summary' }
                }
                // Start next round with only the incorrect flags
                const newQueue = shuffle(incorrectCarryForward)
                return {
                    ...state,
                    queue: newQueue,
                    currentIndex: 0,
                    currentEntity: newQueue[0],
                    incorrectCarryForward: [],
                    currentRound: state.currentRound + 1,
                    lastAnswer: null,
                    phase: 'playing',
                }
            }

            return {
                ...state,
                currentIndex: nextIndex,
                currentEntity: queue[nextIndex],
                lastAnswer: null,
                phase: 'playing',
            }
        }

        case 'RESET_TO_LOBBY':
            return { ...initialState, config: state.config }

        default:
            return state
    }
}

export function useQuizReducer() {
    return useReducer(quizReducer, initialState)
}
