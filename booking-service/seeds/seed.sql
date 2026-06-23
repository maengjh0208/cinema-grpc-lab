-- booking-db 초기 seed 데이터

-- 영화
insert into movies (title, description, runtime_minutes)
values 
('인터스텔라', '우주를 통한 인류 생존 탐사', 169),
('기생충', '두 가족의 계급 갈등', 132);

-- 상영관
insert into halls (name, total_seats)
values
('1관', 5),
('2관', 10);

-- 좌석
insert into seats (hall_id, seat_name)
values
(1, 'A1'),
(1, 'A2'),
(1, 'A3'),
(1, 'A4'),
(1, 'A5'),
(2, 'A1'),
(2, 'A2'),
(2, 'A3'),
(2, 'A4'),
(2, 'A5'),
(2, 'B1'),
(2, 'B2'),
(2, 'B3'),
(2, 'B4'),
(2, 'B5');

-- 상영 일정
insert into screenings (movie_id, hall_id, start_time)
values
(1, 1, '2026-07-01 14:00:00'),
(1, 2, '2026-07-01 18:00:00'),
(2, 1, '2026-07-02 15:00:00');

