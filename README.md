# daum-crawler


## 프로젝트 내용

### 특정 단어를 키워드로 하는 다음 뉴스를 대상으로 기사, 댓글, 대댓글을 수집함

## 사용 방법

### 터미널에 scrapy crawl daum 입력
### spider 폴더에 있는 daum_spider.py에서 keyword, start_date, end_date 입력
### pipline.py 14번째 줄에서 데이터베이스 경로 설정


## 특징

### 1. 기사, 댓글, 대댓글 총 3개의 테이블로 저장
### 2. 저장하는 정보
- 기사 : 기사 id, 기사 제목, 기사 내용, 기사 작성 시간
- 댓글 : 댓글이 작성된 기사 id, 댓글 id, 댓글 내용, 댓글 작성자, 댓글 작성 시간, 댓글의 좋아요 숫자, 댓글의 싫어요 숫자
- 대댓글 : 대댓글이 작성된 기사 id, 대댓글이 작성된 댓글 id, 대댓글 id, 대댓글 내용, 대댓글 작성자, 대댓글 작성 시간