---
name: labview-automation
description: NI LabVIEW 2025 자동화 가이드. LabVIEW 실행 상태 확인, VI(.vi) 실행, 컨트롤/인디케이터 제어, 프론트 패널 캡처 및 CLI 배치 실행을 지원합니다.
---

# LabVIEW Automation Skill

이 스킬은 Antigravity 에이전트가 로컬 Windows 환경에 설치된 NI LabVIEW 2025를 제어하고 자동화할 때 사용하는 표준 지침입니다.

## 1. 시스템 환경 정보

- **LabVIEW 실행 파일**: `C:\Program Files (x86)\National Instruments\LabVIEW 2025\LabVIEW.exe`
- **LabVIEW CLI**: `C:\Program Files (x86)\National Instruments\Shared\LabVIEW CLI\LabVIEWCLI.exe`
- **COM ProgID**: `LabVIEW.Application`
- **파이썬 자동화 모듈**: `src/automation/labview_client.py` (`.venv` 환경)

---

## 2. 기본 작업 절차

### 1) LabVIEW 상태 점검
작업을 시작하기 전 항상 LabVIEW 프로세스 실행 여부를 확인합니다.
```powershell
.\.venv\Scripts\python.exe src/automation/labview_client.py --status
```

### 2) Python COM 클라이언트를 통한 VI 실행 및 데이터 입출력
`src/automation/labview_client.py`의 `LabVIEWClient` 클래스를 사용합니다:

```python
from src.automation.labview_client import LabVIEWClient

client = LabVIEWClient()
client.connect()

# VI 실행 및 입력값 주입 / 출력값 읽기
result = client.run_vi(
    vi_path="path/to/target.vi",
    inputs={"Frequency": 1000.0, "Amplitude": 5.0},
    output_indicators=["ResultArray", "MeasuredVoltage"],
    show_front_panel=True,
)
print(result)
```

### 3) LabVIEW CLI를 통한 헤드리스 실행
UI 없이 빠른 배치 빌드나 실행이 필요할 때:
```powershell
& "C:\Program Files (x86)\National Instruments\Shared\LabVIEW CLI\LabVIEWCLI.exe" -OperationName RunVI -LabVIEWPath "C:\Program Files (x86)\National Instruments\LabVIEW 2025\LabVIEW.exe" -VIPath "D:\path\to\target.vi"
```

---

## 3. 에이전트 주의사항

1. **타임아웃 설정**: 복잡한 계측이나 루프가 포함된 VI는 무한 루프에 빠질 수 있으므로 항상 타임아웃을 명시합니다.
2. **참조 해제**: COM 객체(`vi.Close()`, `client.close()`)를 작업 완료 후 반드시 해제하여 메모리 누수를 방지합니다.
3. **로그 기록**: 실행 결과와 이상 여부는 `logs/labview_automation.log`에 자동 기록됩니다.
