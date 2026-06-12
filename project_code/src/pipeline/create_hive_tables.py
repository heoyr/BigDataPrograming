"""
create_hive_tables.py
─────────────────────────────────────────────────────────────────
Parquet로 저장된 전처리 결과를 Hive 외부 테이블로 등록
등록 후 localhost:30800 (Hive Studio)에서 SQL 분석 가능

실행: spark-submit --master 'local[2]' --driver-memory 2g src/pipeline/create_hive_tables.py
"""
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ChemSafety-CreateHiveTables") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

HDFS_PROC = "hdfs:///user/maria_dev/chem_safety/processed"

# 데이터베이스 생성
spark.sql("CREATE DATABASE IF NOT EXISTS chem_safety")

print("=== Hive 테이블 생성 ===")

tables = [
    ("disclosure",       "전성분 공개 제품"),
    ("violation",        "위반 제품 목록"),
    ("violation_detail", "위반 제품 상세"),
    ("accident",         "화학사고 사례"),
    ("baseline",         "자가검사 신고 기준"),
]

for tbl, desc in tables:
    spark.sql("DROP TABLE IF EXISTS chem_safety.%s" % tbl)
    spark.sql("""
        CREATE TABLE chem_safety.{tbl}
        USING PARQUET
        LOCATION '{proc}/{tbl}'
    """.format(tbl=tbl, proc=HDFS_PROC))
    print("  %s (%s) OK" % (tbl, desc))

print("\n=== 등록된 테이블 목록 ===")
spark.sql("SHOW TABLES IN chem_safety").show()

print("=== 건수 확인 ===")
for tbl, _ in tables:
    cnt = spark.sql("SELECT COUNT(*) AS cnt FROM chem_safety.%s" % tbl).collect()[0]["cnt"]
    print("  %s: %d건" % (tbl, cnt))

print("\nDone! localhost:30800 에서 chem_safety DB를 선택하여 분석하세요.")
spark.stop()
