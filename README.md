# im-korean

im-korean은 한국어 글쓰기 스킬 네 저장소를 하나로 합친 Claude Code 플러그인입니다.
네 저장소에 겹쳐 있던 규칙은 한 곳에만 남겼습니다.
서로 반대 방향을 가리키던 규칙은 한쪽으로 맞췄습니다.

## 들어 있는 것

| 종류 | 이름 | 하는 일 |
|---|---|---|
| 스킬 | `humanize-korean` | AI 티가 나는 한국어 글을 사람 글처럼 고칩니다. 패턴 93개(활성 92개)를 봅니다. |
| 스킬 | `humanize` | `/humanize`로 `humanize-korean`을 시작합니다. |
| 스킬 | `humanize-scan` | 판별력이 확인된 신호 6개로 AI 티가 얼마나 있는지 잽니다. 파일을 만들지 않습니다. |
| 스킬 | `humanize-redo` | `/humanize-redo`로 가장 최근 윤문 결과를 다시 고칩니다. |
| 스킬 | `korean-grammar-checker` | 맞춤법, 띄어쓰기, 문장부호가 맞는지 봅니다. |
| 스킬 | `korean-style-guide` | 한 문서 안에서 용어, 날짜와 숫자 표기, 높임 등급이 고른지 봅니다. |
| 하위 에이전트 | `humanize-diagnostician`, `humanize-monolith`, `humanize-finalizer` | `humanize-korean`이 부르는 진단, 윤문, 마무리 담당입니다. |
| 하위 에이전트 | `korean-ai-tell-taxonomist` | 패턴 목록을 고치고 넓힐 때 씁니다. 윤문 중에는 부르지 않습니다. |
| 출력 스타일 | `fluent-korean` | Claude가 한국어로 답할 때 지킬 규칙입니다. |

세 검사 스킬은 아래 순서로 돌립니다.

1. `korean-grammar-checker`
2. `korean-style-guide`
3. `humanize-korean`

`humanize-korean` 뒤에 맞춤법 검사를 다시 돌릴 때는 확실한 오류만 고칩니다.

## 설치

`humanize-korean`의 판정 스크립트에는 Python 3이 필요합니다. 스크립트는 표준 라이브러리만 씁니다.

### 플러그인으로 설치

Claude Code에서 아래 두 명령을 차례로 입력합니다.

```text
/plugin marketplace add ImTotem/im-korean
/plugin install im-korean@im-korean
```

### 직접 복사

플러그인 기능을 쓰지 않는다면 파일을 `~/.claude` 아래로 복사합니다.

```bash
git clone https://github.com/ImTotem/im-korean.git
cd im-korean
mkdir -p ~/.claude/skills ~/.claude/agents ~/.claude/output-styles
cp -r skills/* ~/.claude/skills/
cp -r scripts ~/.claude/skills/humanize-korean/
cp agents/*.md ~/.claude/agents/
cp output-styles/fluent-korean.md ~/.claude/output-styles/
```

둘째 `cp`는 판정 스크립트를 `humanize-korean` 스킬 폴더 안에 넣습니다.
직접 복사한 설치에서는 `humanize-korean`이 그 자리에서 스크립트를 찾습니다.

### 출력 스타일 켜기

출력 스타일은 설치만으로 켜지지 않습니다.
Claude Code 설정의 출력 스타일 목록에서 `fluent-korean`을 고릅니다.
직접 복사한 경우에는 `~/.claude/settings.json`에 `"outputStyle": "fluent-korean"`을 넣어도 됩니다.
켠 설정은 새 세션부터 적용됩니다.

## 쓰는 법

스킬은 요청 내용을 보고 저절로 불립니다. 이름을 직접 불러도 됩니다.

| 요청 예 | 불리는 스킬 |
|---|---|
| "이 글 AI 티 없애줘", "번역투 고쳐줘", "1000자로 맞춰서 다듬어줘" | `humanize-korean` |
| "이 글 AI 같아?", "AI 티 있나 봐줘" | `humanize-scan` |
| "맞춤법 검사해줘", "띄어쓰기 봐줘" | `korean-grammar-checker` |
| "용어 통일됐는지 봐줘", "날짜 표기 맞춰줘" | `korean-style-guide` |

`humanize-korean`은 작업 폴더에 `_workspace/` 폴더를 만들고 중간 결과를 남깁니다.

## 합친 방법

### 출처

