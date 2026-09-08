import React, { createContext, useContext, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchCatalog } from '../api/flagQuiz'
import { useQuizReducer } from '../hooks/useQuizReducer'
import type { QuizState, FlagEntity } from '../types'
import type { QuizAction } from '../hooks/useQuizReducer'

interface QuizContextValue {
    state: QuizState
    dispatch: React.Dispatch<QuizAction>
    catalog: FlagEntity[]
    catalogLoading: boolean
    catalogError: boolean
    filteredPool: FlagEntity[]
}

const QuizContext = createContext<QuizContextValue | null>(null)

export function QuizProvider({ children }: { children: React.ReactNode }) {
    const [state, dispatch] = useQuizReducer()

    // Fetch the full catalog once on mount (no auth needed for catalog endpoint)
    const {
        data: catalog = [],
        isLoading: catalogLoading,
        isError: catalogError,
    } = useQuery({
        queryKey: ['flagCatalog'],
        queryFn: () => fetchCatalog(),
        staleTime: 5 * 60 * 1000, // 5 min
    })

    // Derive filtered pool from catalog + active filters
    const filteredPool = useMemo(() => {
        const { regions, difficulties, entityTypes } = state.config.filters

        return catalog.filter((e) => {
            if (regions.length > 0 && !regions.includes(e.region)) return false
            if (difficulties.length > 0 && !difficulties.includes(e.difficulty)) return false
            if (entityTypes.length > 0 && !entityTypes.includes(e.entity_type)) return false
            return true
        })
    }, [catalog, state.config.filters])

    const value = useMemo(
        () => ({ state, dispatch, catalog, catalogLoading, catalogError, filteredPool }),
        [state, dispatch, catalog, catalogLoading, catalogError, filteredPool]
    )

    return <QuizContext.Provider value={value}>{children}</QuizContext.Provider>
}

export function useQuiz(): QuizContextValue {
    const ctx = useContext(QuizContext)
    if (!ctx) throw new Error('useQuiz must be used within a QuizProvider')
    return ctx
}
