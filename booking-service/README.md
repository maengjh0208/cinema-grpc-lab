# booking-service

FastAPI 기반 영화 예매 서비스.

## DB 관계도

```mermaid
erDiagram
    Hall {
        int id PK
        string name
        int total_seats
    }

    Movie {
        int id PK
        string title
        string description
        int runtime_minutes
    }

    Screening {
        int id PK
        int movie_id FK
        int hall_id FK
        datetime datetime
    }

    Seat {
        int id PK
        int hall_id FK
        string seat_number
    }

    Booking {
        int id PK
        int screening_id FK
        int seat_id FK
        int user_id
        datetime created_at
    }

    Hall ||--o{ Screening : "hosts"
    Hall ||--o{ Seat : "has"
    Movie ||--o{ Screening : "shown at"
    Screening ||--o{ Booking : "has"
    Seat ||--o{ Booking : "booked at"
```

> `Booking.user_id`는 auth-service의 users 테이블을 가리키지만,
> 서비스가 분리되어 있어 DB 레벨 FK 제약은 없음. JWT에서 파싱한 값을 저장.
>
> `Booking(screening_id, seat_id)`에 유니크 제약 — 같은 상영의 같은 좌석은 중복 예매 불가.
> 같은 좌석(Seat)이라도 다른 상영(Screening)에서는 다시 예매 가능.
