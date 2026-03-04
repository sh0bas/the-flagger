import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import apiClient from '../api/client'
import { User, LoginRequest, RegisterRequest, TokenResponse } from '../types'

interface AuthContextType {
    user: User | null
    loading: boolean
    login: (credentials: LoginRequest) => Promise<void>
    register: (data: RegisterRequest) => Promise<void>
    logout: () => void
    isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider')
    }
    return context
}

interface AuthProviderProps {
    children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    // Load user on mount if tokens exist
    useEffect(() => {
        const loadUser = async () => {
            const token = localStorage.getItem('access_token')
            if (token) {
                try {
                    const response = await apiClient.get<User>('/api/users/me')
                    setUser(response.data)
                } catch (error) {
                    // Token invalid, clear storage
                    localStorage.removeItem('access_token')
                    localStorage.removeItem('refresh_token')
                }
            }
            setLoading(false)
        }

        loadUser()
    }, [])

    const login = async (credentials: LoginRequest) => {
        const response = await apiClient.post<TokenResponse>('/api/auth/login', credentials)
        const { access_token, refresh_token } = response.data

        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        // Fetch user data
        const userResponse = await apiClient.get<User>('/api/users/me')
        setUser(userResponse.data)
    }

    const register = async (data: RegisterRequest) => {
        const response = await apiClient.post<TokenResponse>('/api/auth/register', data)
        const { access_token, refresh_token } = response.data

        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        // Fetch user data
        const userResponse = await apiClient.get<User>('/api/users/me')
        setUser(userResponse.data)
    }

    const logout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setUser(null)
    }

    const value = {
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
    }

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
