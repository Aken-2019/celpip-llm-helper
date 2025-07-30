
# CELPIP Exam Helper Powered by LLM

## About
This project is an application to help CELPIP (Canadian English Language Proficiency Index Program) students improve their speaking and writing skills by integrating LLM models. It's accessible at [https://tifen.harrylearns.com](https://tifen.harrylearns.com). 



## Features
- **User interface**: Users can either record their speaking (or upload their audio file) and get immediate feedback, including a revised version of the practice and grammar corrections.
- **LLM integration**: Prompts are engineered specifially for CELPIP test, inspired by [YouTuber - HZad Education](https://www.youtube.com/@hzadeducation-coachingcent986/playlists).
- **Pricing model**: Users can deposit credits to their account and only pay for the number of LLM tokens they use, powered by API provider - [API2D](https://api2d.com/).

## Tech Stack   
| Category      | Technologies |
|--------------|--------------|
| Backend      | Django |
| Frontend     | Svelte, Bootstrap |
| LLM          | OpenAI's Whisper for STT, Antropic's Claude for chats|
| Testing      | GitHub Actions, Pytest, Playwright |
| Deployment   | Docker, Coolify (Self-hosted PaaS) |
| Infrastructure | Debian Linux (VPS) |

## To-do
- [ ] Add dark/light mode switch
- [ ] Add multi-language support

## Screenshots
### Speaking
Users can record or upload their practices and get feedbacks.
![Speaking](docs/screenshots/celpip-speaking.png)

### Writing
Users can type directly at the website and get feedbacks.
![Writing](docs/screenshots/celpip-writing.png)
