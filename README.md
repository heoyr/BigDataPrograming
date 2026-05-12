# BigDataPrograming
# 문제 정의: 어떤 문제를 풀고자 하는지, 어떤 데이터를 수집·사용할 것인지    
# spotify api와 youtube api를 활용하여 최근에 뜨고있는 밴드, 밴드 장르 아티스트 종합 순위, 밴드의 록,팝,얼터너티브등의 장르의 인기 변화 등을 알아보고자 한다.
# 기술 스택: 어떤 도구를 사용할 계획인지(Spark, Hive, Kafka 등)
# Spark + Hive
# 구현 계획: 데이터 수집부터 분석까지의 대략적인 파이프라인
# spotify api를 이용하여 밴드 장르의 아티스트의 이름을 알아보고 youtube api를 이용해 조회수와 좋아요 수를 수집하여 JSON 형태로 로컬에 저장한 뒤 HDFS에 적재한다.
# 적재된 데이터를 Spark를 이용하여 전처리후 Hive 를 이용하여 집계,분석을 진행한다. 분석 결과는 Matplotlib /Plotly로 시각화하여 인사이트를 정리한다.
