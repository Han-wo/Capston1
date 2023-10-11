# 캡스톤디자인 3주차

## 로그인 및 회원가입 구현

이번 주차에는 Firebase Realtime Database를 사용하여 로그인 및 회원가입 기능을 구현하였습니다.또한, Python Flask 웹 애플리케이션 프레임워크를 사용하여 서버를 개발하였습니다.

### 주요 구현 내용

- Firebase Realtime Database를 사용한 회원가입 및 로그인 기능 구현
- 이메일 형식과 비밀번호 형식 유효성 검사 기능 추가
- 중복된 이메일로 회원가입을 시도할 경우 가입 불가능하도록 구현
- CSS를 사용하여 인프런 사이트를 모티브로한 네비게이션 바 구현

### 사용 기술 및 도구

- Python Flask 웹 애플리케이션 프레임워크
- Firebase Realtime Database
- HTML/CSS/JavaScript

구현 예시 

![https://user-images.githubusercontent.com/99471821/229353805-6768608d-de05-414e-940a-f7feb2d21ba1.png](https://user-images.githubusercontent.com/99471821/229353805-6768608d-de05-414e-940a-f7feb2d21ba1.png)

### 참고 문서 및 자료

- Firebase Documentation: [https://firebase.google.com/docs](https://firebase.google.com/docs)
- Flask Documentation: [https://flask.palletsprojects.com/en/2.1.x/](https://flask.palletsprojects.com/en/2.1.x/)
- Bootstrap Documentation: [https://getbootstrap.com/docs/5.1/getting-started/introduction/](https://getbootstrap.com/docs/5.1/getting-started/introduction/)

### 코드

- 코드는 GitHub에서 확인하실 수 있습니다.
    
    https://github.com/Han-wo/Capston1



# 캡스톤 9주차 진행사항

## 기능 개요
- 로그인 및 회원가입에 전화번호 유효성검사추가
    ![image](https://user-images.githubusercontent.com/99471821/236740245-67e041bc-f23e-47b3-9e24-1051f2cd38ec.png)
    
- 실시간 스트리밍 화면 구현
    - 현재 웹캠으로 구현, 추후 라즈베리파이 카메라로 연결할 예정
    ![Untitled (3)](https://user-images.githubusercontent.com/99471821/236741096-1608a0c0-e672-4bfa-af3f-fb9434e1346f.png)
        - 이 얼굴이 학습된 얼굴이면 등록됨 아니면 미등록 으로 기록하는 출입로그를 작성할것입니다
    
- 출입 로그 데이터베이스 전송 및 받아오기 구현
    - 받아오는 것은 가능하지만 출력이 제대로 되지 않아 수정이 필요함 현재는 출력은 더미데이터를 이용하고 있습니다
     ###  구현 현황
     
     -  출입로그가 없을시
        ![Untitled (2)](https://user-images.githubusercontent.com/99471821/236741025-33a0f5b5-60ea-46be-aeec-a37331cf8db9.png)
     - 더미데이터
        ![Untitled (1)](https://user-images.githubusercontent.com/99471821/236740963-5f197c5e-57cb-4031-bd15-c810a97d9546.png)
     - DB에 기록
        ![Untitled](https://user-images.githubusercontent.com/99471821/236740801-d4b52952-07cd-41da-a7ea-ea2d044e5ec9.png)

    
- 로그인 시 출입 로그를 보여주는 페이지로 이동 구현
    
- 로그인 시 로그인 세션 유지 후 로그아웃 기능 구현
    ![image](https://user-images.githubusercontent.com/99471821/236741325-b32f251e-2adc-457f-9005-8a511d1aac51.png)


## 기술 스택
- Front-end: HTML, CSS, JavaScript
- Back-end: Flask
- Database: Firebase 


# 9주차 문제점
1. 라즈베리파이 모듈과 개인 피씨간의 ip주소로의 연결시 컨스턴트 오류가 계속 떴었음
2. 라즈베리파이카메라 모듈은 피씨가 인식을 못함
3. 비밀번호 저장시 원 번호로 저장되어 보안성 취약

##고친점
1. 라즈베리 파이와의 ip모듈 연결이 안 됐었는데 소켓으로 서버와 클라이언트를 분리하여 라즈베리 파이와 노트북 연결 완료
2. 소켓주소인 서버 주소와 클라이언트 주소가 충돌하였으나 개인ip 주소로 갖고오니까 해결완료
3. 라즈베리파이 보드에 클라이언트 컴퓨터 주소가 띄워짐 
라즈베리 파이 보드와의 연결 문제는 해결 완료
4. 비밀번호를 해시데이터로 저장하고 저장된 해시데이터를 다시 불러오는 코드추가로 보안성 해결 완료




# 캡스톤 10주차 진행사항

## 구현 완료

1. 로그인 및 회원가입 세션에 보안성을 위해 비밀번호는 해시 데이터로 저장
    - 로그인 시, 저장된 해시 데이터 비밀번호를 변경하여 불러오기
    - 전화번호도 가능하다면 해시 데이터로 저장할 예정
2. 출입로그 출력 불가능했던 오류 수정 완료
3. 라즈베리파이 카메라 모듈 얼굴인식 출력 성공 (웹사이트에 구현은 아직)
4. 좌측에는 실시간 스트리밍, 우측에는 출입로그 표시하는 메인 페이지 구현 완료
5. 로그인 시 메인 페이지로 이동하는 기능 구현
    - 웹사이트 좌측에는 실시간 스트리밍 화면, 우측에는 출입로그 일부(더보기를 클릭하면 출입로그 상세페이지로 이동)

## 수정할 점

1. 메인 페이지 CSS 디자인 구현
2. 전화번호 해시 데이터 저장 및 로드 구현
3. 라즈베리 파이 카메라 모듈을 IP로 연결하여 웹사이트에 출력
4. 출입로그 상세 페이지에서 출입로그 표현을 페이지네이션을 사용하여 한 페이지에 최대 10개 출력한 후, 나머지는 다음 페이지로 이동
5. 메인 페이지 출입로그 미리보는 테이블도 최대 5~7개 보여지는 코드 추가 구현
6.소켓연결로 연결해서 다른페이지로 넘어갔다가 메인페이지로 돌아오면 라즈베리파이카메라와 연결이 끊김
