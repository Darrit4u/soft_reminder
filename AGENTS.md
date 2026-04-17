
# Telegram Habit & Gratitude Bot — Dev Blueprint

## 1. Purpose

This document is the main development blueprint for a Telegram bot that helps users:

- maintain very simple daily habits
- keep a gratitude journal
- receive soft, psychologically supportive reminders
- review weekly progress without guilt or pressure
- optionally store short weekly emotional notes

This bot is intentionally **supportive, gentle, and psychologically safe**.  
It should feel like a calm assistant, not a productivity tracker.

---

## 2. Product Principles

## 2.1. Core product goal

Help users build stability through small repeated actions, especially during:

- fatigue
- low mood
- emotional overload
- mild depressive episodes
- loss of motivation

## 2.2. Psychological priority

Every bot message must prioritize:

1. reducing pressure
2. avoiding shame
3. normalizing inconsistency
4. lowering activation energy
5. reinforcing that small steps count

## 2.3. Tone constraints

The bot must never sound:

- judging
- demanding
- disappointed
- manipulative in a harsh way
- overly cheerful in a fake way
- childish or patronizing

The bot should sound:

- warm
- calm
- supportive
- respectful
- steady
- emotionally intelligent

## 2.4. Forbidden language patterns

Never use patterns like:

- "Ты не сделал..."
- "Почему ты не ответил?"
- "Нужно стараться больше"
- "Ты опять пропустил"
- "Ты должен"
- "Надо обязательно"

Prefer:

- "Это нормально"
- "Можно начать с малого"
- "Даже один шаг имеет значение"
- "Можно просто продолжить сегодня"
- "Стабильность тоже важна"

---

## 3. MVP Scope

The first working version must include only these modules:

1. **Gratitude Journal**
2. **Habit Tracker**
3. **Weekly Summary**
4. **Weekly Feelings Note**
5. **Supportive Re-engagement**

Do **not** implement in MVP:

- RPG mechanics
- XP / coins / avatars
- social features
- advanced AI analytics
- complex NLP
- mood diagnosis
- mental health claims
- high-pressure streak mechanics

---

## 4. Main User Features

## 4.1. Gratitude Journal

Daily practice where user sends one message containing a gratitude list.

Rules:

- preferred format: numbered list
- fallback format: lines without numbering
- ideal target: 10 items
- target is soft, not mandatory
- even 1 item counts as valid practice

Bot computes:

- count of gratitude items
- daily participation
- weekly totals
- growth/stability across the week

---

## 4.2. Habit Tracker

User chooses habits from a default list or adds custom ones.

Important rules:

- recommend adding **one new habit per week**
- allow adding more than one if user insists
- habits must be simple and concrete
- every day bot reminds only about **unfinished** habits
- user can mark habits:
  - via button
  - via free text message

---

## 4.3. Weekly Summary

Sent automatically once per week or by request.

Includes:

- gratitude stats
- habit stats
- optional weekly feelings note
- supportive interpretation
- psychologically safe summary

---

## 4.4. Weekly Feelings Note

At the end of week the bot may ask user to describe how the week felt.

Rules:

- free text
- bot responds only with gratitude / acknowledgement
- no analysis
- user can later request archive of recent weekly notes

---

## 4.5. Re-engagement

If user becomes inactive:

- bot lowers expectations
- bot shortens calls to action
- bot avoids pressure
- bot invites user back with one tiny step

---

## 5. Technical Architecture

Recommended architecture:

- Telegram Bot API layer
- Application service layer
- Domain logic layer
- Storage layer
- Scheduler / jobs layer
- Message rendering engine
- Message content JSON file

Suggested stack examples:

- **Node.js / TypeScript** with Telegraf + Prisma + PostgreSQL
- or **Python** with aiogram + SQLAlchemy + PostgreSQL

This blueprint is implementation-agnostic, but examples assume a service-oriented structure.

---

## 6. Project Structure

Example structure:

