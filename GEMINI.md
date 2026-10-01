# Antigravity Agent Guidelines & Automation Rules

이 문서는 Antigravity IDE의 에이전트가 본 프로젝트(`lrctute1`)에서 코딩 및 외부 프로그램 자동화를 수행할 때 준수해야 하는 핵심 지침입니다.

---

## 1. 환경 및 런타임 표준 (Environment & Runtime)

- **운영체제(OS)**: Windows (기본 셸: PowerShell)
- **Python 환경**:
  - 가상환경 경로: `.venv`
  - Python 실행 파일: `.venv\Scripts\python.exe`
  - Pip 실행 파일: `.venv\Scripts\pip.exe`
  - 파이썬 관련 실행이나 패키지 설치 시 시스템 전역 Python이 아닌 반드시 가상환경 인터프리터를 사용합니다.
- **PowerShell 실행 정책**: `RemoteSigned` (CurrentUser) 설정 적용

---

## 2. 에이전트 코딩 원칙 (Agentic Coding Standards)

1. **테스트 및 검증 우선**:
   - 코드를 새로 작성하거나 수정한 후에는 반드시 터미널 명령을 통해 문법 검증 및 단위 테스트를 실행하여 정상 동작을 확인합니다.
2. **타입 힌팅 및 구조화**:
   - Python 코드에는 PEP 484 Type Hints를 적극 적용합니다.
   - 단일 파일에 비대하게 작성하기보다 기능별(core, automation, utils 등)로 모듈화합니다.
3. **보존성 유지**:
   - 기존 파일 수정 시 무관한 주석, 설정, 기존 인터페이스를 훼손하지 않습니다.

---

## 3. 외부 프로그램 자동화 수칙 (Automation Principles)

1. **프로세스 안전성 & 사전 검사**:
   - 외부 프로그램(브라우저, GUI 윈도우 앱, CLI 도구 등)을 제어하기 전, 대상 프로세스가 실행 중인지 먼저 확인합니다.
   - 불필요하게 동일한 인스턴스를 중복 실행하지 않도록 제어합니다.
2. **비동기 / 타임아웃 관리**:
   - 외부 프로그램은 예기치 않게 응답 대기 상태에 빠질 수 있으므로, 모든 자동화 호출에는 명시적인 **타임아웃(Timeout)**과 **재시도(Retry)** 로직을 구현합니다.
   - 장기 실행 프로세스는 백그라운드 태스크로 구동하고 주기적으로 상태를 모니터링합니다.
3. **로깅 및 결과 추적**:
   - 자동화 단계별 진행 상황, 성공/실패 여부를 `logs/` 디렉터리에 타임스탬프와 함께 기록합니다.

---

## 4. 권장 워크플로 (Recommended Workflows)

- **기획 및 검토**: 복합 작업 전 `/plan` 또는 상호 인터뷰(`/grill-me`)를 통해 요구사항 구체화
- **자율 작업**: 검증된 자동화 및 장시간 작업은 `/goal` 커맨드로 목표 지향적 자율 실행
- **지속화**: 재사용 가능한 자동화 절차는 `.agents/skills/`에 커스텀 스킬로 등록

---

## 5. LabVIEW 자동화 표준 (LabVIEW Automation)

- **설치 위치**: `C:\Program Files (x86)\National Instruments\LabVIEW 2025\LabVIEW.exe`
- **CLI 도구**: `C:\Program Files (x86)\National Instruments\Shared\LabVIEW CLI\LabVIEWCLI.exe`
- **제어 라이브러리**: `src/automation/labview_client.py` (ActiveX/COM 기반)
- **실행 전 수칙**:
  - `LabVIEWClient.is_process_running()`으로 현재 실행 상태 선제 점검
  - VI 실행 시 반드시 입력값과 반환받을 인디케이터 명칭을 지정하고 타임아웃을 설정
  - 모든 자동화 로그는 `logs/labview_automation.log`에 자동 기록됨

