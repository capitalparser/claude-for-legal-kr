# 법제처 MCP만 쓰는 변호사에게 설명하는 claude-for-legal-kr의 차이

## 한 줄 결론

법제처 MCP는 법령과 판례를 찾아주는 검색 인프라이고,
`claude-for-legal-kr`은 그 검색 결과를 실무 검토 절차에 넣어 계약서,
DPA, 규제 검토 메모, gap table, 수정 요청안을 만들어주는 업무 레이어임.

즉, 차이는 "자료를 찾느냐"가 아니라 "검토 업무가 어디까지 자동화되느냐"임.

## 변호사에게 처음 던질 말

이미 법제처 MCP로 법령 검색을 잘 하고 있다면, `claude-for-legal-kr`은
그걸 대체하려는 도구가 아님. 오히려 법제처 MCP를 공식 출처 엔진으로
쓰면서, 반복적인 검토 업무를 표준 절차와 산출물로 묶어주는 레이어임.

예를 들어 개인정보 처리위탁 계약을 볼 때, 법제처 MCP만 있으면
"개인정보 보호법 제26조 찾아줘"까지는 잘 됨. 하지만 실제 업무는 그
다음부터 시작됨. 이 계약이 처리위탁인지 제3자 제공인지, 국외 이전
조항이 충분한지, 재위탁 통지가 있는지, AI 학습 목적이 위탁 범위를
넘는지, breach notification이 한국 고객 대응에 충분한지 판단해야 함.

`claude-for-legal-kr`은 이 후반부를 구조화함. 법령을 찾은 뒤 계약서
조항별로 required gap, recommended improvement, source status, review gate를
붙여 검토 메모 초안을 만드는 방식임.

## 기능 차이 요약

| 구분 | 법제처 MCP만 사용 | claude-for-legal-kr + 법제처 MCP |
|---|---|---|
| 기본 역할 | 법령, 판례, 행정자료 검색 | 검색 결과를 업무 검토 절차에 적용 |
| 주 입력 | 법령명, 조문번호, 자연어 질의 | 계약서, DPA, 약관, 업무 상황, 검토 요청 |
| 주 출력 | 조문 원문, 검색 결과, 식별자 | 검토 메모, gap table, 위험 플래그, 수정 제안 |
| 판단 구조 | 사용자가 직접 구성 | pass / conditional / fail 구조 제공 |
| 쟁점 분류 | 검색자가 직접 판단 | required gaps vs recommended improvements 분리 |
| 출처 처리 | 법령 조회 중심 | verified_source / model_inference / user_supplied_unverified 구분 |
| 실무 반복성 | 매번 새로 질의 구성 | skill별 체크리스트와 산출물 형식 재사용 |
| 안전장치 | citation 확인 중심 | citation 확인 + review gate + 외부 사용 차단 문구 |
| 팀 공유 | 검색 결과 공유 | 검토 기준, 산출물 템플릿, issue taxonomy 공유 |

## 실무 예시: PIPA / DPA review

### 법제처 MCP만 쓸 때

변호사는 이런 식으로 직접 질의함.

```text
개인정보 보호법 제26조 찾아줘
개인정보 보호법 제28조의8 찾아줘
개인정보 처리위탁과 제3자 제공 관련 판례 찾아줘
```

그 다음 변호사가 직접 해야 하는 일:

- 계약서 조항을 하나씩 읽음
- 어떤 조항이 제26조 이슈인지 판단
- 국외 이전 조항이 제28조의8 체크 항목을 채우는지 판단
- 제3자 제공 risk인지 처리위탁인지 분류
- 고객에게 보낼 메모 형식으로 다시 씀
- 수정 요청 문구를 별도로 만듦

### claude-for-legal-kr까지 붙였을 때

변호사는 이렇게 요청함.

```text
/privacy-legal:kr-pipa-dpa-review vendor-dpa.pdf
```

기대 산출물:

```text
Verdict: conditional

Required gaps:
- 국외 이전 수령자, 국가, 이전 항목, 보유기간, 보호조치가 불명확함
- AI training 목적이 처리위탁 범위를 넘을 수 있음
- subprocessor 사전 통지 또는 승인 구조가 없음
- breach notification이 내부 조사 완료 후로 되어 있어 한국 고객 대응에 늦을 수 있음

Recommended improvements:
- Korea PIPA addendum 추가
- 재위탁자 목록 별첨화
- 삭제 확인서 및 backup retention carveout 구체화

Source status:
- 제26조: verified_source
- 제28조의8: verified_source
- 제29조: verified_source
- 제34조: verified_source

Review gate:
- requires_professional_review
```

차이는 단순함. MCP는 조문을 찾고, `claude-for-legal-kr`은 그 조문을
검토 업무의 체크리스트, 판단 구조, 메모 형식으로 변환함.

## 기능별로 보면 무엇이 추가되나

### 1. 업무별 playbook

법제처 MCP에는 "DPA를 볼 때 어떤 순서로 봐야 하는가"가 없음.
`claude-for-legal-kr`에는 skill별 playbook이 있음.

PIPA/DPA review 기준:

- 처리위탁 목적과 범위
- 재위탁/subprocessor
- 국외 이전
- 안전성 확보조치
- breach notification
- 삭제/반환
- AI training / analytics / service improvement
- privacy policy consistency

### 2. 쟁점의 중요도 분리

