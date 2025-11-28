# Flagger

## Product Requirements Document

| Field   | Value         |
|---------|---------------|
| Version | 1.0           |
| Date    | November 2025 |
| Status  | Draft         |

---

## 1. Executive Summary

Flagger is a web-based geography education platform that provides engaging, game-based learning experiences centered on world geography. The application offers three distinct game modes focused on flags, countries, and capitals, with comprehensive social features including user accounts, friend systems, and competitive leaderboards. The platform supports regional filtering and multiple leaderboard timeframes to encourage both casual play and competitive engagement.

---

## 2. Product Overview

### 2.1 Vision Statement

To create an accessible, entertaining, and educational platform where users can test and improve their world geography knowledge through engaging gameplay while competing with friends and the global community.

### 2.2 Target Audience

- Students (ages 10+) seeking to learn world geography
- Geography enthusiasts and trivia game players
- Educators looking for classroom engagement tools
- Casual gamers interested in educational content

### 2.3 Technology Stack

**Frontend:**
- React 18+ with Vite build tool
- TypeScript (strict mode enabled)
- Material-UI (MUI) component library v5+
- React Router for navigation
- Axios or TanStack Query for API communication

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM (Object-Relational Mapping) with async support
- Alembic for database migrations
- Pydantic v2 for data validation
- JWT (JSON Web Token) for authentication

**Infrastructure:**
- Docker Compose for containerization
- PostgreSQL 15+ database
- Redis (optional, for session caching and leaderboard optimization)

---

## 3. Game Modes

### 3.1 Flag to Country

**Description:** Users are presented with a country's flag and must identify the corresponding country name.

**Gameplay Flow:**
1. A flag image is displayed prominently in the center of the screen
2. User types their answer in an input field with autocomplete functionality
3. User submits answer via Enter key or Submit button
4. Correct/incorrect animation plays based on result
5. Next flag is presented automatically after brief delay

### 3.2 Country to Capital

**Description:** Users are shown a country name and must identify its capital city.

**Gameplay Flow:**
1. Country name is displayed as the prompt
2. User types the capital city with autocomplete assistance
3. Answer submission and feedback follows same pattern as Flag to Country
4. Country's flag may be shown as supplementary visual context

### 3.3 Capital to Country

**Description:** Users are shown a capital city and must identify which country it belongs to.

**Gameplay Flow:**
1. Capital city name is displayed as the prompt
2. User types the country name with autocomplete assistance
3. Standard submission and feedback flow applies

### 3.4 Regional Filtering

Before starting any game mode, users can select which geographic regions to include. Available regions:

- **Americas** – North America, Central America, Caribbean, and South America combined
- **Europe** – All European nations including transcontinental countries primarily in Europe
- **Africa** – All African nations
- **Asia** – All Asian nations including Middle East and Central Asia
- **Oceania** – Australia, New Zealand, Pacific Islands, and associated territories

Users may select one or more regions. Selecting no regions defaults to "All Regions" (worldwide).

---

## 4. Autocomplete System

### 4.1 Core Behavior

The autocomplete system provides real-time suggestions as users type, significantly reducing friction and typo-related frustration.

**Activation:**
- Suggestions appear after typing 2+ characters
- Tab key accepts the top suggestion and places it in the input field
- Enter key accepts the top suggestion AND submits the answer
- Arrow keys allow navigation through suggestion list

### 4.2 Prioritization Algorithm

**Critical Requirement:** The autocomplete must prioritize exact prefix matches over partial/fuzzy matches.

**Priority Order:**
1. **Exact match** – Input exactly matches a valid answer (case-insensitive)
2. **Exact prefix match** – Input matches the beginning of an answer
3. **Word-boundary match** – Input matches the start of any word in a multi-word answer
4. **Substring match** – Input appears anywhere within the answer (lowest priority)

**Required Behavior Examples:**

