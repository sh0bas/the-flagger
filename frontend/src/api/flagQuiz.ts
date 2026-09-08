import apiClient from './client'
import type { FlagEntity, QuizAnswer, QuizFilters } from '../types'

export async function fetchCatalog(): Promise<FlagEntity[]> {
    const response = await apiClient.get<FlagEntity[]>('/api/countries/catalog')
    return response.data
}

/** Payload for a finished run. Carries no score — the server grades it. */
export interface SaveResultPayload {
    game_mode: string
    regions: string[]
    entity_types: string[]
    difficulties: string[]
    answers: Array<{
        country_id: number
        user_answer: string
        response_ms: number
    }>
}

export interface SavedGame {
    id: string
    game_mode: string
    score: number
    questions_count: number
    correct_count: number
    avg_response_ms: number
    max_streak: number
    played_at: string
}

export function buildSavePayload(
    answers: QuizAnswer[],
    config: { mode: string; filters: QuizFilters }
): SaveResultPayload {
    return {
        game_mode: config.mode,
        regions: config.filters.regions,
        entity_types: config.filters.entityTypes,
        difficulties: config.filters.difficulties,
        answers: answers.map((a) => ({
            country_id: a.entityId,
            user_answer: a.userAnswer,
            response_ms: a.responseMs,
        })),
    }
}

export async function saveResult(payload: SaveResultPayload): Promise<SavedGame> {
    const response = await apiClient.post<SavedGame>('/api/games/save-result', payload)
    return response.data
}

export async function fetchHistory(limit = 20): Promise<SavedGame[]> {
    const response = await apiClient.get<SavedGame[]>('/api/games/history', { params: { limit } })
    return response.data
}
