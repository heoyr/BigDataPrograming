"""
preprocess.py
─────────────────────────────────────────────────────────────────
HDFS에 적재된 JSON 파일을 Spark로 읽어 전처리 후 Parquet으로 저장
실행: spark-submit --master 'local[2]' --driver-memory 4g src/pipeline/preprocess.py
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim

spark = SparkSession.builder \
    .appName("ChemSafety-Preprocess") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

HDFS_RAW  = "hdfs:///user/maria_dev/chem_safety/raw"
HDFS_PROC = "hdfs:///user/maria_dev/chem_safety/processed"


def read_json(path):
    """multiLine JSON 읽기 (배열 형태의 대용량 JSON 파일 지원)"""
    return spark.read \
        .option("multiLine", "true") \
        .option("encoding", "UTF-8") \
        .json(path)


# ─────────────────────────────────────────────
# 1. disclosure (전성분 공개 제품)
# ─────────────────────────────────────────────
print("=== 1. disclosure ===")
df_disc = read_json(HDFS_RAW + "/disclosure/disclosure.json")
df_disc = df_disc.select(
    trim(col("prdt_mstr_no")).alias("prdt_mstr_no"),   # 제품 마스터 번호
    trim(col("prdtnm_kor")).alias("product_name"),      # 제품명(한국어)
    trim(col("prdtarm")).alias("product_category"),     # 제품군
    trim(col("knd")).alias("product_type"),             # 제품 형태
    trim(col("prdtn_incme_cmpnynm")).alias("company_name"),  # 기업명
    trim(col("prdtarm_cd")).alias("category_cd"),       # 제품군 코드
    trim(col("slfsfcfst_no")).alias("slfsfcfst_no"),    # 자가검사번호 (JOIN 키)
    trim(col("barcd_info")).alias("barcode"),           # 바코드
) \
.filter(col("prdt_mstr_no") != "") \
.filter(col("product_name") != "")

df_disc.write.mode("overwrite").parquet(HDFS_PROC + "/disclosure")
print("  rows: %d" % df_disc.count())

# ─────────────────────────────────────────────
# 2. violation (위반 제품 목록)
# ─────────────────────────────────────────────
print("=== 2. violation ===")
df_viol = read_json(HDFS_RAW + "/violation/violation.json")
df_viol = df_viol.select(
    trim(col("prdt_mstr_no")).alias("prdt_mstr_no"),
    trim(col("prdt_nm")).alias("prdt_nm"),           # 제품명
    trim(col("prdtarm")).alias("prdtarm"),            # 제품군
    trim(col("prdtarm_cd")).alias("prdtarm_cd"),
    trim(col("mnfctur_nm")).alias("mnfctur_nm"),     # 제조/수입사
    trim(col("origin_instt")).alias("origin_instt"), # 단속기관
    trim(col("action_de")).alias("action_de"),       # 처분일자
) \
.filter(col("prdt_mstr_no") != "")

# 연도 파생 컬럼 추가
df_viol = df_viol.withColumn("action_year", col("action_de").substr(1, 4))
df_viol.write.mode("overwrite").parquet(HDFS_PROC + "/violation")
print("  rows: %d" % df_viol.count())

# ─────────────────────────────────────────────
# 3. violation_detail (위반 제품 상세)
# ─────────────────────────────────────────────
print("=== 3. violation_detail ===")
df_vdet = read_json(HDFS_RAW + "/violation/violation_detail.json")
df_vdet = df_vdet.select(
    trim(col("prdt_mstr_no")).alias("prdt_mstr_no"),
    trim(col("prdt_nm")).alias("prdt_nm"),
    trim(col("prdtarm")).alias("prdtarm"),
    trim(col("mnfctur_nm")).alias("mnfctur_nm"),
    trim(col("violt_cn")).alias("violt_cn"),         # 위반 내용
    trim(col("action_cn")).alias("action_cn"),       # 조치 내용
    trim(col("act_org")).alias("act_org"),           # 조치 기관
    trim(col("action_de")).alias("action_de"),
) \
.filter(col("prdt_mstr_no") != "")

df_vdet.write.mode("overwrite").parquet(HDFS_PROC + "/violation_detail")
print("  rows: %d" % df_vdet.count())

# ─────────────────────────────────────────────
# 4. accident (화학사고 사례)
# ─────────────────────────────────────────────
print("=== 4. accident ===")
df_acc = read_json(HDFS_RAW + "/accident/accident.json")
df_acc = df_acc.select(
    trim(col("acdnt_case_no")).alias("acdnt_case_no"),   # 사고 번호
    trim(col("prdtarm_nm")).alias("prdtarm_nm"),         # 관련 제품군
    trim(col("trget_nm")).alias("trget_nm"),             # 피해 대상
    trim(col("area_nm")).alias("area_nm"),               # 지역
    trim(col("acdnt_case_cn")).alias("acdnt_case_cn"),   # 사고 내용
) \
.filter(col("acdnt_case_no") != "")

df_acc.write.mode("overwrite").parquet(HDFS_PROC + "/accident")
print("  rows: %d" % df_acc.count())

# ─────────────────────────────────────────────
# 5. baseline (자가검사 신고 기준)
#    291,640건 대용량 → driver-memory 4g 필요
# ─────────────────────────────────────────────
print("=== 5. baseline ===")
df_base = read_json(HDFS_RAW + "/baseline/baseline.json")
df_base = df_base.select(
    trim(col("mst_id")).alias("mst_id"),
    trim(col("prdt_nm")).alias("prdt_nm"),       # 제품명
    trim(col("comp_nm")).alias("comp_nm"),       # 기업명
    trim(col("item")).alias("item"),             # 품목 (Q2 분석 기준)
    trim(col("est_no")).alias("est_no"),
    trim(col("slfsfcfst_no")).alias("slfsfcfst_no"),  # 자가검사번호 (JOIN 키)
    trim(col("reg_date")).alias("reg_date"),     # 등록일
) \
.filter(col("prdt_nm") != "")

# 연도 파생 컬럼 추가
df_base = df_base.withColumn("reg_year", col("reg_date").substr(1, 4))
df_base.write.mode("overwrite").parquet(HDFS_PROC + "/baseline")
print("  rows: %d" % df_base.count())

print("\n=== 전처리 완료 ===")
spark.stop()