| User Types | Must Suggest First | Must NOT Suggest First |
|------------|-------------------|------------------------|
| Mali | Mali | Somalia |
| Dominica | Dominica | Dominican Republic |
| Niger | Niger | Nigeria |
| Guinea | Guinea | Equatorial Guinea, Guinea-Bissau, Papua New Guinea |
| Congo | Congo (alphabetically first) | Democratic Republic of the Congo (unless typed exactly) |

### 4.3 Implementation Notes

- Autocomplete list should be filtered to only include countries from selected regions
- For Capital modes, autocomplete searches capital cities, not country names
- Maximum 8 suggestions displayed at once
- Suggestions update with each keystroke (debounced at 50ms)
- Matching text within suggestions should be visually highlighted (bold or underlined)

---

## 5. Scoring System

### 5.1 Point Calculation

Points are awarded based on correctness and speed of response.

| Factor | Points |
|--------|--------|
| Correct answer | 100 base points |
| Speed bonus (answer within 5 seconds) | +50 points |
| Speed bonus (answer within 10 seconds) | +25 points |
| Streak bonus (3+ correct in a row) | +10 points per streak count |
| Incorrect answer | 0 points, streak reset |

### 5.2 Game Session Structure

- Each session consists of 20 questions (configurable)
- No duplicate questions within a single session
- Session score = sum of all question scores
- Final screen shows: total score, accuracy percentage, average response time, longest streak
- Scores are submitted to leaderboards upon session completion (authenticated users only)

---

## 6. Visual Feedback & Animations

### 6.1 Correct Answer Animation

A satisfying visual confirmation for correct guesses:

- Input field border flashes green
- Checkmark icon appears with scale-in animation (0 to 100% over 200ms)
- Subtle confetti particle burst from answer area
- Points earned display with count-up animation
- Duration: 800ms before transitioning to next question

### 6.2 Incorrect Answer Animation

Clear but non-punishing feedback for incorrect guesses:

- Input field border flashes red
- Horizontal shake animation (3 oscillations over 300ms)
- X icon appears with fade-in
- Correct answer revealed below input with highlight
- Duration: 1500ms to allow user to read correct answer

### 6.3 Additional UI Animations

- Question transitions: Fade-out/fade-in with slight vertical movement
- Flag images: Smooth crossfade between questions
- Streak counter: Pulse animation on increment
- Score updates: Number roll animation
- All animations should respect `prefers-reduced-motion` media query

---

## 7. User Account System

### 7.1 Registration & Authentication

**Registration Requirements:**
- Username (3-20 characters, alphanumeric and underscores only, unique)
- Email address (valid format, unique)
- Password (minimum 8 characters, at least one uppercase, one lowercase, one number)
- Display name (optional, shown on leaderboards)

**Authentication Flow:**
- JWT-based authentication with access tokens (15-minute expiry) and refresh tokens (7-day expiry)
- Passwords hashed using bcrypt with appropriate work factor
- Email verification required before account activation
- Password reset via email with time-limited tokens

### 7.2 User Profile

Each user profile displays:

- Username and display name
- Avatar (default generated from username, or custom upload)
- Member since date
- Statistics: total games played, overall accuracy, favorite game mode
- Best scores per game mode and region
- Recent game history (last 10 sessions)

### 7.3 Friend System

**Friend Requests:**
- Users can send friend requests by username search
- Pending requests shown in notification center
- Recipients can accept or decline requests
- Maximum 500 friends per user

**Friend Features:**
- View friends' profiles and statistics
- Friends-only leaderboard filter
- Activity feed showing friends' recent games and achievements
- Remove friend option (no notification sent to removed user)

### 7.4 Block System

**Blocking Behavior:**
- Blocked users cannot send friend requests
- Blocked users are hidden from all leaderboards for the blocking user
- Existing friendships are automatically removed when blocking
- Blocked users cannot view the blocking user's profile
- No notification sent to blocked user
- Users can unblock from settings; this does not restore previous friendship

---

## 8. Leaderboard System

### 8.1 Leaderboard Structure

