# 생활화학제품 안전 데이터 빅데이터 분석

> 빅데이터 프로그래밍 기말 프로젝트

## 프로젝트 개요

환경부 초록누리 API를 통해 수집한 생활화학제품 데이터(143.6MB, 517,273건)를 Hadoop 기반 빅데이터 파이프라인으로 처리·분석하는 시스템입니다.

**핵심 분석 질문:**

- Q1. 어떤 품목에서 화학사고가 가장 많이 발생하는가?
- Q2. 전성분 공개 기업은 미공개 기업보다 위반율이 낮은가?
- Q3. 위반 기업의 재범 패턴이 존재하는가?

---

## 기술 스택

| 단계        | 기술                       | 역할                                  |
| ----------- | -------------------------- | ------------------------------------- |
| 데이터 수집 | Python 3.6 (requests, xml) | 초록누리 REST API 호출                |
| 저장        | HDFS                       | 원시 JSON 적재                        |
| 전처리      | Apache Spark (PySpark)     | 필요 컬럼 선택, 결측치 제거           |
| 분석        | Apache Hive (HiveQL)       | GROUP BY / JOIN / CASE WHEN 집계 분석 |
| 실행 환경   | HDP Sandbox                | sandbox-hdp.hortonworks.com           |

---

## 데이터 규모

| 데이터           | 건수          | 용량        |
| ---------------- | ------------- | ----------- |
| 전성분 공개 제품 | 211,871건     | 75.0MB      |
| 위반 제품 목록   | 6,542건       | 2.7MB       |
| 위반 제품 상세   | 6,542건       | 6.2MB       |
| 화학사고 사례    | 678건         | 0.2MB       |
| 자가검사 기준    | 291,640건     | 59.5MB      |
| **합계**         | **517,273건** | **143.6MB** |

---

## 디렉터리 구조

```
chem_safety/
├── README.md                        # 프로젝트 설명 (이 파일)
├── run_all.sh                       # 전체 파이프라인 자동 실행
├── .gitignore
├── data/
│   ├── README.md                    # 데이터 스키마 설명
│   ├── sample_disclosure.json       # 샘플 데이터 (100건)
│   ├── sample_violation.json
│   ├── sample_accident.json
│   └── sample_baseline.json
├── src/
│   ├── ingest/
│   │   └── fetch_all.py             # [Step 1] API 수집 스크립트
│   ├── pipeline/
│   │   ├── preprocess.py            # [Step 2] Spark 전처리
│   │   └── create_hive_tables.py    # [Step 3] Hive 테이블 생성
│   └── analyze/
│       └── analysis.hql             # [Step 4] HiveQL 분석 쿼리
└── results/
    ├── q1_accident.csv              # Q1 분석 결과
    ├── q2_violation_rate.csv        # Q2 분석 결과
    └── q3_recidivism.csv            # Q3 분석 결과
```

---

## 실행 방법

### 사전 준비

```bash
# 1. API 키 환경변수 설정
export ECOLIFE_API_KEY="your_api_key_here"

# 2. requests 라이브러리 설치
pip3 install requests --user
```

### 전체 자동 실행

```bash
cd ~/chem_safety
bash run_all.sh
```

### 단계별 수동 실행

**Step 1. 데이터 수집**

```bash
/usr/bin/python3.6 src/ingest/fetch_all.py
```

**Step 2. HDFS 적재**

```bash
hdfs dfs -mkdir -p /user/maria_dev/chem_safety/raw/disclosure
hdfs dfs -put -f data/raw/disclosure.json /user/maria_dev/chem_safety/raw/disclosure/
hdfs dfs -put -f data/raw/violation.json /user/maria_dev/chem_safety/raw/violation/
hdfs dfs -put -f data/raw/accident.json /user/maria_dev/chem_safety/raw/accident/
hdfs dfs -put -f data/raw/baseline.json /user/maria_dev/chem_safety/raw/baseline/
```

**Step 3. Spark 전처리**

```bash
spark-submit --master 'local[2]' --driver-memory 4g src/pipeline/preprocess.py
```

**Step 4. Hive 테이블 생성**

```bash
spark-submit --master 'local[2]' --driver-memory 2g src/pipeline/create_hive_tables.py
```

**Step 5. 분석 쿼리 실행**

```
localhost:30800 접속
→ Database: chem_safety 선택
→ src/analyze/analysis.hql 쿼리 순서대로 실행
```

---

## 주요 분석 결과

### Q1. 품목별 화학사고 발생 건수

| 품목     | 사고 건수 |
| -------- | --------- |
| 표백제   | 211건     |
| 접착제   | 126건     |
| 세정제   | 99건      |
| 합성세제 | 91건      |

→ **상위 3개 품목(표백제·접착제·세정제)이 전체 678건의 63% 차지**

### Q2. 전성분 공개 기업 vs 미공개 기업 위반율

| 기업 유형        | 전체 기업 수 | 위반 기업 수 | 위반율 |
| ---------------- | ------------ | ------------ | ------ |
| 전성분 공개 기업 | 129개사      | 1개사        | 0.8%   |
| 미공개 기업      | 8,615개사    | 4,026개사    | 46.7%  |

→ **미공개 기업 위반율이 공개 기업보다 약 60배 높음**

### Q3. 위반 기업 재범 패턴

| 구분            | 기업 수         | 위반 비율 |
| --------------- | --------------- | --------- |
| 1건 (일회성)    | 3,064개사 (75%) | 47%       |
| 2~4건 (재범)    | 839개사 (21%)   | 31%       |
| 5건 이상 (상습) | 123개사 (3%)    | 21%       |

→ **재범+상습 기업(962개사)이 전체 위반의 52% 차지**

---

## AI 도구 사용 내역

- Claude (Anthropic): Spark 전처리 코드 디버깅, HiveQL 오류 수정, 보고서 작성 보조

---

## 참고 자료

- 환경부 초록누리 API: https://ecolife.mcee.go.kr/ecolife/infoCenter/openApi?pMENU_NO=588
