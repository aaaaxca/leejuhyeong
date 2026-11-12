# 이주형 클래스 — 작업 안내

SBS아카데미AIX 안산 이주형 학과장의 수업 허브. GitHub Pages로 배포: https://aaaaxca.github.io/leejuhyeong/

## 구조
- `index.html` — 강사용 허브. 파일 안 `const DATA = [...]`에 모든 카테고리·과목 목록이 있음. 허브 전체가 4자리 번호 잠금(`HUB_LOCK`, SHA-256 값, 번호는 사용자만 앎). 과목 카드는 학생 페이지를 새 탭으로 연다.
- `content/<과목id>/` — 과목 본문. `overview.html`(과정 첫 페이지 아래쪽) + `01.html`~ (차시별 본문, 첫 줄 `day-head`의 h3가 차시 제목).
- `c/` — **자동 생성물. 직접 고치지 말 것.** 학생 배포용 페이지(`c/<id>-<key>.html`, 차시는 `c/<id>-<key>/01.html`).
- `build.py` — `python3 build.py` 실행 시 DATA와 content를 읽어 `c/` 전체를 다시 만듦. key 없는 과목엔 key를 만들어 index.html에 기록.

## 과목 하나 작업하는 순서 (한 대화 = 한 과목)
1. `git pull --rebase origin main` 먼저 (다른 대화에서 올린 변경 반영).
2. 해당 과목의 `content/<id>/` 파일과 DATA의 그 과목 한 줄만 고친다. 다른 과목은 건드리지 않는다.
   - 차시 본문이 생기면 DATA 그 과목에 `content:"<id>"`, `projects:[{ title:"...", doc:"01" }, ...]` 를 넣는다. 예시는 `ai-basic`.
3. `python3 build.py`
4. 커밋 후 `git push origin main`. 끝나면 사용자에게 1~2분 뒤 새로고침하라고 한 줄로 알린다.

## 사용량을 아끼는 원칙
- 파일은 필요한 부분만 읽고 Edit로 부분 수정. 전체 재작성·전체 읽기는 피한다.
- 스크린샷 확인은 사용자가 요청하거나 레이아웃을 새로 만들 때만.
- 여러 수정은 모아서 한 번에 빌드·푸시.

## 디자인 규칙
- 블랙 톤, 차분하게. 색 박스·이모지 쓰지 않음. 제목은 Noto Serif KR.
- 본문에 쓸 수 있는 클래스: `hub-section`, `hub-section-head`, `table-scroll`, `callout`(`--tip`), `practice-card`/`practice-title`/`practice-prep`, `adjust`(조절 구간), `out`(오늘 결과물). 스타일은 `build.py`의 `CONTENT_CSS`.
- 학생 페이지에는 허브나 다른 과목으로 가는 링크를 넣지 않는다.

## 과목 id
시니어: `ai-basic`, `office-basic` / AI: `prompt`, `agent1`, `agent2`, `biz-agent`, `sns`, `short-drama` / 모션: `ae1`, `ae2`, `pr1`, `pr2` / 편집 디자인: `design-basic`, `design-adv` / CG: `maya1`~`maya8` / 세미나: `ai-draw-move`, `figure`, `zbrush`
