# Parametric Scatter — Blender Add-on

**Вариант 46:** 3D-редактор для параметрического размещения объектов.

![Blender](https://img.shields.io/badge/Blender-5.1.2-orange)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-GPL%203.0-green)
![Tests](https://img.shields.io/badge/Tests-20%20passed-brightgreen)
![CI](https://github.com/variant46/parametric-scatter/actions/workflows/ci.yml/badge.svg)

Модуль-расширение для Blender, реализующий параметрическое размещение геометрических объектов в заданном пространстве (аналог Corona Scatter). Управление плотностью, масштабом и поворотом на основе карт текстур.

---

## Возможности

- Параметрическое рассеивание объекта-источника по поверхности целевого mesh
- **3 карты текстур**: Density (плотность), Scale (масштаб), Rotation (поворот)
- Collision detection — Avoid Overlap с KD-tree
- Мульти-источники — несколько объектов с весами
- Ветровая анимация (Wave) — процедурная анимация экземпляров
- LOD (Level of Detail) — генерация упрощённых копий
- Physics placement — симуляция Rigid Body для натурального расположения
- Geometry Nodes — поддерживается неразрушающий режим
- Выравнивание экземпляров по нормалям поверхности
- Группировка в коллекции для производительности
- Seed для воспроизводимости результата
- Сохранение/загрузка пресетов (JSON)
- Полная поддержка Undo/Redo
- Интеграция в боковую панель 3D Viewport

## Быстрый старт

```bash
# Установка зависимостей для разработки
pip install -r requirements-dev.txt

# Запуск тестов
python -m pytest tests/ -v --cov=blender_scatter_addon

# Проверка безопасности
bandit -r blender_scatter_addon/

# Линтинг
flake8 blender_scatter_addon/
```

## Установка аддона

1. Скопируйте папку `blender_scatter_addon` в:
   - **Blender 4.2+**: `%APPDATA%/Blender Foundation/Blender/5.1/extensions/user_default/`
   - **Blender 4.0-**: `%APPDATA%/Blender Foundation/Blender/5.1/scripts/addons/`
2. В Blender: `Edit → Preferences → Add-ons`
3. Найдите "Parametric Scatter" и активируйте

## Использование

```
View3D → Sidebar (N) → Scatter
```

1. **Source** — объект для рассеивания (или несколько с весами)
2. **Surface** — поверхность-цель
3. **Texture Maps** (опционально):
   - Density — карта плотности
   - Scale — карта масштаба
   - Rotation — карта поворота
4. **Parameters**: Count, Scale Min/Max, Seed
5. **Режимы**: Face / Edge
6. **Опции**: Align to Normal, Use Collection, Avoid Overlap, Wind, LOD, Physics
7. **Scatter** — запуск / **Clear** — очистка

## Архитектура

```mermaid
graph TD
    UI[SCATTER_PT_main] -->|Scatter/Clear| Op[Operators]
    Op --> Core[scatter_core.py]
    Core --> Tex[texture_utils.py]
    Core --> BM[bmesh]
    Tex --> NP[NumPy]
    Core --> Obj[Blender Objects]
    Op --> Props[properties.py]
    UI --> Props
    Core --> GN[Geometry Nodes]
    Core --> KD[KD-tree / Collision]
    Core --> Wind[Wind Animation]
    Core --> LOD[Level of Detail]
    Core --> Phys[Rigid Body Physics]
```

## CI/CD Pipeline

Проект использует GitHub Actions для автоматической проверки качества кода.

| Этап | Инструмент | Описание |
|------|-----------|----------|
| Lint | flake8 | Статический анализ, проверка стиля (PEP8, max-line-length=100) |
| Security | bandit | SAST-анализ, поиск уязвимостей Python-кода |
| Test | pytest + pytest-cov | 20 модульных тестов с замером покрытия |
| Blender Integration | Blender --background | Интеграционный тест (опционально, в Docker) |

Pipeline запускается на каждый push и pull request в `main`/`develop`.

### Docker

```bash
# Сборка образа
docker-compose build

# Запуск тестов
docker-compose run pytest

# Проверка безопасности
docker-compose run security

# Линтинг
docker-compose run lint

# Интеграционный тест Blender
docker-compose run blender-test
```

## Тестирование

| Уровень | Инструмент | Описание |
|---------|-----------|----------|
| Модульное | pytest | 20 тестов для texture_utils и scatter_core |
| Интеграционное | Blender --background | Scatter/Clear в Blender |
| Безопасность | bandit | SAST-анализ Python-кода |
| Зависимости | safety | Проверка уязвимостей пакетов |
| Lint | flake8 | Статический анализ кода (PEP8) |

## API

### `scatter_core.scatter_objects(settings) -> bool`

Запускает рассеивание. Принимает `ScatterSettings` PropertyGroup.

### `scatter_core.clear_scatter(source_name: str)`

Удаляет все рассеянные экземпляры по имени коллекции.

### `texture_utils.load_texture_as_grayscale(image) -> np.ndarray | None`

Конвертирует Blender Image в grayscale numpy-массив.

### `texture_utils.sample_texture(tex, u, v) -> float`

Сэмплинг текстуры по UV-координатам (wrap-режим).

## Git flow

| Ветка | Назначение |
|-------|-----------|
| `main` | Стабильная версия |
| `develop` | Разработка |
| `feature/*` | Новые функции |
| `fix/*` | Исправления |
| `release/*` | Подготовка релиза |

## Безопасность

- SAST-анализ: `bandit -r blender_scatter_addon/`
- Проверка зависимостей: `safety check -r requirements.txt`
- Минимальные привилегии: аддон не требует доступа к файловой системе вне Blender
- Pipeline CI: flake8 + bandit + pytest на каждый PR

## ИИ-ассистенты

Разработка выполнена с использованием AI-ассистента (opencode), который помогал в:
- Генерации кода ядра рассеивания
- Написании тестов
- Создании документации
- Документировании архитектуры

## Лицензия

GPL-3.0
