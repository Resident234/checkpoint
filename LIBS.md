# Список используемых библиотек в проекте CheckPoint

## Основные зависимости

### 1. **geopy** (^2.4.1)
**Описание:** Python Geocoding Toolbox - библиотека для геокодирования и работы с географическими координатами.
**Использование:** Обработка географических данных, определение координат по адресам.

### 2. **httpx** (^0.27.2) с поддержкой HTTP/2
**Описание:** The next generation HTTP client - современный HTTP клиент для Python.
**Использование:** HTTP запросы, работа с API, веб-скрапинг.

### 3. **imagehash** (^4.3.1)
**Описание:** Image Hashing library - библиотека для создания хешей изображений.
**Использование:** Сравнение изображений, поиск дубликатов, анализ визуального контента.

### 4. **pillow** (^10.4.0)
**Описание:** Python Imaging Library (Fork) - библиотека для работы с изображениями.
**Использование:** Обработка, изменение размера, конвертация изображений.

### 5. **python-dateutil** (^2.9.0.post0)
**Описание:** Extensions to the standard Python datetime module - расширения для работы с датами.
**Использование:** Парсинг дат, работа с временными зонами, вычисления с датами.

### 6. **rich** (^13.9.1)
**Описание:** Render rich text, tables, progress bars, syntax highlighting, markdown and more to the terminal - библиотека для красивого вывода в терминал.
**Использование:** Создание красивых интерфейсов в командной строке, прогресс-бары, таблицы.

### 7. **beautifultable** (^1.1.0)
**Описание:** Print text tables for terminals - библиотека для создания таблиц в терминале.
**Использование:** Форматированный вывод данных в виде таблиц.

### 8. **beautifulsoup4** (^4.12.3)
**Описание:** Screen-scraping library - библиотека для парсинга HTML и XML.
**Использование:** Веб-скрапинг, извлечение данных из веб-страниц.

### 9. **alive-progress** (^3.1.5)
**Описание:** A new kind of Progress Bar, with real-time throughput, ETA, and very cool animations! - анимированные прогресс-бары.
**Использование:** Визуализация прогресса выполнения задач.

### 10. **protobuf** (^5.28.2)
**Описание:** Protocol Buffers - система сериализации данных от Google.
**Использование:** Сериализация и десериализация структурированных данных.

### 11. **autoslot** (^2022.12.1)
**Описание:** Classes and metaclasses for easier __slots__ handling - упрощение работы с __slots__.
**Использование:** Оптимизация памяти в классах Python.

### 12. **humanize** (^4.10.0)
**Описание:** Python humanize utilities - утилиты для "очеловечивания" данных.
**Использование:** Форматирование чисел, дат, размеров файлов в удобочитаемый вид.

### 13. **inflection** (^0.5.1)
**Описание:** A port of Ruby on Rails inflector to Python - библиотека для склонения слов.
**Использование:** Работа с формами слов, склонение существительных.

### 14. **jsonpickle** (^3.3.0)
**Описание:** Python library for serializing arbitrary object graphs into JSON - сериализация объектов в JSON.
**Использование:** Сохранение сложных объектов Python в JSON формате.

### 15. **packaging** (^24.1)
**Описание:** Core utilities for Python packages - утилиты для работы с пакетами Python.
**Использование:** Управление версиями, метаданными пакетов.

### 16. **rich-argparse** (^1.5.2)
**Описание:** Rich help formatters for argparse and optparse - красивое форматирование справки для argparse.
**Использование:** Улучшение интерфейса командной строки.

### 17. **selenium** (^4.35.0)
**Описание:** Official Python bindings for Selenium WebDriver - автоматизация веб-браузера.
**Использование:** Автоматизация браузера, тестирование веб-приложений, веб-скрапинг.

### 18. **pydub** (^0.25.1)
**Описание:** Manipulate audio with an simple and easy high level interface - работа с аудио файлами.
**Использование:** Обработка аудио, конвертация форматов, редактирование звука.

### 19. **speechrecognition** (^3.14.3)
**Описание:** Library for performing speech recognition, with support for several engines and APIs, online and offline - распознавание речи.
**Использование:** Преобразование речи в текст, работа с аудио командами.

## Системные зависимости

### 20. **numpy** (2.1.1)
**Описание:** Fundamental package for array computing in Python - основа для научных вычислений.
**Использование:** Математические операции, работа с массивами.

### 21. **scipy** (1.14.1)
**Описание:** Fundamental algorithms for scientific computing in Python - научные вычисления.
**Использование:** Статистика, оптимизация, обработка сигналов.

### 22. **certifi** (2025.8.3)
**Описание:** Python package for providing Mozilla's CA Bundle - сертификаты для SSL.
**Использование:** Безопасные HTTPS соединения.

### 23. **urllib3** (2.5.0)
**Описание:** HTTP library with thread-safe connection pooling - HTTP библиотека с пулом соединений.
**Использование:** HTTP запросы, управление соединениями.

### 24. **trio** (0.30.0)
**Описание:** A friendly Python library for async concurrency and I/O - асинхронное программирование.
**Использование:** Асинхронные операции, конкурентность.

### 25. **websocket-client** (1.8.0)
**Описание:** WebSocket client for Python with low level API options - клиент для WebSocket.
**Использование:** Реальное время коммуникации, WebSocket соединения.

## Вспомогательные библиотеки

### 26. **attrs** (25.3.0)
**Описание:** Classes Without Boilerplate - упрощение создания классов.
**Использование:** Создание классов с автоматическими методами.

### 27. **cffi** (1.17.1)
**Описание:** Foreign Function Interface for Python calling C code - интерфейс для вызова C кода.
**Использование:** Интеграция с C библиотеками.