Leaderboards are organized by three dimensions:

**Game Mode (3 options):**
- Flag to Country
- Country to Capital
- Capital to Country

**Time Period (4 options):**
- **Daily** – Resets at 00:00 UTC
- **Weekly** – Resets Monday 00:00 UTC
- **Monthly** – Resets 1st of month 00:00 UTC
- **All-Time** – Cumulative since account creation

**Region (6 options):**
- All Regions (worldwide)
- Americas
- Europe
- Africa
- Asia
- Oceania

**Total combinations:** 3 modes × 4 periods × 6 regions = 72 distinct leaderboards

### 8.2 Leaderboard Display

- Top 100 users displayed per leaderboard
- Current user's rank always visible (even if outside top 100)
- Each entry shows: rank, username/display name, avatar, score, games played
- Toggle to show "Friends Only" (displays only mutual friends)
- Clicking a user opens their public profile

### 8.3 Score Aggregation

- **Daily/Weekly/Monthly:** Sum of best score per day within the period
- **All-Time:** Highest single-session score achieved

---

## 9. Database Schema

### 9.1 Core Tables

#### `users`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| username | VARCHAR(20) | Unique, indexed |
| email | VARCHAR(255) | Unique, indexed |
| password_hash | VARCHAR(255) | bcrypt hash |
| display_name | VARCHAR(50) | Nullable |
| avatar_url | VARCHAR(500) | Nullable |
| email_verified | BOOLEAN | Default false |
| created_at | TIMESTAMP | Account creation time |
| updated_at | TIMESTAMP | Last modification |

#### `game_sessions`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key → users |
| game_mode | ENUM | flag_to_country, country_to_capital, capital_to_country |
| regions | VARCHAR[] | Array of selected regions |
| score | INTEGER | Final session score |
| questions_count | INTEGER | Total questions |
| correct_count | INTEGER | Correct answers |
| avg_response_ms | INTEGER | Average response time |
| max_streak | INTEGER | Longest streak achieved |
| played_at | TIMESTAMP | Session timestamp, indexed |

#### `friendships`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| requester_id | UUID | Foreign key → users (sender) |
| addressee_id | UUID | Foreign key → users (recipient) |
| status | ENUM | pending, accepted, declined |
| created_at | TIMESTAMP | Request time |
| updated_at | TIMESTAMP | Last status change |

#### `blocks`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| blocker_id | UUID | Foreign key → users (who blocked) |
| blocked_id | UUID | Foreign key → users (who is blocked) |
| created_at | TIMESTAMP | Block time |

#### `countries`

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| name | VARCHAR(100) | Official country name |
| capital | VARCHAR(100) | Capital city name |
| region | ENUM | americas, europe, africa, asia, oceania |
| flag_url | VARCHAR(500) | Path to flag image |
| iso_code | CHAR(2) | ISO 3166-1 alpha-2 code |
| alt_names | VARCHAR[] | Alternative/common names |

---

## 10. API Endpoints

### 10.1 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Create new user account |
| POST | /api/auth/login | Authenticate and receive tokens |
| POST | /api/auth/refresh | Refresh access token |
| POST | /api/auth/logout | Invalidate refresh token |
| POST | /api/auth/verify-email | Verify email with token |
| POST | /api/auth/forgot-password | Request password reset email |
| POST | /api/auth/reset-password | Reset password with token |

### 10.2 User & Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users/me | Get current user profile |
| PATCH | /api/users/me | Update current user profile |
| GET | /api/users/{username} | Get public profile by username |
| GET | /api/users/search?q={query} | Search users by username |

### 10.3 Friends & Blocks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/friends | List all friends |
| GET | /api/friends/requests | List pending friend requests |
| POST | /api/friends/request/{user_id} | Send friend request |
| POST | /api/friends/accept/{request_id} | Accept friend request |
| POST | /api/friends/decline/{request_id} | Decline friend request |
| DELETE | /api/friends/{user_id} | Remove friend |
| GET | /api/blocks | List blocked users |
| POST | /api/blocks/{user_id} | Block user |
| DELETE | /api/blocks/{user_id} | Unblock user |