| 저장소 | 커밋 | 가져온 것 |
|---|---|---|
| [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai) | `b37e020` | `humanize-korean`, `humanize`, `humanize-scan`, `humanize-redo`, 하위 에이전트 4개, 판정 스크립트 |
| [DaleSeo/korean-skills](https://github.com/DaleSeo/korean-skills) | `ae12ba2` | `grammar-checker`, `style-guide`, `humanizer`의 고유 패턴 |
| [NomaDamas/k-skill](https://github.com/NomaDamas/k-skill) | `1dc4e68` | `korean-humanizer`의 고유 패턴과 기능 |
| [snflkd/fluent-korean](https://github.com/snflkd/fluent-korean) | `ce8683f` | `fluent-korean` 출력 스타일 |

### 윤문 스킬

- 윤문 스킬은 세 개였습니다. im-not-ai의 `humanize-korean`을 바탕으로 삼았습니다.
- DaleSeo `humanizer`와 k-skill `korean-humanizer`는 im-not-ai와 같은 방법을 씁니다. 심각도 S1·S2·S3, 변경률 30%·50% 제한, 등급 A~D가 같습니다.
- 그래서 두 스킬에만 있던 패턴 8개를 `humanize-korean`의 패턴 목록으로 옮겼습니다.
  - `A-25` 영어 구문 직역 잔여형 "~중 하나", "~의 경우"
  - `C-15` 본문 콜론 도입 "다음과 같습니다:"
  - `C-16` 셋씩 묶기
  - `D-15` 챗봇 응대와 아첨
  - `D-16` 예고 멘트
  - `F-8` 동의어 돌려쓰기
  - `G-4` 지식 한계 면피
  - `J-5` 따옴표 종류 혼용과 문장 끝 물결표
- 옮긴 패턴은 모두 `estimated`입니다. im-not-ai의 대조 코퍼스로 재지 않았다는 뜻입니다.
- 옮기려다 뺀 패턴은 4개입니다. im-not-ai가 직접 재어 보고 버렸거나 보류한 패턴입니다.
  - "X에서 Y까지" 가짜 범위는 실측에서 사람이 2.6배 더 썼습니다.
  - 띄어쓰기가 지나치게 고른 것은 v1.6에서 보류되었습니다.
  - 가운뎃점 열거는 신문에도 흔하다는 이유로 보류되었습니다.
  - "해당·본" 반복은 실측에서 사람 글과 차이가 없었습니다.
- 기능도 다섯 가지를 옮겼습니다.
  - k-skill에서는 목표 분량, 진단만 하기, 서식 티만 고치기, 결과만 받기를 옮겼습니다.
  - DaleSeo에서는 아주 짧은 입력 처리를 옮겼습니다.
- 말투 샘플 기능은 옮기지 않았습니다. im-not-ai가 v1.5에서 일부러 걷어낸 방향입니다.
- im-not-ai 안에서 서로 반대이던 규칙 세 쌍을 맞췄습니다.
  - `C-10`은 엠대시를 권하고 `J-3`은 엠대시를 잡았습니다. `C-10`에서 엠대시를 뺐습니다.
  - `J-3`은 괄호로 바꾸라 하고 `J-4`는 괄호를 줄이라 했습니다. `J-3`에서 괄호를 뺐습니다.
  - 처방집은 framework를 번역하라 하고 `B-2`는 원어로 두라 했습니다. 번역은 일반 독자 대상일 때만 하도록 좁혔습니다.
- 청자 높임 등급이 섞이는 문제(`E-7`)는 `korean-style-guide`가 맡습니다.

### 맞춤법 검사와 문체 통일

- 두 스킬 이름 앞에 `korean-`을 붙였습니다. 다른 스킬과 이름이 겹치지 않게 하려는 것입니다.
- 세 스킬이 같은 현상을 다르게 판정하던 곳을 한 곳으로 모았습니다.
  - "10개"와 "10 개"는 맞춤법상 둘 다 맞습니다. `korean-grammar-checker`는 둘 다 맞다고만 합니다. `korean-style-guide`는 한 문서 안에서 섞인 것만 잡습니다.
  - 영어식 쉼표, 강조 따옴표, 굵게, 이모지가 많은지는 `humanize-korean`이 봅니다.
- 틀린 고친 예를 바로잡았습니다. "웬 일이야", "댓수", "-되요", "캐릭터 → 캐릭터" 같은 예입니다.
- 장르별 권장 표가 세 번씩 되풀이되며 값이 서로 달랐습니다. `korean-style-guide`의 장르 매트릭스 하나만 남겼습니다.

### 출력 스타일

- fluent-korean의 두 판 가운데 코딩 지침을 유지하는 판(`keep-coding-instructions: true`)만 남겼습니다.
- 본문에 있던 연결어미 뒤 쉼표 8개를 뺐습니다. `humanize-korean`이 강한 AI 신호로 보는 쉼표입니다.
- 엠대시를 콜론으로 바꾸라는 문장을 "문장을 나누거나 연결어미로 잇는다"로 바꿨습니다.
- 정도부사("매우", "정말")와 진행형 "~고 있다"를 꾸밈으로 붙이지 않는다는 문장을 더했습니다.

### 넣지 않은 것

- im-not-ai의 Codex, Gemini, Copilot용 파일과 테스트는 넣지 않았습니다.
- im-not-ai의 부속 스킬 `commit-ko`는 넣지 않았습니다. im-not-ai도 기본 설치에서 빼 둔 스킬입니다.

## 패턴 목록 고치기

`humanize-korean`의 패턴 원본은 `skills/humanize-korean/references/ai-tell-taxonomy.md` 하나입니다.
`quick-rules.md`와 `diagnosis-rules.md`는 이 파일에서 만들어집니다. 두 파일을 손으로 고치지 않습니다.
원본을 고친 뒤 저장소 루트에서 아래 명령을 돌립니다.

```bash
python scripts/build_quick_rules.py
python scripts/build_diagnosis_rules.py
python scripts/build_quick_rules.py --check
python scripts/build_diagnosis_rules.py --check
```

## 라이선스

MIT입니다. 네 저장소도 모두 MIT입니다.
각 저장소의 원래 라이선스 전문은 `licenses/` 폴더에 그대로 두었습니다.
