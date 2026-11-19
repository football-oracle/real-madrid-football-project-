 

 
CREATE TABLE PLAYER (
    player_id          NUMBER PRIMARY KEY,
    first_name         VARCHAR2(50) NOT NULL,
    last_name          VARCHAR2(50) NOT NULL,
    age                NUMBER(3),
    nationality        VARCHAR2(50),
    position           VARCHAR2(40) NOT NULL,
    preferred_foot     VARCHAR2(10),
    height_cm          NUMBER(5,2),
    weight_kg          NUMBER(5,2),
    jersey_number      NUMBER(2) NOT NULL,
    salary             NUMBER(14,2),
    joined_date        DATE,
    contract_end_date  DATE,

    CONSTRAINT uq_player_jersey UNIQUE (jersey_number),
    
    CONSTRAINT chk_player_foot CHECK (preferred_foot IN ('Right', 'Left', 'Both')),
    
    CONSTRAINT chk_player_jersey CHECK (jersey_number BETWEEN 1 AND 99),
    
    CONSTRAINT chk_player_salary CHECK (salary >= 0),
    
    CONSTRAINT chk_player_age CHECK (age >= 18 AND age <= 100)  
);






CREATE TABLE COACH (
    coach_id       NUMBER PRIMARY KEY,
    coach_name     VARCHAR2(100) NOT NULL,
    age            NUMBER(3),
    nationality    VARCHAR2(50),
    game_style     VARCHAR2(150),
    salary         NUMBER(14,2),

    CONSTRAINT chk_coach_salary CHECK (salary >= 0),           
    CONSTRAINT chk_coach_age CHECK (age >= 18 AND age <= 100)  
);







CREATE TABLE STADIUM (
    stadium_id    NUMBER PRIMARY KEY,
    stadium_name  VARCHAR2(100) NOT NULL,
    location      VARCHAR2(150),
    capacity      NUMBER,
    opened_year   NUMBER(4),
    CONSTRAINT chk_stadium_capacity CHECK (capacity > 0)
);







CREATE TABLE MEDICAL_RECORD (
    record_id     NUMBER PRIMARY KEY,
    player_id     NUMBER NOT NULL,
    injury_type   VARCHAR2(100),
    injury_date   DATE,
    return_date   DATE,
    
    CONSTRAINT fk_medical_player FOREIGN KEY (player_id) REFERENCES PLAYER(player_id)
);







CREATE TABLE ACHIEVEMENT (
    achievement_id    NUMBER PRIMARY KEY,
    achievement_name  VARCHAR2(100) NOT NULL,
    achievement_year  NUMBER(4)
);








 
CREATE OR REPLACE TRIGGER TRG_PLAYER_ID
BEFORE INSERT ON PLAYER FOR EACH ROW

BEGIN
    IF :NEW.player_id IS NULL THEN
        SELECT NVL(MAX(player_id),0)+1 INTO :NEW.player_id FROM PLAYER;
    END IF;
END;
/





CREATE OR REPLACE TRIGGER TRG_COACH_ID
BEFORE INSERT ON COACH FOR EACH ROW

BEGIN
    IF :NEW.coach_id IS NULL THEN
        SELECT NVL(MAX(coach_id),0)+1 INTO :NEW.coach_id FROM COACH;
    END IF;
END;
/





CREATE OR REPLACE TRIGGER TRG_STADIUM_ID
BEFORE INSERT ON STADIUM FOR EACH ROW

BEGIN
    IF :NEW.stadium_id IS NULL THEN
        SELECT NVL(MAX(stadium_id),0)+1 INTO :NEW.stadium_id FROM STADIUM;
    END IF;
END;
/





CREATE OR REPLACE TRIGGER TRG_MEDICAL_ID
BEFORE INSERT ON MEDICAL_RECORD FOR EACH ROW

BEGIN
    IF :NEW.record_id IS NULL THEN
        SELECT NVL(MAX(record_id),0)+1 INTO :NEW.record_id FROM MEDICAL_RECORD;
    END IF;
END;
/





CREATE OR REPLACE TRIGGER TRG_ACHIEVEMENT_ID
BEFORE INSERT ON ACHIEVEMENT FOR EACH ROW

BEGIN
    IF :NEW.achievement_id IS NULL THEN
        SELECT NVL(MAX(achievement_id),0)+1 INTO :NEW.achievement_id FROM ACHIEVEMENT;
    END IF;
END;
/





SELECT * FROM player;

SELECT * FROM coach;

SELECT * FROM achievement;

SELECT * FROM medical_record;

SELECT * FROM stadium;
 



s
INSERT INTO PLAYER (
    first_name, 
    last_name, 
    age, 
    nationality, 
    position, 
    preferred_foot, 
    height_cm, 
    weight_kg, 
    jersey_number, 
    salary, 
    joined_date, 
    contract_end_date
    
) VALUES (
    'Federico', 
    'Valverde', 
    26, 
    'Uruguay', 
    'MF', 
    'Right', 
    182, 
    78, 
    15, 
    8000000, 
    TO_DATE('2018-07-01', 'YYYY-MM-DD'), 
    TO_DATE('2029-06-30', 'YYYY-MM-DD')
);


COMMIT;






 
DELETE FROM PLAYER 
WHERE PLAYER_ID IN (1);
 COMMIT;
 
 
DELETE FROM MEDICAL_RECORD 
WHERE RECORD_ID IN (1); 
 COMMIT;
 


DELETE FROM COACH 
WHERE COACH_ID IN (1);
COMMIT;


DELETE FROM ACHIEVEMENT 
WHERE ACHIEVEMENT_ID IN (1);
COMMIT;

 
DELETE FROM STADIUM 
WHERE STADIUM_ID IN (1);
COMMIT;






CREATE OR REPLACE FUNCTION FN_FORMAT_MONEY (p_amount IN NUMBER) 
RETURN VARCHAR2 IS
BEGIN
    IF p_amount IS NULL THEN
        RETURN '$0.00';
    END IF;
    
    RETURN '$' || TO_CHAR(p_amount, 'FM999,999,999,999.00');
END;
/






CREATE OR REPLACE FUNCTION FN_TOTAL_SALARY (p_table_name IN VARCHAR2) 
RETURN NUMBER IS
    v_total NUMBER := 0;
    
BEGIN
    
    IF p_table_name = 'PLAYER' THEN
        SELECT NVL(SUM(salary), 0) INTO v_total FROM PLAYER;
 
 
    ELSIF p_table_name = 'COACH' THEN
        SELECT NVL(SUM(salary), 0) INTO v_total FROM COACH;
    END IF;
    
    RETURN v_total;
END;
/



SELECT FN_TOTAL_SALARY('PLAYER') AS TOTAL_PLAYER_SALARY FROM DUAL;


SELECT FN_TOTAL_SALARY('COACH') AS TOTAL_COACH_SALARY FROM DUAL;




 