```text
project/
  src/
    app/
      bot.ts
      webhook.ts
      polling.ts

    config/
      env.ts
      constants.ts

    domain/
      users/
        user.types.ts
        user.service.ts
      gratitude/
        gratitude.types.ts
        gratitude.service.ts
        gratitude.parser.ts
      habits/
        habit.types.ts
        habit.service.ts
        habit.parser.ts
        habit.stats.ts
      feelings/
        feelings.types.ts
        feelings.service.ts
      weekly-summary/
        weekly-summary.service.ts
        weekly-summary.renderer.ts
        weekly-summary.types.ts
      engagement/
        engagement.service.ts

    messaging/
      messages.json
      message-engine.ts
      template-renderer.ts
      message-selection.ts

    telegram/
      command.handlers.ts
      text.handlers.ts
      callback.handlers.ts
      keyboards.ts

    jobs/
      daily-reminders.job.ts
      weekly-summary.job.ts
      inactivity-check.job.ts

    storage/
      db.ts
      repositories/
        user.repository.ts
        gratitude.repository.ts
        habit.repository.ts
        habit-completion.repository.ts
        feelings.repository.ts

    utils/
      dates.ts
      random.ts
      logger.ts
      text.ts

  prisma/ or migrations/
  README.md
````

---

## 7. Domain Model

## 7.1. User

```ts
type User = {
  id: string
  telegramId: string
  username?: string
  firstName?: string
  timezone: string
  locale: string
  onboardingCompleted: boolean

  engagementState: 'active' | 'low_activity' | 'inactive'

  preferredReminderMorning?: string
  preferredReminderDay?: string
  preferredReminderEvening?: string
  weeklySummaryDay?: number
  weeklySummaryTime?: string

  createdAt: Date
  updatedAt: Date
  lastActivityAt?: Date
}
```

---

## 7.2. Habit

```ts
type Habit = {
  id: string
  userId: string
  title: string
  normalizedTitle: string
  source: 'default' | 'custom'
  active: boolean
  createdAt: Date
  archivedAt?: Date

  stage: 'adaptation' | 'stable'
}
```

Rules:

* `stage = adaptation` for first 7 days after creation
* after 7 days -> `stable`

---

## 7.3. HabitCompletion

```ts
type HabitCompletion = {
  id: string
  userId: string
  habitId: string
  date: string // YYYY-MM-DD in user timezone
  completed: boolean
  completedAt?: Date
  source: 'button' | 'text' | 'admin'
}
```

Constraint:

* unique `(habitId, date)`

---

## 7.4. GratitudeEntry

```ts
type GratitudeEntry = {
  id: string
  userId: string
  date: string // YYYY-MM-DD in user timezone
  rawText: string
  itemsCount: number
  parsedItems?: string[]
  createdAt: Date
}
```

Constraint:

* one entry per user per date for MVP, or multiple entries merged logically

Recommended MVP rule:

* allow multiple gratitude messages per day
* aggregate into one daily total for stats
* but simplest implementation can store multiple entries and sum them by day

---

## 7.5. WeeklyFeelingEntry

```ts
type WeeklyFeelingEntry = {
  id: string
  userId: string
  weekStartDate: string // YYYY-MM-DD
  weekEndDate: string // YYYY-MM-DD
  rawText: string
  createdAt: Date
}
```

Constraint:

* max 1 weekly feeling entry per user per week in MVP

---

## 7.6. UserState / InteractionState

To handle conversational waiting states:

```ts
type UserInteractionState =
  | 'idle'
  | 'waiting_for_custom_habit'
  | 'waiting_for_gratitude'
  | 'waiting_for_weekly_feelings'
```

Store separately:

```ts
type UserSessionState = {
  userId: string
  state: UserInteractionState
  payload?: Record<string, unknown>
  updatedAt: Date
}
```

---

## 8. Default Habit Catalog

MVP default habits:

```ts
const DEFAULT_HABITS = [
  'Почистить зубы',
  'Умыться',
  'Сделать короткую зарядку',
  'Выпить стакан воды утром',
  'Проветрить комнату',
  'Лечь спать вовремя',
  'Сделать 2 минуты движения'
]
```

Rules:

* user picks one to start
* after 7 days, bot offers to add one more
* user can add custom habits any time

---

## 9. Main Commands

Required commands:

* `/start`
* `/help`
* `/gratitude`
* `/habits`
* `/add_habit`
* `/stats`
* `/feelings`
* `/settings`

Optional future commands:

* `/pause`
* `/resume`
* `/archive_habit`

---

## 10. Free Text Intents

The bot must classify free text into simple intent buckets.

## 10.1. Intent types

```ts
type IncomingTextIntent =
  | 'gratitude_list'
  | 'habit_completion'
  | 'weekly_feelings'
  | 'custom_habit_creation'
  | 'unknown'