### 10.4 Game

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/game/start | Start new game session |
| GET | /api/game/{session_id}/question | Get current question |
| POST | /api/game/{session_id}/answer | Submit answer |
| GET | /api/game/{session_id}/results | Get final session results |
| GET | /api/game/history | Get user's game history |
| GET | /api/countries | Get all countries (for autocomplete) |
| GET | /api/capitals | Get all capitals (for autocomplete) |

### 10.5 Leaderboards

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/leaderboard?mode={mode}&period={period}&region={region} | Get leaderboard |
| GET | /api/leaderboard/friends?mode={mode}&period={period}&region={region} | Friends leaderboard |
| GET | /api/leaderboard/rank?mode={mode}&period={period}&region={region} | Current user's rank |

---

## 11. Docker Configuration

### 11.1 Services

The Docker Compose configuration includes the following services:

- **frontend** – Node.js container serving Vite dev server (dev) or nginx with built assets (prod)
- **backend** – Python container running FastAPI with Uvicorn
- **db** – PostgreSQL 15 container with persistent volume
- **redis** – Redis container for caching (optional)

### 11.2 Environment Variables

| Variable | Purpose |
|----------|---------|
| DATABASE_URL | PostgreSQL connection string |
| SECRET_KEY | JWT signing key (min 32 characters) |
| REDIS_URL | Redis connection string |
| SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS | Email service configuration |
| FRONTEND_URL | Frontend URL for CORS and emails |
| VITE_API_URL | Backend API URL for frontend |

---

## 12. Non-Functional Requirements

### 12.1 Performance

- API response time: < 200ms for 95th percentile
- Autocomplete latency: < 50ms perceived delay
- Initial page load: < 3 seconds on 3G connection
- Leaderboard queries optimized with proper indexing and caching

### 12.2 Security

- All passwords hashed with bcrypt (work factor 12)
- HTTPS required in production
- CORS (Cross-Origin Resource Sharing) configured for frontend domain only
- Rate limiting: 100 requests/minute per IP for unauthenticated, 300 for authenticated
- SQL injection prevention via parameterized queries (SQLAlchemy)
- XSS (Cross-Site Scripting) prevention via React's default escaping

### 12.3 Accessibility

- WCAG (Web Content Accessibility Guidelines) 2.1 AA compliance
- Keyboard navigation fully supported
- Screen reader compatibility with ARIA labels
- Color contrast ratios meeting AA standards
- Animations respect `prefers-reduced-motion`

### 12.4 Scalability

- Stateless backend design for horizontal scaling
- Database connection pooling
- Redis caching for leaderboard queries
- CDN (Content Delivery Network) for static assets and flag images

---

## 13. Future Considerations

Features to consider for future versions:

- OAuth integration (Google, Discord, GitHub)
- Additional game modes (Flag to Capital, Map Click, Outline to Country)
- Achievements and badges system
- Multiplayer head-to-head mode
- Mobile applications (iOS/Android)
- Localization/internationalization support
- Custom game creation (user-defined country subsets)
- Educational mode with learning resources

---

## 14. Data Sources

Recommended sources for country data:

- **Country Information:** REST Countries API (restcountries.com) or pre-seeded database
- **Flag Images:** FlagCDN (flagcdn.com) or self-hosted SVG collection
- **Alternative Names:** GeoNames database for common alternative country names

*Note: Country data should be seeded into the database at deployment and updated periodically, not fetched at runtime.*

---

## Appendix A: Country Counts by Region

| Region | Approximate Country Count |
|--------|---------------------------|
| Americas | 35 countries |
| Europe | 44 countries |
| Africa | 54 countries |
| Asia | 49 countries |
| Oceania | 14 countries |
| **Total** | **~196 countries** |

---

*— End of Document —*