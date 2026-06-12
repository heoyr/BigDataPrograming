# 데이터 설명

## 출처
환경부 에코라이프 공개 REST API  
https://ecolife.mcee.go.kr/openapi/ServiceSvl

## 수집 데이터 구성

| 파일명 | API 서비스명 | 건수 | 용량 | 설명 |
|--------|-------------|------|------|------|
| disclosure.json | irdntChmstryProductList | 211,871건 | 75.0MB | 전성분 공개 제품 목록 |
| violation.json | violtProductList | 6,542건 | 2.7MB | 위반 제품 목록 |
| violation_detail.json | violtProductDetail | 6,542건 | 6.2MB | 위반 제품 상세 |
| accident.json | acdntCaseList | 678건 | 0.2MB | 화학사고 사례 |
| baseline.json | slfsfcfst02List | 291,640건 | 59.5MB | 자가검사 신고 기준 |
| **합계** | | **517,273건** | **143.6MB** | |

> 대용량 raw 데이터는 .gitignore로 제외됨. sample_*.json 참고.

## 스키마

### disclosure.json (전성분 공개 제품)
| 컬럼명 | 설명 |
|--------|------|
| prdt_mstr_no | 제품 마스터 번호 (PK) |
| prdtnm_kor | 제품명(한국어) |
| prdtarm | 제품군 |
| knd | 제품 형태 (액체형, 분무기형 등) |
| prdtn_incme_cmpnynm | 제조/수입 기업명 |
| prdtarm_cd | 제품군 코드 |
| slfsfcfst_no | 자가검사 번호 (baseline JOIN 키) |
| barcd_info | 바코드 |

### violation.json (위반 제품 목록)
| 컬럼명 | 설명 |
|--------|------|
| prdt_mstr_no | 제품 마스터 번호 |
| prdt_nm | 제품명 |
| prdtarm | 제품군 |
| mnfctur_nm | 제조/수입사명 |
| action_de | 처분 일자 (YYYYMMDD) |
| origin_instt | 단속 기관 |

### accident.json (화학사고 사례)
| 컬럼명 | 설명 |
|--------|------|
| acdnt_case_no | 사고 번호 (PK) |
| prdtarm_nm | 관련 제품군 |
| trget_nm | 피해 대상 |
| area_nm | 지역명 |
| acdnt_case_cn | 사고 내용 |

### baseline.json (자가검사 신고 기준)
| 컬럼명 | 설명 |
|--------|------|
| mst_id | 마스터 ID |
| prdt_nm | 제품명 |
| comp_nm | 기업명 |
| item | 품목 (Q2 분석 기준) |
| slfsfcfst_no | 자가검사 번호 (disclosure JOIN 키) |
| reg_date | 등록일 |