실무에서 중요한 건 모든 issue를 다 나열하는 게 아니라, 지금 막는
것과 나중에 고치면 되는 것을 분리하는 것임.

`claude-for-legal-kr`은 산출물을 다음처럼 나눔.

- `required gaps`: 서명/진행 전 고쳐야 하는 항목
- `recommended improvements`: 협상력이나 문서 품질을 높이는 항목
- `source status`: 근거가 실제 조회됐는지
- `review gate`: 변호사/책임자 검토 없이는 외부 사용 금지

### 3. source-backed 판단

법제처 MCP만 쓰면 출처는 찾을 수 있지만, 메모 작성 과정에서 어떤
문장이 조회된 근거인지, 모델 추론인지 섞이기 쉬움.

`claude-for-legal-kr`은 다음 라벨을 강제함.

- `verified_source`: 현재 workflow에서 조회한 근거
- `user_supplied_unverified`: 사용자가 준 자료이나 공식 조회는 안 됨
- `model_inference`: 모델 추론이므로 확인 필요
- `requires_professional_review`: 외부 사용 전 전문가 검토 필요

### 4. 반복 가능한 산출물

변호사가 바쁜 이유는 법을 몰라서가 아니라, 비슷한 검토를 매번 다시
조립해야 해서임.

`claude-for-legal-kr`은 반복 산출물을 표준화함.

- 계약 검토 메모
- gap table
- red flag list
- 수정 요청안
- 내부 보고용 bottom line
- client/vendor에게 물어볼 follow-up question

### 5. junior reviewer 역할

법제처 MCP는 "검색 잘하는 도구"에 가까움.
`claude-for-legal-kr`은 "초벌 검토를 하는 junior reviewer"에 가까움.

단, 최종 판단은 하지 않음. 최종 의견, 서명, 발송, 제출은 항상 변호사
또는 책임자가 검토해야 함.

## 변호사 입장에서 체감되는 차이

### Before

```text
1. 계약서 읽기
2. 관련 조문 검색
3. 판례 검색
4. 조항별 issue spotting
5. 중요도 분류
6. 메모 작성
7. 수정 요청안 작성
8. 출처 확인
```

### After

```text
1. 계약서 넣기
2. claude-for-legal-kr이 issue spotting 초안 생성
3. 법제처 MCP source status 확인
4. 변호사가 판단과 문구를 검토
5. 메모/수정 요청안 확정
```

시간이 줄어드는 부분은 "법률 판단 자체"가 아니라, 반복적인 구조화,
누락 체크, 초안 작성, 쟁점 분류임.

## 데모 시나리오

### 데모 1: 법제처 MCP만 사용

질문:

```text
개인정보 보호법 제26조와 제28조의8을 찾아줘.
```

보여줄 것:

- 법령 검색 결과
- 조문 조회
- MST / 법령ID

메시지:

```text
여기까지는 공식 출처 검색입니다. 매우 중요하지만, 검토 업무 전체는
아직 변호사가 직접 조립해야 합니다.
```

### 데모 2: claude-for-legal-kr 사용

질문:

```text
/privacy-legal:kr-pipa-dpa-review sample_vendor_dpa.md
```

보여줄 것:

- verdict
- required gaps
- recommended improvements
- source status
- review gate

메시지:

```text
여기서는 같은 법령 조회를 하되, 계약서 검토 업무의 결과물까지
초안화합니다. 변호사는 검색자가 아니라 reviewer로 들어오게 됩니다.
```

## 이 제품이 잘 맞는 변호사

- 법제처 MCP나 AI 검색을 이미 쓰고 있음
- 계약서, DPA, 약관, 규제 검토를 반복적으로 함
- junior가 정리한 issue list를 검토하는 방식에 익숙함
- 법령 원문보다 "그래서 이 계약서 어디가 문제인가"가 더 필요함
- 내부 보고용 메모, client memo, vendor redline 요청을 자주 씀

## 맞지 않는 경우

- 단순 법령 검색만 필요함
- 산출물 표준화가 필요 없음
- 매번 완전히 다른 쟁점의 고난도 법률의견만 작성함
- AI가 만든 초안을 검토할 시간이 전혀 없음
- source status나 review gate 없이 바로 외부 발송 가능한 답을 원함

## 제안 문구

```text
지금 쓰는 법제처 MCP는 그대로 두시면 됩니다.
제가 붙이려는 건 그 위의 workflow layer입니다.

법령을 찾는 도구가 아니라, 법령을 근거로 계약서/DPA를 검토해서
required gap, recommended improvement, source status, review gate가 있는
초안 메모를 만드는 구조입니다.

변호사 판단을 대체하려는 게 아니라, 변호사가 검토할 초벌 issue list와
메모를 더 빨리 만드는 쪽입니다.

한 번만 테스트해보시죠. 같은 DPA를 두고
1. 법제처 MCP만 썼을 때
2. claude-for-legal-kr workflow까지 붙였을 때
결과물이 어떻게 다른지 비교하면 차이가 바로 보일 겁니다.
```

## 한 문장 포지셔닝

`claude-for-legal-kr`은 법제처 MCP를 대체하는 검색기가 아니라, 법제처
MCP를 근거 엔진으로 사용해 변호사의 반복 검토 업무를 메모와 gap table로
초안화하는 legal workflow layer임.