```

## 10.2. Intent priority order

When receiving text, resolve in this order:

1. if session state expects something -> use session state
2. detect gratitude list
3. detect habit completion
4. detect custom habit input
5. otherwise unknown

---

## 11. Gratitude Logic

## 11.1. Input format

Preferred:

```text
1. Спасибо за...
2. Спасибо за...
3. Спасибо за...
```

Fallback:

```text
Спасибо за...
Спасибо за...
Спасибо за...
```

## 11.2. Parsing rules

Function:

```ts
parseGratitudeItems(text: string): string[]
```

Logic:

1. normalize line breaks
2. split into lines
3. trim empty lines
4. if lines contain numbering pattern (`^\d+[\.\)]\s+`) -> parse each numbered line
5. else parse each non-empty line as separate item
6. if still only one meaningful line -> count as 1 item

Example regex:

```ts
/^\s*\d+[\.\)]\s+(.+)$/
```

## 11.3. Validity

A gratitude entry is valid if:

* parsed item count >= 1

## 11.4. Response classification

By count:

* `1-2` -> minimal step
* `3-5` -> good start
* `6-9` -> deep engagement
* `10+` -> full practice

## 11.5. Gratitude response keys

From `messages.json`:

* `gratitude.responses.count_1_2`
* `gratitude.responses.count_3_5`
* `gratitude.responses.count_6_9`
* `gratitude.responses.count_10_plus`
* `gratitude.responses.single_line_fallback`

---

## 12. Habit Logic

## 12.1. Habit creation rules

User can create habit via:

* `/add_habit`
* button "Добавить привычку"
* text after bot asks for custom habit

Validation rules:

* must be short
* must be concrete
* recommended max length: 80 chars
* reject empty input
* reject extremely vague phrases like:

  * "быть лучше"
  * "жить нормально"
  * "стать продуктивным"

Basic validation heuristic:

* minimum 2 characters
* maximum 80
* no only emojis
* optionally warn if contains too many abstract words

## 12.2. Habit completion methods

User can complete a habit by:

1. pressing inline button
2. sending text:

   * "сделал зарядку"
   * "выпил воду"
   * "умылся"
   * "почистил зубы"

## 12.3. Habit completion parser

Function:

```ts
detectHabitCompletion(text: string, activeHabits: Habit[]): Habit | null
```

Approach for MVP:

* normalize text
* tokenize / lowercase
* compare against:

  * habit title
  * normalized habit title
  * synonym dictionary
  * common verb forms

Example synonym map:

```ts
const HABIT_SYNONYMS = {
  'Сделать короткую зарядку': ['зарядка', 'сделал зарядку', 'размялся'],
  'Выпить стакан воды утром': ['выпил воду', 'вода', 'стакан воды'],
  'Почистить зубы': ['почистил зубы', 'зубы'],
  'Умыться': ['умылся', 'умылась', 'умыл лицо']
}
```

If one habit matches confidently -> mark complete.

If multiple habits ambiguous:

* ask short clarification
* but in MVP it is acceptable to ignore ambiguous text and reply neutrally

## 12.4. Completion constraints

If already completed today:

* do not create duplicate row
* reply gently:

  * "Эта привычка уже отмечена на сегодня ✅"

## 12.5. Daily habit completion states

For each user and day:

* some habits completed
* some pending
* all done

This affects reply selection:

* first completed today -> `habits.responses.completed_first_today`
* generic completion -> `habits.responses.completed_generic`
* last remaining habit completed -> `habits.responses.completed_last_today`

---

## 13. Weekly Feelings Logic

## 13.1. Prompt

At weekly summary end, optionally ask:

* "Если хочешь, можешь коротко описать, как прошла эта неделя."

## 13.2. Handling user response

If session state is `waiting_for_weekly_feelings`:

* save text as weekly feeling note
* reply with:

  * `feelings_journal.response`

No analysis. No sentiment classification. No advice.

## 13.3. Archive retrieval

Command:

* `/feelings`

Output:

* recent 4 weekly feeling entries, newest first

If empty:

* `feelings_journal.empty_archive`

---

## 14. Weekly Summary Logic

## 14.1. Weekly period

Use user timezone.

Define week as:

* Monday 00:00 to Sunday 23:59:59
  or
* any chosen week window, but must be consistent

Recommended: ISO week Monday-Sunday.

## 14.2. Gratitude weekly stats

Function:

```ts
getWeeklyGratitudeStats(userId: string, weekStart: string, weekEnd: string)
```

Returns:

```ts
type WeeklyGratitudeStats = {
  totalItems: number
  daysWithEntries: number
  avgPerDay: number
  maxItemsDay: number
  first3DaysAvg: number
  last3DaysAvg: number
  dynamicType: 'growth' | 'stable' | 'irregular' | 'low_data'
}
```

### Calculation notes

* `avgPerDay = totalItems / 7`
* `first3DaysAvg` = average of first 3 days in week
* `last3DaysAvg` = average of last 3 days in week
* `dynamicType`:

  * `low_data` if `daysWithEntries < 2` or `totalItems < 3`
  * `growth` if `last3DaysAvg > first3DaysAvg + threshold`
  * `stable` if abs difference within threshold
  * `irregular` otherwise

Recommended threshold:

```ts
const GRATITUDE_STABILITY_THRESHOLD = 1.0
```

## 14.3. Habit weekly stats

Function:

```ts
getWeeklyHabitStats(userId: string, weekStart: string, weekEnd: string)
```

Returns:

```ts
type HabitWeeklyItemStats = {
  habitId: string
  habitName: string
  completedDays: number
  totalDays: number
  completionRate: number
  currentStreak: number
  bestStreak: number
  stage: 'adaptation' | 'stable'
}

