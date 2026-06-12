-- ================================================================
-- analysis.hql
-- 생활화학제품 안전 데이터 분석 쿼리
-- 실행 환경: localhost:30800 (Hive Studio) > chem_safety DB 선택
-- 각 쿼리는 별도 Worksheet에서 실행
-- ================================================================

USE chem_safety;

-- ================================================================
-- Q1. 품목별 화학사고 발생 건수
--     어떤 품목에서 사고가 가장 많이 발생하는가?
-- ================================================================
SELECT
    prdtarm_nm,
    COUNT(*) AS accident_count
FROM chem_safety.accident
WHERE prdtarm_nm != ''
GROUP BY prdtarm_nm
ORDER BY accident_count DESC;


-- ================================================================
-- Q2. 전성분 공개 기업 vs 미공개 기업 위반율 비교
--     공개 기업(disclosure)과 위반 기업(violation)을 기업명으로 조인
-- ================================================================
SELECT
    CASE
        WHEN d.prdtn_incme_cmpnynm IS NOT NULL THEN '공개기업'
        ELSE '미공개기업'
    END AS disclosure_type,
    COUNT(DISTINCT v.mnfctur_nm)   AS violated_companies,
    COUNT(DISTINCT v.prdt_mstr_no) AS violated_products
FROM chem_safety.violation v
LEFT JOIN chem_safety.disclosure d
    ON v.mnfctur_nm = d.prdtn_incme_cmpnynm
GROUP BY
    CASE
        WHEN d.prdtn_incme_cmpnynm IS NOT NULL THEN '공개기업'
        ELSE '미공개기업'
    END;


-- ================================================================
-- Q3. 위반 기업 재범 패턴 분석
--     한 번 위반한 기업이 반복적으로 위반하는가?
-- ================================================================
SELECT
    CASE
        WHEN violation_count = 1             THEN '1건 (일회성)'
        WHEN violation_count BETWEEN 2 AND 4 THEN '2~4건 (재범)'
        WHEN violation_count >= 5            THEN '5건 이상 (상습)'
    END AS group_type,
    COUNT(DISTINCT mnfctur_nm) AS company_count,
    SUM(violation_count)       AS total_violations
FROM (
    SELECT
        mnfctur_nm,
        COUNT(DISTINCT prdt_mstr_no) AS violation_count
    FROM chem_safety.violation
    WHERE mnfctur_nm != ''
    GROUP BY mnfctur_nm
) t
GROUP BY
    CASE
        WHEN violation_count = 1             THEN '1건 (일회성)'
        WHEN violation_count BETWEEN 2 AND 4 THEN '2~4건 (재범)'
        WHEN violation_count >= 5            THEN '5건 이상 (상습)'
    END;
