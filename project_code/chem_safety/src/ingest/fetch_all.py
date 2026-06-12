import requests
import xml.etree.ElementTree as ET
import json
import os
import time

# API 설정
API_KEY = os.environ.get("ECOLIFE_API_KEY", "")
BASE_URL = "https://ecolife.mcee.go.kr/openapi/ServiceSvl"
PAGE_SIZE = 20
RAW_DIR = os.path.expanduser("~/chem_safety/data/raw")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(os.path.join(RAW_DIR, "baseline_chunks"), exist_ok=True)

# API 1페이지 호출 함수
def get_page(service_name, page, extra={}):
    params = {
        "ServiceName": service_name,
        "AuthKey": API_KEY,
        "PageCount": PAGE_SIZE,
        "PageNum": page,
    }
    params.update(extra)

    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        root = ET.fromstring(r.text)
        total = int(root.findtext("count") or 0)
        items = []
        for row in root.iter("row"):
            item = {}
            for child in row:
                item[child.tag] = child.text.strip() if child.text else ""
            items.append(item)
        return items, total
    except Exception as e:
        print("오류 발생: " + str(e))
        return [], 0

# 전체 페이지 수집 후 JSON 저장
def fetch_all(service_name, filename, extra={}):
    out_path = os.path.join(RAW_DIR, filename)

    # 이미 수집된 파일이면 건너뜀
    if os.path.exists(out_path):
        print(filename + " 이미 존재, 건너뜀")
        return

    print(service_name + " 수집 시작...")
    items_first, total = get_page(service_name, 1, extra)
    total_pages = total // PAGE_SIZE
    if total % PAGE_SIZE != 0:
        total_pages += 1
    print("총 " + str(total) + "건 / " + str(total_pages) + "페이지")

    all_items = []
    for page in range(1, total_pages + 1):
        items, _ = get_page(service_name, page, extra)
        all_items.extend(items)
        if page % 50 == 0:
            print(str(page) + "/" + str(total_pages) + " 페이지 완료")
        time.sleep(0.3)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(filename + " 저장 완료 (" + str(len(all_items)) + "건)")


# 1. 전성분 공개 제품
print("=" * 40)
print("1. 전성분 공개 제품 수집")
fetch_all("irdntChmstryProductList", "disclosure.json")

# 2. 위반 제품 목록
print("=" * 40)
print("2. 위반 제품 목록 수집")
fetch_all("violtProductList", "violation.json", {"prdtarmCd": "07"})

# 3. 위반 제품 상세 (violation.json의 제품 ID로 1건씩 호출)
print("=" * 40)
print("3. 위반 제품 상세 수집")
detail_path = os.path.join(RAW_DIR, "violation_detail.json")
if not os.path.exists(detail_path):
    with open(os.path.join(RAW_DIR, "violation.json"), encoding="utf-8") as f:
        violation_list = json.load(f)

    details = []
    for i, item in enumerate(violation_list):
        prdt_no = item.get("prdt_mstr_no", "")
        cd = item.get("prdtarm_cd", "07")
        if prdt_no == "":
            continue
        rows, _ = get_page("violtProductDetail", 1, {"prdtMstrNo": prdt_no, "prdtarmCd": cd})
        details.extend(rows)
        if (i + 1) % 500 == 0:
            print(str(i + 1) + "/" + str(len(violation_list)) + " 처리 완료")
        time.sleep(0.3)

    with open(detail_path, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print("violation_detail.json 저장 완료 (" + str(len(details)) + "건)")
else:
    print("violation_detail.json 이미 존재, 건너뜀")

# 4. 화학사고 사례
print("=" * 40)
print("4. 화학사고 사례 수집")
fetch_all("acdntCaseList", "accident.json")

# 5. 자가검사 기준 (데이터가 많아서 청크로 나눠서 저장)
print("=" * 40)
print("5. 자가검사 기준 수집 (대용량 - 청크 방식)")
CHUNK_DIR = os.path.join(RAW_DIR, "baseline_chunks")
baseline_path = os.path.join(RAW_DIR, "baseline.json")

if not os.path.exists(baseline_path):
    _, total = get_page("slfsfcfst02List", 1, {})
    total_pages = total // PAGE_SIZE
    if total % PAGE_SIZE != 0:
        total_pages += 1
    print("총 " + str(total) + "건 / " + str(total_pages) + "페이지")

    buffer = []
    chunk_idx = 0
    CHUNK_SIZE = 1000  # 1000페이지마다 파일 저장

    for page in range(1, total_pages + 1):
        items, _ = get_page("slfsfcfst02List", page, {})
        buffer.extend(items)

        if page % 100 == 0:
            print(str(page) + "/" + str(total_pages) + " 페이지 완료")

        # 1000페이지마다 청크 저장
        if page % CHUNK_SIZE == 0 or page == total_pages:
            chunk_file = os.path.join(CHUNK_DIR, "chunk_" + str(chunk_idx) + ".json")
            with open(chunk_file, "w", encoding="utf-8") as f:
                json.dump(buffer, f, ensure_ascii=False)
            print("청크 " + str(chunk_idx) + " 저장 완료")
            buffer = []
            chunk_idx += 1

        time.sleep(0.3)

    # 청크 파일 합치기
    print("청크 파일 합치는 중...")
    all_data = []
    for fname in sorted(os.listdir(CHUNK_DIR)):
        if fname.endswith(".json"):
            with open(os.path.join(CHUNK_DIR, fname), encoding="utf-8") as f:
                all_data.extend(json.load(f))

    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False)
    print("baseline.json 저장 완료 (" + str(len(all_data)) + "건)")
else:
    print("baseline.json 이미 존재, 건너뜀")

print("=" * 40)
print("모든 데이터 수집 완료!")