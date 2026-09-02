# GitHub workflow for this project

Ниже — базовый набор команд для сохранения и обновления проекта в GitHub.

## 1. Проверить статус

```bash
git status
```

## 2. Добавить файлы в индекс

```bash
git add .
```

Или только выбранные файлы:

```bash
git add app README.md requirements.txt
```

## 3. Создать коммит

```bash
git commit -m "Initial project setup"
```

Или после изменений:

```bash
git commit -m "Add application API and schemas"
```

## 4. Подключить GitHub репозиторий

Если репозиторий ещё не создан:

```bash
git remote add origin https://github.com/<username>/<repo-name>.git
```

Проверить привязку:

```bash
git remote -v
```

## 5. Отправить изменения в GitHub

```bash
git push -u origin main
```

Если ветка называется `master`:

```bash
git push -u origin master
```

## 6. Дальнейшие обновления

После каждого изменения:

```bash
git status
git add .
git commit -m "Describe your changes"
git push
```

## 7. Создать новую ветку

```bash
git checkout -b feature/my-change
```

После работы:

```bash
git add .
git commit -m "Add my change"
git push -u origin feature/my-change
```

## 8. Обновить локальную ветку из GitHub

```bash
git pull origin main
```

## 9. Полезная команда для просмотра истории

```bash
git log --oneline
```

## 10. Для Windows PowerShell

Если нужно выполнить всё быстро:

```powershell
git status
git add .
git commit -m "Update project"
git push
```

## 11. Быстрый шаблон для текущей работы

```bash
git add .
git commit -m "Update app routes and schemas"
git push
```

> Если после `git push` появляется ошибка, обычно это связано с тем, что репозиторий ещё не привязан или ветка не совпадает с основной.
