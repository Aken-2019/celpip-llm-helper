This project is an application to help CELPIP (Canadian English Language Proficiency Index Program) students improve their speaking and writing skills. Screenshots can be found at the [docs/screenshots](docs/screenshots) folder.

## Features
- User can either record their speaking (or upload their audio file) and get immediate feedback from LLM, including revised version of the speaking and grammar corrections.
- Prompts are engineered specifially for CELPIP test, inspired by [YouTuber - HZad Education](https://www.youtube.com/@hzadeducation-coachingcent986/playlists).
- User can deposit credits to their account and only pay for the number of LLM tokens they use.

## Tech Stack
- Backend: Django
- Frontend: Svelte 
- LLM: OpenAI, Claude
- Testing: GitHub actions, Pytest, Playwright
- Deployment: Docker, Coolify (an open source alternative to Heroku)
```mermaid
graph LR
    client[Svelte] --> |requests|> api[Django]
    api --> |uses|> db[PostgreSQL]
    api --> |uses|> llm[OpenAI]
    api --> |uses|> llm[Claude]
    api --> |tested by|> tests[Pytest]
    api --> |tested by|> tests[Playwright]
    ci[GitHub Actions] --> |runs|> tests[Pytest]
    ci --> |runs|> tests[Playwright]
    ci --> |uses|> docker[Docker]
    ci --> |uses|> coolify[Coolify]
```