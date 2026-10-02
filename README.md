# VideoToPPT — Python 없는 Windows 배포판 만들기

이 프로젝트의 목표는 최종 사용자가 Python을 설치하지 않고 `VideoToPPT.exe`만 실행하는 것입니다.

## 가장 쉬운 빌드 방법: GitHub Actions

개발 PC에 Python이 없어도 됩니다.

### 1. GitHub 저장소 만들기

GitHub에서 빈 저장소를 하나 만듭니다.

예:
`VideoToPPT`

### 2. 이 프로젝트의 파일을 업로드

다음 구조를 그대로 올립니다.

```text
VideoToPPT/
├─ app.py
├─ converter.py
├─ requirements.txt
├─ README.md
└─ .github/
   └─ workflows/
      └─ build-windows.yml
```

### 3. GitHub에서 Actions 실행

저장소의:

`Actions → Build Windows EXE → Run workflow`

를 누릅니다.

GitHub의 Windows 빌드 머신에서 Python과 필요한 패키지를 설치하고 EXE를 만듭니다.

### 4. EXE 다운로드

빌드가 끝나면 workflow의 Artifacts에서:

`VideoToPPT-Windows.zip`

을 다운로드합니다.

압축을 풀면:

```text
VideoToPPT.exe
README.txt
```

가 있습니다.

사용자는 Python을 설치할 필요가 없습니다.

## 정식 Release 만들기

GitHub 저장소에 tag를 올리면 자동으로 Release를 만들도록 설정되어 있습니다.

예:

```bash
git tag v1.0.0
git push origin v1.0.0
```

그러면 GitHub Release에:

`VideoToPPT-Windows.zip`

이 자동으로 첨부됩니다.

## 로컬 Windows에서 직접 빌드하고 싶은 경우

이 경우에는 빌드 PC에만 Python이 필요합니다.

```bat
build-local-windows.bat
```

완성 파일:

```text
dist\VideoToPPT.exe
```

## 최종 사용자가 하는 일

최종 사용자는:

1. `VideoToPPT-Windows.zip` 다운로드
2. 압축 해제
3. `VideoToPPT.exe` 더블클릭
4. MP4 선택
5. 출력 폴더 선택
6. 변환 시작

만 하면 됩니다.

## 중요한 사항

이 방식은 PyInstaller로 Python 런타임과 필요한 Python 라이브러리를 EXE에 묶습니다.

따라서 최종 사용자 PC에는 Python이 필요하지 않습니다.

또한 Windows Defender/SmartScreen이 처음 받은 EXE에 경고를 표시할 수 있습니다. 개인 개발자가 서명하지 않은 새 EXE에서 흔히 발생하는 현상입니다. 실제 배포용이라면 코드 서명 인증서를 사용해 EXE에 서명하는 것을 권장합니다.

## 현재 프로그램의 출력

MP4를 처리하면:

```text
영상이름_slides/
├─ 영상이름_slides.pptx
├─ 영상이름_slides.pdf
├─ 영상이름_slides.csv
└─ images/
   ├─ slide_0001.png
   ├─ slide_0002.png
   └─ ...
```

PPTX는 영상에서 추출한 슬라이드 이미지를 16:9 PowerPoint에 넣습니다.

즉, PPT 내부 텍스트/도형을 개별 편집할 수 있는 완전한 원본 PPT 복원은 아닙니다.

## 다음 고도화

정확도를 더 높이려면 다음 기능을 추가할 수 있습니다.

- 발표자 얼굴/PiP 자동 제거
- 슬라이드 영역 자동 검출
- 마우스 커서 영향 제거
- OCR 기반 슬라이드 변화 검증
- 애니메이션 최종 프레임 선택
- 슬라이드 미리보기 및 수동 삭제
- 선택한 슬라이드만 PPT/PDF 생성
- 영상의 특정 구간만 분석
- 여러 MP4 일괄 변환
- 자동 업데이트
- 코드 서명된 Windows 설치 프로그램
