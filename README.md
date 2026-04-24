flowchart TD
    A[Користувач Telegram] -->|написання повідомлення| B[Telegram Cloud Server]
    B -->|Webhook| C[Python Telegram Bot<br/>обробник повідомлень]
    
    C -->|отримано текст| D{Перевірка команди}
    D -->|/start або /help| E[Відповідь з інструкцією]
    D -->|звичайне питання| F[Відправка статусу<br/>'бот друкує...']
    
    F --> G[RAG-модуль<br/>пошук у knowledge_base.json]
    
    G --> H{Знайдено в JSON?}
    
    H -->|ТАК| I[Формування відповіді<br/>з JSON даних]
    
    H -->|НІ| J[Function Calling Module<br/>DuckDuckGo Search API]
    
    J --> K[Отримання результатів<br/>заголовки + snippets]
    
    K --> L[Gemini API<br/>gemini-1.5-flash]
    
    L --> M[Промпт: стиснути до 3-4 речень<br/>Temperature: 0.3]
    
    M --> N[Відповідь від Gemini]
    
    I --> O[Відправка відповіді<br/>користувачу]
    N --> O
    
    O --> A
    
    E --> A

    subgraph "ВАШ СЕРВЕР"
        C
        F
        G
        H
        I
        J
        K
        L
        M
        N
        O
    end

    subgraph "БАЗА ЗНАНЬ"
        G2[(knowledge_base.json<br/>ваша вікіпедія)]
    end

    subgraph "ЗОВНІШНІ API"
        J2[DuckDuckGo API]
        L2[Google Gemini API]
    end

    G -.-> G2
    J -.-> J2
    L -.-> L2