type WeeklyHabitStats = {
  habits: HabitWeeklyItemStats[]
  strongType: 'strong' | 'mixed' | 'weak' | 'empty'
  mostConsistentHabitName?: string
  hasAdaptationHabits: boolean
}
```

### Completion rate

```ts
completionRate = Math.round((completedDays / totalDays) * 100)
```

### Weekly strong type heuristic

If no active habits -> `empty`

Else based on average completion rate across active habits:

* `strong` if avg >= 70
* `mixed` if avg between 35 and 69
* `weak` if avg < 35

## 14.4. Overall week classification

Function:

```ts
classifyOverallWeek(gratitudeStats, habitStats): 'strong_week' | 'mixed_week' | 'weak_week' | 'empty_week'
```

Suggested logic:

* `empty_week` if no gratitude entries and no habit completions
* `strong_week` if habits strong OR gratitude meaningful and stable/growth
* `mixed_week` as default
* `weak_week` if low overall activity but not fully empty

This classification selects:

* weekly header
* weekly closing

---

## 15. Message Engine

All content must live in `messages.json`.

## 15.1. Engine responsibilities

Message engine should:

1. load message JSON
2. select random variant from a given path
3. interpolate placeholders
4. avoid exact recent repetition if possible

## 15.2. Function signatures

```ts
getMessage(path: string, placeholders?: Record<string, string | number>): string
getRandomVariant(items: string[]): string
renderTemplate(template: string, placeholders: Record<string, string | number>): string
```

Optional advanced version:

```ts
getMessage(path: string, options?: {
  placeholders?: Record<string, string | number>
  excludeRecent?: string[]
})
```

## 15.3. Placeholder syntax

Use:

```text
{{habit_name}}
{{total_items}}
{{avg_per_day}}
```

## 15.4. Deduplication strategy

MVP:

* keep last 10 sent message keys per user
* when selecting message, try not to reuse same exact string if alternatives exist

---

## 16. Telegram UI

## 16.1. Keyboards

Use:

* inline keyboards for habit completion
* reply keyboards only if necessary

## 16.2. Habit reminder keyboard

For unfinished habits:

```text
[ ✅ Зарядка ]
[ ✅ Вода ]
[ ✅ Умыться ]
```

Callback data:

```ts
habit_done:{habitId}:{date}
```

## 16.3. Weekly habit addition keyboard

```text
[ Добавить привычку ]
[ Пока оставить как есть ]
```

## 16.4. Settings keyboard

Minimal MVP:

* reminder time
* timezone (optional later)
* pause / resume reminders

---

## 17. Scheduler / Jobs

Need three core scheduled jobs.

## 17.1. Daily reminders job

Runs periodically, e.g. every 15 minutes.

For each user:

* determine current local time
* decide whether morning/day/evening reminder should be sent
* send gratitude prompt if not already sent in that window
* send habit reminder only if unfinished habits exist
* change prompt tone based on engagement state

### Reminder windows

Example:

* morning: 08:00–11:00
* day: 12:00–16:00
* evening: 18:00–21:00

## 17.2. Weekly summary job

Runs once daily and checks user local date/time.

If local time matches weekly summary schedule:

* compute summary
* render message
* send summary
* optionally prompt weekly feelings
* mark summary as sent for that week

Need a table or log:

```ts
type SentWeeklySummary = {
  id: string
  userId: string
  weekStartDate: string
  sentAt: Date
}
```

## 17.3. Inactivity check job

Runs daily.

Rules:

* if no activity for 2 days -> `low_activity`
* if no activity for 5+ days -> `inactive`
* else `active`

These states affect reminder text selection.

---

## 18. Engagement State Logic

Function:

```ts
getEngagementState(lastActivityAt: Date | null, now: Date, timezone: string)
```

Rules:

* `active` -> last activity within 1 day
* `low_activity` -> inactivity 2-4 days
* `inactive` -> inactivity 5+ days

Behavior impact:

* `active` -> standard prompts
* `low_activity` -> softer, lower-bar prompts
* `inactive` -> re-entry prompts focused on one tiny step

---

## 19. Event-Driven Business Logic

All key actions should be modeled as internal events.

## 19.1. Event list

```ts
type DomainEvent =
  | 'user_started'
  | 'onboarding_completed'
  | 'gratitude_submitted'
  | 'habit_created'
  | 'habit_completed'
  | 'daily_reminder_sent'
  | 'weekly_summary_sent'
  | 'weekly_feeling_submitted'
  | 'engagement_state_changed'
