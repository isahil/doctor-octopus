# Doctor Octopus - System Architecture

## High-Level System Design

```mermaid
graph TB
    subgraph "User Interface"
        User[👤 User/Tester]
    end

    subgraph "Client Layer - Port 3000"
        Client[React Frontend<br/>Vite + React 19]
        Cards[📊 Cards View<br/>Test Report Viewer]
        Lab[🧪 Lab View<br/>Test Execution UI]
        Terminal[💻 Terminal View<br/>XTerm.js]
        SocketIOClient[SocketIO Client]
    end

    subgraph "Server Layer"
        subgraph "Main Server - Port 8000"
            FastAPI[FastAPI REST API]
            CardsAPI[Cards Component<br/>Report Management]
            LocalAPI[Local Component<br/>Local Report Handling]
            RemoteAPI[Remote Component<br/>S3 Operations]
            ValidationAPI[Validation Component]
            NotificationAPI[Notification Component]
        end

        subgraph "FixMe Server - Port 8001"
            FixMeWS[FastAPI WebSocket Server]
            SocketIOServer[SocketIO Server<br/>Log Streaming]
        end
    end

    subgraph "Data Layer"
        Redis[(Redis Cache<br/>Port 6379)]
        RedisKeys["• Test Report Cards<br/>• Client Stats<br/>• Download Queues<br/>• Pub/Sub Events"]
    end

    subgraph "Storage Layer"
        S3[AWS S3 Bucket<br/>Remote Test Reports]
        LocalFS[Local File System<br/>test_reports/]
    end

    subgraph "Test Execution"
        Playwright[Playwright Test Runner<br/>e2e/client/tests/]
        Pytest[Pytest Test Runner<br/>e2e/server/tests/]
        Artillery[Artillery Performance Tests<br/>e2e/perf/]
    end

    %% User interactions
    User -->|Browse Reports| Cards
    User -->|Run Tests| Lab
    User -->|View Logs| Terminal

    %% Client to Server - REST API
    Cards -->|GET /cards| CardsAPI
    Cards -->|GET /view-report| LocalAPI
    Lab -->|POST /execute-test| FastAPI
    Client -->|HTTP Requests| FastAPI

    %% Client to FixMe - WebSocket
    Terminal -.->|WebSocket Connection| SocketIOClient
    SocketIOClient -.->|Real-time Logs| SocketIOServer
    SocketIOServer -.->|Stream Logs| FixMeWS

    %% Server to Redis
    FastAPI -->|Cache Read/Write| Redis
    CardsAPI -->|Cache Report Cards<br/>TTL: 60 days| Redis
    NotificationAPI -->|Pub/Sub<br/>Update Frequency: 10s| Redis
    FastAPI -->|Track Client Stats| Redis
    RemoteAPI -->|Queue Management| Redis
    Redis -.->|Cached Data| RedisKeys

    %% Server to S3
    RemoteAPI -->|Upload Reports| S3
    RemoteAPI -->|Download Reports<br/>Rate Limited| S3
    RemoteAPI -->|List Buckets/Objects| S3

    %% Server to Local Storage
    LocalAPI -->|Read Reports| LocalFS
    LocalAPI -->|Start Report Server| LocalFS
    RemoteAPI -->|Download & Save<br/>Max 1000 dirs| LocalFS

    %% Test Execution Flow
    Lab -->|Trigger Execution| FastAPI
    FastAPI -->|Execute Tests| Playwright
    FastAPI -->|Execute Tests| Pytest
    Lab -->|Run Performance| Artillery

    Playwright -->|Generate Reports| LocalFS
    Pytest -->|Generate Reports| LocalFS
    Artillery -->|Generate Metrics| LocalFS

    FastAPI -->|Stream Logs| FixMeWS
    LocalFS -->|Upload After Completion| RemoteAPI

    %% Styling
    classDef clientStyle fill:#61dafb,stroke:#333,stroke-width:2px,color:#000
    classDef serverStyle fill:#009688,stroke:#333,stroke-width:2px,color:#fff
    classDef dataStyle fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef storageStyle fill:#ffd93d,stroke:#333,stroke-width:2px,color:#000
    classDef testStyle fill:#a29bfe,stroke:#333,stroke-width:2px,color:#000

    class Client,Cards,Lab,Terminal,SocketIOClient clientStyle
    class FastAPI,CardsAPI,LocalAPI,RemoteAPI,ValidationAPI,NotificationAPI,FixMeWS,SocketIOServer serverStyle
    class Redis,RedisKeys dataStyle
    class S3,LocalFS storageStyle
    class Playwright,Pytest,Artillery testStyle
```

## Data Flow Diagrams

### 1. Test Execution Flow

```mermaid
sequenceDiagram
    participant U as User
    participant L as Lab UI
    participant API as Main Server
    participant WS as FixMe Server
    participant T as Terminal
    participant TE as Test Executor
    participant FS as Local Storage
    participant S3 as AWS S3
    participant R as Redis

    U->>L: Click "Run Test"
    L->>API: POST /execute-test
    API->>TE: Start Test Execution
    API->>WS: Initialize Log Stream

    activate TE
    TE-->>WS: Stream Logs
    WS-->>T: Real-time Logs via SocketIO
    T-->>U: Display Live Logs

    TE->>FS: Generate Test Report
    TE->>API: Execution Complete
    deactivate TE

    API->>S3: Upload Report
    S3-->>API: Upload Success
    API->>R: Cache Report Metadata
    API->>L: Execution Complete
    L->>U: Show Success Message
```

### 2. Report Viewing Flow

