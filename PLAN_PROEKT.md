# Project Plan: Job Application Automation Platform

## Overall Direction

The project should grow in stages: first a basic working product, then integrations, then analytics, and only then AI/RAG.

## 1. Stage 0 — Project Setup and Skeleton

### Goal
Create a basic structure so the project can be run locally and developed further.

### Tasks
- choose the stack:
  - Python
  - FastAPI
  - PostgreSQL
  - SQLAlchemy
  - Telegram bot
  - Docker Compose
  - pytest
- create the basic project structure
- configure the environment
- configure environment variables
- verify that the backend and bot start
- create a health-check endpoint

### Result
- the project runs locally
- there is an empty but working skeleton
- new modules can be added without breaking the system

## 2. Stage 1 — MVP: Application Processing and Telegram Bot

### Goal
Create a minimum version where users can submit vacancy data and have it saved.

### Tasks
- Telegram commands:
  - start
  - new vacancy
  - status
  - help
- application form:
  - company
  - link
  - position
  - description
  - status
- API for creating and viewing applications
- data model for vacancy / application / status
- database storage
- basic checks and validation

### Result
- the bot accepts applications
- data is saved in the database
- there is a basic API

## 3. Stage 2 — Database and Business Logic

### Goal
Create a proper data model so the project can be scaled later.

### Tasks
- design tables:
  - vacancies
  - companies
  - applications
  - statuses
  - change history
  - follow-up log
- add relationships between entities
- implement CRUD operations
- add repositories and a service layer
- create migrations
- add event logging

### Result
- there is a proper data schema
- data is stored in a structured way
- analytics layers and AI are easier to add

## 4. Stage 3 — Synchronization with Google Sheets and External Sources

### Goal
Connect external tools so data flows not only to the bot but also to spreadsheets.

### Tasks
- integrate with the Google Sheets API
- export applications and statuses
- import data when needed
- update the status after actions
- normalize data formats
- protect against repeats and duplicates

### Result
- data is available in tabular form
- it is easy to share with other participants
- tracking and analytics are convenient

## 5. Stage 4 — Preparing Data for Analytics

### Goal
Make the data convenient for reports and further analysis.

### Tasks
- bring the data into a single format
- identify fields:
  - acquisition channel
  - application status
  - company
  - date
  - response type
  - follow-up
- add a model for metrics
- create basic reports
- prepare a layer for dbt

### Result
- the data is ready for dashboards and BI
- conversion rates and effectiveness can be calculated

## 6. Stage 5 — BI, Dashboards, and Metrics

### Goal
Show that the project does more than store data: it helps with decision-making.

### Tasks
- integrate with Metabase
- reports:
  - number of applications
  - status by company
  - successful / unsuccessful vacancies
  - channel performance
  - follow-up statistics
- visualize KPIs
- track processes

### Result
- clear analytics
- weaknesses in the job search process are visible

## 7. Stage 6 — RAG and AI Assistant

### Goal
Add a “smart layer” after the data and structure are in place.

### Tasks
- connect LangChain
- configure ChromaDB
- store:
  - vacancy descriptions
  - messages/replies
  - historical applications
  - follow-up templates
  - text documents
- implement RAG:
  - search for similar vacancies
  - generate recommendations
  - create message drafts
  - analyze application text
  - help with reply templates
- keep AI services separate from the core logic

### Result
- the project gains intelligent features
- the bot can help not only store data but also make decisions

## 8. Stage 7 — Quality, CI/CD, and Production Readiness

### Goal
Make the project stable and easy to develop.

### Tasks
- tests
- linting
- static analysis
- GitHub Actions
- Docker Compose
- env configuration
- logging
- monitoring
- secure secret storage

### Result
- the project can be developed by a team
- fewer errors
- easier startup in different environments

## Recommended Development Sequence

### Month 1
- project skeleton
- Telegram bot
- API
- database
- basic models
- application storage

### Month 2
- Google Sheets
- statuses
- follow-up logic
- analytics
- basic reports

### Month 3
- RAG
- ChromaDB
- LangChain
- AI suggestions
- UX improvements
- CI/CD

## Key Idea

Do not try to build everything at once:
- first a working basic product,
- then integrations,
- then analytics,
- then AI.

This gives you a project that:
- runs,
- is stable,
- is easy to extend,
- is ready for RAG and analytics.

## Priority Recommendation

The recommended order is:
1. Telegram + API + database
2. Google Sheets
3. Metrics / dashboard
4. AI / LangChain / ChromaDB
5. CI/CD and stabilization