```

## 19.2. Event usage

Events can be handled directly in service layer or via lightweight event bus.

MVP can simply call downstream services inline.

Example:

* `habit_completed`:

  * save completion
  * update last activity
  * compute whether it was first / last completion of day
  * send correct response

---

## 20. Main User Flows

## 20.1. First-time user onboarding

1. user sends `/start`
2. bot sends welcome + explanation
3. bot explains:

   * gratitude
   * habits
   * weekly stats
4. bot offers to choose first habit
5. bot optionally explains gratitude input
6. set `onboardingCompleted = true`

### Pseudocode

```ts
async function handleStart(user) {
  await ensureUserExists(user)
  await sendMessage(user, getMessage('onboarding.welcome'))
  await sendMessage(user, getMessage('onboarding.product_explanation'))
  await sendMessage(user, getMessage('onboarding.habit_selection_intro'), defaultHabitKeyboard())
}
```

---

## 20.2. Daily gratitude flow

1. bot sends gratitude prompt
2. user sends gratitude list
3. parser counts items
4. save entry
5. select appropriate supportive response
6. update user last activity

### Pseudocode

```ts
async function handleGratitudeText(userId, text) {
  const items = parseGratitudeItems(text)
  if (items.length === 0) {
    return sendMessage(userId, getMessage('gratitude.responses.empty_followup'))
  }

  await gratitudeRepo.create({
    userId,
    date: todayInUserTz(userId),
    rawText: text,
    itemsCount: items.length,
    parsedItems: items
  })

  let key = 'gratitude.responses.count_1_2'
  if (items.length >= 3 && items.length <= 5) key = 'gratitude.responses.count_3_5'
  else if (items.length >= 6 && items.length <= 9) key = 'gratitude.responses.count_6_9'
  else if (items.length >= 10) key = 'gratitude.responses.count_10_plus'

  await userService.touchActivity(userId)
  await sendMessage(userId, getMessage(key))
}
```

---

## 20.3. Daily habits flow

1. bot checks unfinished habits
2. sends reminder with buttons
3. user taps button or sends text
4. bot marks habit complete
5. bot responds with first/generic/last-done message

### Pseudocode

```ts
async function completeHabitForToday(userId, habitId, source) {
  const today = todayInUserTz(userId)
  const alreadyDone = await habitCompletionRepo.exists(userId, habitId, today)

  if (alreadyDone) {
    return sendMessage(userId, 'Эта привычка уже отмечена на сегодня ✅')
  }

  await habitCompletionRepo.upsert({
    userId,
    habitId,
    date: today,
    completed: true,
    completedAt: new Date(),
    source
  })

  await userService.touchActivity(userId)

  const allHabits = await habitService.getActiveHabits(userId)
  const completedToday = await habitService.getCompletedHabitsToday(userId)
  const pendingToday = allHabits.filter(h => !completedToday.some(c => c.habitId === h.id))

  let messageKey = 'habits.responses.completed_generic'
  if (completedToday.length === 1) {
    messageKey = 'habits.responses.completed_first_today'
  }
  if (pendingToday.length === 0) {
    messageKey = 'habits.responses.completed_last_today'
  }

  await sendMessage(userId, getMessage(messageKey))
}
```

Note: after insert, recompute carefully so counts are accurate.

---

## 20.4. Weekly summary flow

1. scheduler detects correct local time
2. compute gratitude stats
3. compute habit stats
4. classify week
5. render summary blocks
6. send summary
7. optionally ask for weekly feelings
8. mark week summary as sent

### Pseudocode

```ts
async function sendWeeklySummary(userId) {
  const { weekStart, weekEnd } = getCurrentWeekRangeForSummary(userId)

  const gratitudeStats = await weeklySummaryService.getWeeklyGratitudeStats(userId, weekStart, weekEnd)
  const habitStats = await weeklySummaryService.getWeeklyHabitStats(userId, weekStart, weekEnd)
  const feeling = await feelingsService.getFeelingForWeek(userId, weekStart, weekEnd)

  const weekType = classifyOverallWeek(gratitudeStats, habitStats)

  const summaryText = await weeklySummaryRenderer.render({
    userId,
    weekType,
    gratitudeStats,
    habitStats,
    feeling
  })

  await sendMessage(userId, summaryText)
  await sendMessage(userId, getMessage('feelings_journal.prompt'))

  await userSessionRepo.setState(userId, 'waiting_for_weekly_feelings')
  await weeklySummaryLogRepo.markSent(userId, weekStart)
}
```

---

## 20.5. Re-engagement flow

Triggered by inactivity check or soft reminder scheduling.

### Pseudocode

```ts
async function getContextualGratitudePrompt(userId) {
  const state = await userService.getEngagementState(userId)

  if (state === 'inactive') {
    return getMessage('gratitude.prompts.inactive_return')
  }
  if (state === 'low_activity') {
    return getMessage('gratitude.prompts.low_activity')
  }
  return getMessage('gratitude.prompts.day')
}
```

Same for habits.

---

## 21. Weekly Summary Renderer

Renderer combines blocks into one Telegram-safe message.

## 21.1. Output structure

Message should have:

1. header
2. gratitude block if available
3. gratitude interpretation if available
4. habits block if available
5. habits interpretation if available
6. feelings block if available
7. closing

## 21.2. Renderer pseudocode

```ts
function renderWeeklySummary(input): string {
  const parts: string[] = []

  parts.push(getMessage(`weekly_summary.header.${input.weekType}`))

  if (input.gratitudeStats.totalItems > 0) {
    parts.push(renderGratitudeBlock(input.gratitudeStats))
    parts.push(renderGratitudeInterpretation(input.gratitudeStats.dynamicType))
  }

  if (input.habitStats.habits.length > 0) {
    parts.push(renderHabitsBlock(input.habitStats))
    parts.push(renderHabitsInterpretation(input.habitStats.strongType))
  }

  if (input.feeling?.rawText) {
    parts.push(renderFeelingsBlock(input.feeling.rawText))
  }

  parts.push(getMessage(`weekly_summary.closing.${input.weekType}`))

  return parts.filter(Boolean).join('\n\n')
}
```

## 21.3. Gratitude block example renderer

```ts
function renderGratitudeBlock(stats) {
  return [
    getStaticTitle('weekly_summary.gratitude_block.title'),
    renderTemplate(
      getMessage('weekly_summary.gratitude_block.templates'),
      {
        total_items: stats.totalItems,
        avg_per_day: stats.avgPerDay.toFixed(1),
        max_items_day: stats.maxItemsDay
      }
    )
  ].join('\n')
}
```

---

## 22. Persistence / Storage Notes

Recommended DB: PostgreSQL.

## 22.1. Required indexes

* `users.telegram_id`
* `habits.user_id`
* `habit_completions (user_id, date)`
* `habit_completions (habit_id, date)` unique
* `gratitude_entries (user_id, date)`
* `weekly_feelings (user_id, week_start_date)` unique

## 22.2. Timezone-safe dates

Always calculate local day boundaries using user timezone.

Never use server date directly for daily records.

---

## 23. Suggested Database Tables

## users

```sql
id UUID PK
telegram_id TEXT UNIQUE NOT NULL
username TEXT NULL
first_name TEXT NULL
timezone TEXT NOT NULL DEFAULT 'Europe/Berlin'
locale TEXT NOT NULL DEFAULT 'ru'
onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE
engagement_state TEXT NOT NULL DEFAULT 'active'
preferred_reminder_morning TEXT NULL
preferred_reminder_day TEXT NULL
preferred_reminder_evening TEXT NULL
weekly_summary_day INT NOT NULL DEFAULT 7
weekly_summary_time TEXT NULL
last_activity_at TIMESTAMP NULL
created_at TIMESTAMP NOT NULL
updated_at TIMESTAMP NOT NULL
```

## habits

```sql
id UUID PK
user_id UUID NOT NULL REFERENCES users(id)
title TEXT NOT NULL
normalized_title TEXT NOT NULL
source TEXT NOT NULL
active BOOLEAN NOT NULL DEFAULT TRUE
stage TEXT NOT NULL DEFAULT 'adaptation'
created_at TIMESTAMP NOT NULL
archived_at TIMESTAMP NULL
```

## habit_completions

```sql
id UUID PK
user_id UUID NOT NULL REFERENCES users(id)
habit_id UUID NOT NULL REFERENCES habits(id)
date TEXT NOT NULL
completed BOOLEAN NOT NULL DEFAULT TRUE
completed_at TIMESTAMP NULL
source TEXT NOT NULL
UNIQUE(habit_id, date)
```

## gratitude_entries

```sql
id UUID PK
user_id UUID NOT NULL REFERENCES users(id)
date TEXT NOT NULL
raw_text TEXT NOT NULL
items_count INT NOT NULL
parsed_items JSONB NULL
created_at TIMESTAMP NOT NULL
```

## weekly_feelings

```sql
id UUID PK
user_id UUID NOT NULL REFERENCES users(id)
week_start_date TEXT NOT NULL
week_end_date TEXT NOT NULL
raw_text TEXT NOT NULL
created_at TIMESTAMP NOT NULL
UNIQUE(user_id, week_start_date)
```

## user_session_states

```sql
id UUID PK
user_id UUID UNIQUE NOT NULL REFERENCES users(id)
state TEXT NOT NULL
payload JSONB NULL
updated_at TIMESTAMP NOT NULL
```

## weekly_summary_logs

```sql
id UUID PK
user_id UUID NOT NULL REFERENCES users(id)
week_start_date TEXT NOT NULL
sent_at TIMESTAMP NOT NULL
UNIQUE(user_id, week_start_date)
```

---

## 24. Command Handlers

## `/start`

* create user if needed
* send onboarding
* suggest first habit

## `/help`

Return concise explanation of available actions.

## `/gratitude`

Send gratitude prompt and set session state `waiting_for_gratitude`.

## `/habits`

Show current active habits and their completion for today.

## `/add_habit`

* show default habit options + custom add option

## `/stats`

* generate weekly summary on demand

## `/feelings`

* show recent monthly weekly-feelings archive

## `/settings`

MVP can respond:

* "Settings will include reminder time and timezone in next version"
  or basic implementation if available

---

## 25. Text Message Handler

Central text router pseudocode:

```ts
async function handleIncomingText(userId: string, text: string) {
  const session = await sessionRepo.get(userId)

  if (session?.state === 'waiting_for_custom_habit') {
    return habitService.handleCustomHabitCreation(userId, text)
  }

  if (session?.state === 'waiting_for_weekly_feelings') {
    return feelingsService.handleWeeklyFeelingInput(userId, text)
  }

  if (looksLikeGratitudeList(text)) {
    return gratitudeService.handleGratitudeText(userId, text)
  }

  const matchedHabit = await habitService.detectHabitCompletionFromText(userId, text)
  if (matchedHabit) {
    return habitService.completeHabitForToday(userId, matchedHabit.id, 'text')
  }

  return sendNeutralUnknownReply(userId)
}
```

### Unknown reply examples

Keep neutral and simple:

* "Я пока не совсем понял сообщение. Можно отправить список благодарностей, отметить привычку или открыть /help."
* "Если хочешь, можно написать благодарности, отметить привычку или посмотреть /stats."

---

## 26. Detection Helpers

## 26.1. `looksLikeGratitudeList(text)`

Heuristic:

Return true if:

* text has 2+ lines
* OR contains numbered list pattern
* OR session state is `waiting_for_gratitude`

## 26.2. `looksLikeCustomHabit(text)`

Only if session state is `waiting_for_custom_habit`

## 26.3. `detectHabitCompletionFromText`

Return matched habit if text contains:

* a habit title
* known synonym
* habit keyword with completion-like phrasing

---

## 27. Buttons / Callback Handlers

Need callback format:

```text
habit_done:{habitId}:{date}
add_habit_default:{habitName}
add_habit_custom
keep_current_habits
write_weekly_feelings
```

Handler examples:

```ts
async function onHabitDoneCallback(userId, habitId, date) {
  return habitService.completeHabitForToday(userId, habitId, 'button')
}
```

---

## 28. Safety / Psychology Constraints in Code

These are non-negotiable product constraints and should be treated as development requirements.

## 28.1. Never punish

No punitive logic:

* no negative scores
* no aggressive streak-loss messages
* no "missed goal" alerts

## 28.2. Never over-interpret mental state

Do not output:

* diagnosis
* claims about depression severity
* therapeutic claims
* "you are healing"
* "this will cure..."

Allowed:

* supportive reflection
* normalization
* invitation to a tiny action

## 28.3. Respect low energy states

If user inactivity increases:

* reduce expectation size
* shorten task phrasing
* focus on single step
* avoid stacking multiple reminders

---

## 29. Anti-Spam Rules

## 29.1. Daily limits

Recommended max:

* 3 reminders per day total
* ideally 1 gratitude + 1-2 habit reminders

## 29.2. Suppression rules

Do not send gratitude reminder if:

* user already sent gratitude today
* max reminder count reached

Do not send habit reminder if:

* no active habits
* all habits completed
* max reminder count reached

## 29.3. Duplicate prevention

Do not send same exact text twice in a row if alternative exists.

---

## 30. Metrics / Analytics for Future

Track but do not expose initially:

* daily active users
* gratitude participation rate
* average gratitude item count
* habit completion rate
* weekly summary open rate if trackable
* re-engagement success rate after inactivity

Useful event logs:

```ts
track('gratitude_submitted', { userId, itemsCount })
track('habit_completed', { userId, habitId })
track('weekly_summary_sent', { userId, weekType })
track('weekly_feeling_saved', { userId })
```

---

## 31. Recommended Development Order

Build in this exact order:

### Phase 1

* user model
* `/start`
* default habit selection
* custom habit creation

### Phase 2

* habit completion by button
* daily habit reminder job

### Phase 3

* gratitude parser
* gratitude save + response
* gratitude prompt reminders

### Phase 4

* weekly summary calculations
* weekly summary renderer
* `/stats`

### Phase 5

* weekly feelings note
* feelings archive

### Phase 6

* inactivity state handling
* re-engagement messaging
* deduplication / polish

---

## 32. Acceptance Criteria

## 32.1. Gratitude

* user can send numbered gratitude list
* bot counts items correctly
* bot replies supportively based on item count
* weekly gratitude stats compute correctly

## 32.2. Habits

* user can select a default habit
* user can add custom habit
* bot sends reminders only for unfinished habits
* user can complete via button
* user can complete via text for basic supported phrases
* weekly habit stats compute correctly

## 32.3. Weekly Summary

* weekly summary can be generated on demand
* summary includes gratitude block if data exists
* summary includes habits block if data exists
* summary includes feelings note if exists
* tone remains supportive across all cases
* empty week handled gently

## 32.4. Re-engagement

* engagement state updates based on inactivity
* prompts change for low_activity and inactive
* no guilt language appears

---

## 33. Example Interfaces

```ts
interface GratitudeService {
  handleGratitudeText(userId: string, text: string): Promise<void>
  parseItems(text: string): string[]
  getWeeklyStats(userId: string, weekStart: string, weekEnd: string): Promise<WeeklyGratitudeStats>
}

