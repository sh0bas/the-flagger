/** TypeScript type definitions. */
export interface User {
    id: string
    username: string
    email: string
    display_name: string | null
    avatar_url: string | null
    created_at: string
}

export interface LoginRequest {
    username: string
    password: string
}

export interface RegisterRequest {
    username: string
    email: string
    password: string
    display_name?: string
}

export interface TokenResponse {
    access_token: string
    refresh_token: string
    token_type: string
}

export interface GameSession {
    id: string
    game_mode: string
    regions: string[]
    score: number
    questions_count: number
    correct_count: number
    avg_response_ms: number
    max_streak: number
    played_at: string
}

export type FlagQuizMode = 'practice' | 'endless' | 'gauntlet'
export type Region = 'americas' | 'europe' | 'africa' | 'asia' | 'oceania'
export type Difficulty = 'easy' | 'medium' | 'hard'
export type EntityType = 'sovereign_state' | 'territory' | 'us_state'

export interface FlagEntity {
    id: number
    name: string
    capital: string
    region: Region
    flag_url: string
    iso_code: string
    alt_names: string[]
    difficulty: Difficulty
    entity_type: EntityType
    is_independent: boolean
}

export interface QuizFilters {
    regions: Region[]
    difficulties: Difficulty[]
    entityTypes: EntityType[]
}

export interface QuizConfig {
    mode: FlagQuizMode
    filters: QuizFilters
    batchSize: number
}

export interface QuizAnswer {
    entityId: number
    entityName: string
    userAnswer: string
    correct: boolean
    responseMs: number
    flagUrl: string
    isoCode: string
}

export type QuizPhase = 'lobby' | 'playing' | 'feedback' | 'summary'

export interface QuizState {
    phase: QuizPhase
    config: QuizConfig
    pool: FlagEntity[]
    queue: FlagEntity[]
    currentIndex: number
    currentEntity: FlagEntity | null
    lastAnswer: QuizAnswer | null
    answers: QuizAnswer[]
    streak: number
    maxStreak: number
    score: number
    // Practice-specific
    incorrectCarryForward: FlagEntity[]
    currentRound: number
    // Gauntlet-specific
    failed: boolean
    gauntletWon: boolean
}
