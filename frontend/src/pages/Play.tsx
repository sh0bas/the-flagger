import { useQuiz } from '../contexts/QuizContext'
import Lobby from '../components/quiz/Lobby'
import GameScreen from '../components/quiz/GameScreen'
import Summary from '../components/quiz/Summary'

export default function Play() {
    const { state } = useQuiz()

    if (state.phase === 'lobby') return <Lobby />
    if (state.phase === 'summary') return <Summary />
    return <GameScreen />
}