interface HabitService {
  createHabit(userId: string, title: string, source: 'default' | 'custom'): Promise<Habit>
  completeHabitForToday(userId: string, habitId: string, source: 'button' | 'text'): Promise<void>
  detectHabitCompletionFromText(userId: string, text: string): Promise<Habit | null>
  getWeeklyStats(userId: string, weekStart: string, weekEnd: string): Promise<WeeklyHabitStats>
}

interface WeeklySummaryService {
  generate(userId: string, weekStart: string, weekEnd: string): Promise<string>
}
```

---

## 34. Example Constants

```ts
export const ENGAGEMENT_THRESHOLDS = {
  LOW_ACTIVITY_DAYS: 2,
  INACTIVE_DAYS: 5
}

export const WEEKLY_SUMMARY = {
  DEFAULT_DAY: 7, // Sunday
  DEFAULT_TIME: '19:00'
}

export const GRATITUDE = {
  SOFT_TARGET: 10,
  STABILITY_THRESHOLD: 1.0
}

export const REMINDERS = {
  MAX_PER_DAY: 3,
  MORNING_WINDOW: ['08:00', '11:00'],
  DAY_WINDOW: ['12:00', '16:00'],
  EVENING_WINDOW: ['18:00', '21:00']
}
```

---

## 35. Future Extensions (not MVP)

Potential later additions:

* achievement system
* "consistency badges"
* lightweight happiness/progress meter
* customizable reminder styles
* advanced habit frequency (e.g. Mon/Wed/Fri)
* monthly summary
* "gentle mode" vs "more active mode"
* emotional tagging of weekly notes
* richer custom NLP

Do not implement before MVP is stable.

---

## 36. Final Development Notes for Codex

When generating implementation code:

1. Keep business logic separate from Telegram handlers
2. Keep all user-facing text in `messages.json`
3. Use user timezone for all daily/weekly logic
4. Keep reminders idempotent
5. Avoid duplicate completions
6. Prefer small pure functions for:

   * parsing gratitude lists
   * classifying engagement state
   * calculating weekly stats
   * rendering summary text
7. Preserve psychological safety as a product requirement, not a cosmetic detail

---

## 37. Minimal Launch Checklist

Before first deployment confirm:

* `/start` works
* habits can be added
* habits can be marked via button
* gratitude list parsing works
* `/stats` returns meaningful summary
* weekly summary job sends once only
* inactivity state changes correctly
* no shaming text anywhere
* reminders are not spammy
* empty-data weeks handled gently

---

## 38. One-Sentence Product Contract

This bot helps the user return to life through small, repeatable, emotionally safe actions — and every implementation choice should preserve that.