### 28. **idna** (3.10)
**Описание:** Internationalized Domain Names in Applications - интернационализированные доменные имена.
**Использование:** Обработка Unicode в URL.

### 29. **sniffio** (1.3.1)
**Описание:** Sniff out which async library your code is running under - определение асинхронной библиотеки.
**Использование:** Совместимость между асинхронными библиотеками.

### 30. **sortedcontainers** (2.4.0)
**Описание:** Sorted Containers -- Sorted List, Sorted Dict, Sorted Set - отсортированные контейнеры.
**Использование:** Эффективные отсортированные структуры данных.

### 31. **typing-extensions** (4.14.1)
**Описание:** Backported and Experimental Type Hints for Python 3.9+ - расширения типизации.
**Использование:** Улучшенная типизация в Python.

### 32. **wcwidth** (0.2.13)
**Описание:** Measures the displayed width of unicode strings in a terminal - измерение ширины Unicode строк.
**Использование:** Правильное отображение Unicode в терминале.

### 33. **wsproto** (1.2.0)
**Описание:** WebSockets state-machine based protocol implementation - реализация протокола WebSocket.
**Использование:** Низкоуровневая работа с WebSocket.

### 34. **trio-websocket** (0.12.2)
**Описание:** WebSocket library for Trio - WebSocket для Trio.
**Использование:** Асинхронные WebSocket соединения.

### 35. **outcome** (1.3.0.post0)
**Описание:** Capture the outcome of Python function calls - захват результатов вызовов функций.
**Использование:** Обработка результатов асинхронных операций.

### 36. **h11** (0.14.0)
**Описание:** A pure-Python, bring-your-own-I/O implementation of HTTP/1.1 - реализация HTTP/1.1.
**Использование:** HTTP протокол.

### 37. **h2** (4.1.0)
**Описание:** HTTP/2 State-Machine based protocol implementation - реализация HTTP/2.
**Использование:** HTTP/2 протокол.

### 38. **hpack** (4.0.0)
**Описание:** Pure-Python HPACK header compression - сжатие HTTP заголовков.
**Использование:** Оптимизация HTTP/2.

### 39. **hyperframe** (6.0.1)
**Описание:** HTTP/2 framing layer for Python - фрейминг HTTP/2.
**Использование:** Низкоуровневая работа с HTTP/2.

### 40. **httpcore** (1.0.6)
**Описание:** A minimal low-level HTTP client - минимальный HTTP клиент.
**Использование:** Базовые HTTP операции.

### 41. **anyio** (4.6.0)
**Описание:** High level compatibility layer for multiple asynchronous event loop implementations - совместимость асинхронных библиотек.
**Использование:** Универсальная асинхронность.

### 42. **six** (1.16.0)
**Описание:** Python 2 and 3 compatibility utilities - совместимость Python 2 и 3.
**Использование:** Кросс-версионная совместимость.

### 43. **pycparser** (2.22)
**Описание:** C parser in Python - парсер C кода.
**Использование:** Анализ C кода.

### 44. **pysocks** (1.7.1)
**Описание:** A Python SOCKS client module - SOCKS прокси клиент.
**Использование:** Работа через SOCKS прокси.

### 45. **soupsieve** (2.6)
**Описание:** A modern CSS selector implementation for Beautiful Soup - CSS селекторы для Beautiful Soup.
**Использование:** Парсинг HTML с CSS селекторами.

### 46. **geographiclib** (2.0)
**Описание:** The geodesic routines from GeographicLib - геодезические вычисления.
**Использование:** Точные географические расчеты.

### 47. **grapheme** (0.6.0)
**Описание:** Unicode grapheme helpers - работа с Unicode графемами.
**Использование:** Правильная обработка Unicode текста.

### 48. **about-time** (4.2.1)
**Описание:** Easily measure timing and throughput of code blocks - измерение времени выполнения.
**Использование:** Профилирование и бенчмаркинг.

### 49. **audioop-lts** (0.2.2)
**Описание:** LTS Port of Python audioop - порт модуля audioop.
**Использование:** Обработка аудио данных.

### 50. **standard-aifc** (3.13.0)
**Описание:** Standard library aifc redistribution - перераспределение стандартной библиотеки aifc.
**Использование:** Работа с AIFF аудио файлами.

### 51. **standard-chunk** (3.13.0)
**Описание:** Standard library chunk redistribution - перераспределение стандартной библиотеки chunk.
**Использование:** Работа с chunk данными.

### 52. **pywavelets** (1.7.0)
**Описание:** PyWavelets, wavelet transform module - вейвлет преобразования.
**Использование:** Обработка сигналов, анализ изображений.

### 53. **markdown-it-py** (3.0.0)
**Описание:** Python port of markdown-it. Markdown parsing, done right! - парсер Markdown.
**Использование:** Обработка Markdown текста.

### 54. **mdurl** (0.1.2)
**Описание:** Markdown URL utilities - утилиты для URL в Markdown.
**Использование:** Обработка ссылок в Markdown.

### 55. **pygments** (2.18.0)
**Описание:** Pygments is a syntax highlighting package written in Python - подсветка синтаксиса.
**Использование:** Цветной вывод кода в терминале.

---

## Общая информация

**Всего библиотек:** 55  
**Основной фреймворк:** Poetry  
**Версия Python:** ^3.11  
**Лицензия:** AGPL-3.0  

Проект CheckPoint представляет собой "offensive Google framework" для работы с Facebook Graph API, включающий в себя широкий набор библиотек для:
- Веб-скрапинга и автоматизации браузера
- Обработки изображений и аудио
- Работы с географическими данными
- Создания красивых CLI интерфейсов
- Асинхронного программирования
- Научных вычислений
