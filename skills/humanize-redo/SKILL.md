---
name: humanize-redo
description: 가장 최근 윤문 결과를 2차로 다시 다듬는다 — 특정 카테고리·문단·강도 조정도 가능. humanize-korean strict 윤문(Phase B)을 기존 run_id에 재실행해 잔존 finding을 처리한다. 트리거 — "/humanize-redo".
argument-hint: "[조정 지시 — 예: \"번역투만 다시\" \"이 문단만\" \"강도 낮춰\"]"
disable-model-invocation: true
---

# /humanize-redo — 2차 윤문 / 부분 재실행

cwd 기준 가장 최근 `_workspace/{run_id}/`를 찾아 `humanize-korean` 스킬의 heavy 경로로 다시 실행한다.

## 사용자 지시
$ARGUMENTS

위 줄에 `$ARGUMENTS`가 글자 그대로 보이면 런타임이 인자를 바꿔 넣지 않은 것이다. 그때는 사용자가 이 스킬과 함께 보낸 말을 지시로 쓴다.

## 동작
1. `_workspace/YYYY-MM-DD-*/final.md`(또는 `01_input.txt`)를 파일 찾기로 매칭해 최신 `run_id` 식별. 없으면 "이전 실행이 없습니다. `/humanize`로 시작하세요" 안내 후 종료.
2. 사용자 지시를 `humanize-korean` SKILL.md 「부분 재실행 / 후속 명령」 표대로 처리한다:
   - **카테고리 지정**("번역투만", "관용구만", "이모지만") → 진단의 지배 패턴을 해당 카테고리로 한정해 heavy P1부터
   - **문단 지정**("이 문단만", "두 번째 문단만") → 해당 문단만 입력으로 새 run을 만들어 heavy
   - **강도 조정**("강도 낮춰"·"보수적으로", "강도 높여") → 진단의 지배 패턴 개수(3~6)를 줄이거나 늘려 heavy
   - **롤백 요청**("이 변경 되돌려줘") → 해당 문장을 `01_input.txt`의 원문 문장으로 되돌린 뒤 Phase 2.5 게이트를 다시 돌린다
   - 지시 없음·"2차 윤문해줘" → 기존 `final.md`를 새 입력으로 heavy P1부터
3. 이전 `final.md`는 `final_prev.md`로 백업한다.
4. 결과는 `humanize-korean`의 「결과 전달」대로 준다. 이전 결과와 바뀐 곳을 표로 덧붙인다.

## 루프 한도
최대 round 3. 그 이상 미해결이면 `hold_and_report`로 사람 검토 권고.

## 참고
- 풀 파이프라인 신규 실행은 `/humanize`.
- 분류 체계: `humanize-korean/references/ai-tell-taxonomy.md`
