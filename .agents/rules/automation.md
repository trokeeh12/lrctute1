---
description: 외부 프로그램 연동 및 시스템 자동화 실행 시 준수해야 하는 안전 규칙
---

# Automation & Tool Safety Rules

1. **자동화 스크립트 실행 환경**:
   - 모든 자동화 파이썬 스크립트는 `.\.venv\Scripts\python.exe <script_path>`로 실행합니다.
   - 의존성 라이브러리가 필요한 경우 `.\.venv\Scripts\pip.exe install <package>`로 가상환경 내에 설치합니다.

2. **GUI 및 OS 제어 시 주의사항**:
   - 키보드/마우스 입력 자동화(PyAutoGUI, pywinauto 등)를 수행할 때는 예기치 않은 시스템 조작을 방지하기 위해 안전장치(Fail-Safe 옵션)를 기본 활성화합니다.
   - 윈도우 창 활성화 및 캡처 전, 해당 프로세스 존재 여부를 `Get-Process` 등으로 사전 확인합니다.

3. **리소스 정리**:
   - 실행된 외부 프로그램이나 브라우저 인스턴스는 작업 완료 후 적절히 종료(Graceful close)하여 좀비 프로세스가 남지 않도록 합니다.
