# Avatar Engine

Локальный Avatar Engine для одного оператора.

Проект создаётся в:

```text
F:\Dev\Projects\Avatar Engine
```

Git-репозиторий:

```text
git@github.com:solomonczyk/Avatar-Engine.git
```

Источник для выборочного переиспользования:

```text
https://github.com/solomonczyk/comfy-agent-mvp
```

## Цель

Получать короткое видео с говорящим аватаром из локального задания:

```text
портрет/референсы + текст или аудио
→ подготовка персонажа
→ голос
→ анимация лица
→ lip-sync
→ постобработка
→ ручной визуальный просмотр
→ финальный MP4
```

Решение предназначено для одного человека и одного локального компьютера. Это не SaaS, не коммерческая платформа и не многопользовательская система.

## Основные ограничения

- Windows 10.
- NVIDIA GTX 1060 5 GB VRAM.
- Один тяжёлый GPU-процесс одновременно.
- Никакой параллельной GPU-генерации.
- Нет автоматического слепого retry.
- Одна активная локальная очередь.
- SQLite вместо PostgreSQL/Redis.
- CLI как основной интерфейс MVP.
- FastAPI или простой локальный UI добавляются только после работающего E2E.
- Веса моделей и generated artifacts не коммитятся в Git.

## MVP

Первый MVP должен:

1. принять локальное задание;
2. положить его в persistent SQLite queue;
3. последовательно выполнить необходимые стадии;
4. не запускать более одной GPU-операции одновременно;
5. сохранить артефакты и лог;
6. создать короткий MP4;
7. остановиться на ручном визуальном просмотре;
8. после решения оператора пометить результат `accepted` или `rejected`.

## Документация

- [Scope](docs/01_PROJECT_SCOPE.md)
- [Architecture](docs/02_ARCHITECTURE.md)
- [Reuse plan](docs/03_COMFY_AGENT_REUSE_PLAN.md)
- [Project structure](docs/04_PROJECT_STRUCTURE.md)
- [Development plan](docs/05_DEVELOPMENT_PLAN.md)
- [Local setup](docs/06_LOCAL_SETUP.md)
- [GPU queue](docs/07_GPU_QUEUE_AND_RESOURCE_POLICY.md)
- [Data and artifacts](docs/08_DATA_AND_ARTIFACTS.md)
- [Testing](docs/09_TEST_STRATEGY.md)
- [Git workflow](docs/10_GIT_WORKFLOW.md)
- [Acceptance](docs/11_ACCEPTANCE_CRITERIA.md)
- [Risks and limits](docs/12_RISKS_AND_LIMITS.md)
- [Agent implementation brief](docs/13_AGENT_IMPLEMENTATION_BRIEF.md)
