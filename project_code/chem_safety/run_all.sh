#!/bin/bash
# ================================================================
# run_all.sh
# 화학제품 안전 빅데이터 파이프라인 전체 실행 스크립트
# 실행: bash run_all.sh
# ================================================================

set -e  # 오류 발생 시 즉시 중단

echo "================================================"
echo "  ChemSafety BigData Pipeline - 전체 실행"
echo "================================================"

# ── 환경 설정 ──────────────────────────────────────
PYTHON=/usr/bin/python3.6
SPARK_SUBMIT=spark-submit
MASTER='local[2]'
MEM_HIGH=4g
MEM_LOW=2g

# API 키 확인
if [ -z "$ECOLIFE_API_KEY" ]; then
    echo "[ERROR] ECOLIFE_API_KEY 환경변수를 먼저 설정해주세요."
    echo "  export ECOLIFE_API_KEY=your_api_key_here"
    exit 1
fi

# ── Step 1. 데이터 수집 ────────────────────────────
echo ""
echo "[Step 1] 에코라이프 API 데이터 수집..."
$PYTHON src/ingest/fetch_all.py

# ── Step 2. HDFS 적재 ─────────────────────────────
echo ""
echo "[Step 2] HDFS 적재..."
hdfs dfs -mkdir -p /user/maria_dev/chem_safety/raw/disclosure
hdfs dfs -mkdir -p /user/maria_dev/chem_safety/raw/violation
hdfs dfs -mkdir -p /user/maria_dev/chem_safety/raw/accident
hdfs dfs -mkdir -p /user/maria_dev/chem_safety/raw/baseline

hdfs dfs -put -f data/raw/disclosure.json       /user/maria_dev/chem_safety/raw/disclosure/
hdfs dfs -put -f data/raw/violation.json        /user/maria_dev/chem_safety/raw/violation/
hdfs dfs -put -f data/raw/violation_detail.json /user/maria_dev/chem_safety/raw/violation/
hdfs dfs -put -f data/raw/accident.json         /user/maria_dev/chem_safety/raw/accident/
hdfs dfs -put -f data/raw/baseline.json         /user/maria_dev/chem_safety/raw/baseline/

echo "  HDFS 적재 완료"
hdfs dfs -du -h /user/maria_dev/chem_safety/raw/

# ── Step 3. Spark 전처리 ──────────────────────────
echo ""
echo "[Step 3] Spark 전처리 (JSON → Parquet)..."
$SPARK_SUBMIT --master $MASTER --driver-memory $MEM_HIGH src/pipeline/preprocess.py

echo "[Step 3-1] baseline 재처리 (대용량 59.5MB)..."
$SPARK_SUBMIT --master $MASTER --driver-memory $MEM_HIGH src/pipeline/reprocess_baseline.py

# ── Step 4. Hive 테이블 등록 ──────────────────────
echo ""
echo "[Step 4] Hive 테이블 등록..."
$SPARK_SUBMIT --master $MASTER --driver-memory $MEM_LOW src/pipeline/create_hive_tables.py

# ── 완료 ──────────────────────────────────────────
echo ""
echo "================================================"
echo "  완료!"
echo "  분석: localhost:30800 접속"
echo "        Database: chem_safety 선택"
echo "        src/analyze/analysis.hql 쿼리 실행"
echo "================================================"
