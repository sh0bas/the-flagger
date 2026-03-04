import apiClient from './client'
import type { FlagEntity, QuizFilters, QuizAnswer } from '../types'

export async function fetchCatalog(filters?: Partial<QuizFilters>): Promise<FlagEntity[]> {
    const params: Record<string, string> = {}
    if (filters?.regions?.length) params.regions = filters.regions.join(',')
    if (filters?.difficulties?.length) params.difficulties = filters.difficulties.join(',')
    if (filters?.entityTypes?.length) params.entity_types = filters.entityTypes.join(',')

    const response = await apiClient.get<FlagEntity[]>('/api/countries/catalog', { params })
    return response.data
}

export async function fetchAutocomplete(
    search: string,
    filters?: Partial<QuizFilters>,
    limit = 8
): Promise<string[]> {
    if (!search || search.length < 1) return []

    const params: Record<string, string | number> = { search, limit }
    if (filters?.regions?.length) params.regions = filters.regions.join(',')
    if (filters?.entityTypes?.length) params.entity_types = filters.entityTypes.join(',')
    if (filters?.difficulties?.length) params.difficulties = filters.difficulties.join(',')

    const response = await apiClient.get<string[]>('/api/countries', { params })
    return response.data
}

export interface SaveResultPayload {
    game_mode: string
    regions: string[]
    entity_types: string[]
    difficulties: string[]
    score: number
    correct_count: number
    questions_count: number
    max_streak: number
    avg_response_ms: number
    answers: Array<{
        country_id: number
        user_answer: string
        correct: boolean
        response_ms: number
    }>
}

export function buildSavePayload(
    answers: QuizAnswer[],
    config: { mode: string; filters: QuizFilters },
    score: number,
    maxStreak: number
): SaveResultPayload {
    const totalMs = answers.reduce((sum, a) => sum + a.responseMs, 0)
    const avgMs = answers.length > 0 ? Math.round(totalMs / answers.length) : 0

    return {
        game_mode: config.mode,
        regions: config.filters.regions,
        entity_types: config.filters.entityTypes,
        difficulties: config.filters.difficulties,
        score,
        correct_count: answers.filter((a) => a.correct).length,
        questions_count: answers.length,
        max_streak: maxStreak,
        avg_response_ms: avgMs,
        answers: answers.map((a) => ({
            country_id: a.entityId,
            user_answer: a.userAnswer,
            correct: a.correct,
            response_ms: a.responseMs,
        })),
    }
}

export async function saveResult(payload: SaveResultPayload): Promise<void> {
    await apiClient.post('/api/games/save-result', payload)
}