```mermaid
sequenceDiagram
    participant U as User
    participant C as Cards UI
    participant API as Main Server
    participant R as Redis
    participant S3 as AWS S3
    participant FS as Local Storage
    participant PS as Playwright Server

    U->>C: Open Cards Page
    C->>API: GET /cards

    API->>R: Check Cache
    alt Cache Hit
        R-->>API: Return Cached Cards
    else Cache Miss
        API->>S3: Fetch Report List
        S3-->>API: Return Reports
        API->>R: Cache Results (60 days TTL)
    end

    API-->>C: Display Report Cards
    C-->>U: Show Reports

    U->>C: Click "View Report"
    C->>API: GET /view-report

    API->>FS: Check Local Storage
    alt Report Exists Locally
        FS-->>API: Report Found
    else Download from S3
        API->>S3: Download Report
        S3-->>API: Report Data
        API->>FS: Save to Local (Max 1000 dirs)
    end

    API->>PS: Start Playwright Report Server
    PS-->>API: Server URL
    API-->>C: Return Report URL
    C-->>U: Open Report in Browser
```

### 3. Redis Caching Strategy

```mermaid
graph LR
    subgraph "Redis Key Structure"
        Root[doctor-octopus:*]

        Reports[trading-apps-reports]
        ReportsCached[trading-apps-reports:cached]

        Stats[stats:*]
        CurrentClients[stats:current_clients_count]
        LifetimeClients[stats:lifetime_clients_count]
        MaxConcurrent[stats:max_concurrent_clients_count]

        Downloads[downloads:in-progress:*]

        Root --> Reports
        Root --> ReportsCached
        Root --> Stats
        Root --> Downloads

        Stats --> CurrentClients
        Stats --> LifetimeClients
        Stats --> MaxConcurrent
    end

    style Root fill:#ff6b6b,color:#fff
    style Reports fill:#ffd93d,color:#000
    style ReportsCached fill:#ffd93d,color:#000
    style Stats fill:#a29bfe,color:#fff
    style Downloads fill:#6c5ce7,color:#fff
```

## Component Interactions

### Service Communication Matrix

| Source         | Target       | Protocol       | Port | Purpose                                         |
| -------------- | ------------ | -------------- | ---- | ----------------------------------------------- |
| Client         | Main Server  | HTTP/REST      | 8000 | API requests, test execution, report management |
| Client         | FixMe Server | WebSocket      | 8001 | Real-time log streaming                         |
| Main Server    | Redis        | Redis Protocol | 6379 | Caching, stats, queues, pub/sub                 |
| Main Server    | AWS S3       | HTTPS          | 443  | Upload/download test reports                    |
| Main Server    | Local FS     | File I/O       | -    | Read/write test reports                         |
| FixMe Server   | Client       | SocketIO       | 8001 | Bidirectional log streaming                     |
| Test Executors | Local FS     | File I/O       | -    | Generate test reports                           |

### Redis Cache Configuration

- **Test Report Cards**: 60-day TTL
- **Download Queue**: 10-minute TTL
- **Cache Reload Queue**: 5-minute TTL
- **Stats Tracking**: No expiration (persistent counters)
- **Pub/Sub Frequency**: 1s for pubsub, 10s for S3 notifications

### S3 Rate Limiting Strategy

- **Folder Batch Size**: 5 folders per batch
- **File Batch Size**: 20 files per batch
- **Wait Time Between Batches**: 0.25 seconds
- **Max Local Directories**: 1000 (cleanup triggered when exceeded)

## Deployment Architecture

### Docker Compose Setup

```mermaid
graph TB
    subgraph "Docker Network: doctor-network"
        subgraph "Container: doctor-octopus-client"
            C[Client Service<br/>Port: 3000]
        end

        subgraph "Container: doctor-octopus-server"
            S[Main Server<br/>Port: 8000]
            SV[Volume: logs/]
            SV2[Volume: test_reports/]
        end

        subgraph "Container: doctor-octopus-fixme"
            F[FixMe Server<br/>Port: 8001]
            FV[Volume: logs/]
        end

        subgraph "Container: doctor-octopus-redis"
            R[(Redis<br/>Port: 6379)]
            RV[Volume: redis-data]
        end
    end

    External[External Access<br/>Browser]
    S3Cloud[AWS S3 Cloud]

    External -->|http://localhost:3000| C
    C -->|API Calls| S
    C -->|WebSocket| F
    S -->|Cache| R
    S -->|Upload/Download| S3Cloud
    F -->|Logs Storage| FV
    S -->|Logs & Reports| SV
    S -->|Reports Storage| SV2
    R -->|Persistence| RV

    style C fill:#61dafb,color:#000
    style S fill:#009688,color:#fff
    style F fill:#00acc1,color:#fff
    style R fill:#ff6b6b,color:#fff
    style S3Cloud fill:#ffd93d,color:#000
```

## Technology Stack

```mermaid
mindmap
    root((Doctor<br/>Octopus))
        Frontend
            React 19
            Vite
            React Router v7
            XTerm.js
            SocketIO Client
        Backend
            FastAPI
            Python 3.10+
            SocketIO Server
            Uvicorn
            Poetry
        Data & Cache
            Redis
            AWS S3
            boto3
        Testing
            Playwright
            Pytest
            Artillery
        DevOps
            Docker
            Docker Compose
            Nginx
        Linting & Format
            ESLint
            Prettier
            Ruff
```

## Performance Characteristics

- **Concurrent Workers**: 20 in production, 1 in development
- **Test Execution**: Playwright workers: 3, retries: 1
- **WebSocket**: Dedicated FixMe server prevents blocking main API
- **Cache TTL**: 60 days for report cards (configurable)
- **Rate Limiting**: S3 operations throttled to prevent rate limits
- **Max Local Storage**: 1000 test report directories before cleanup
