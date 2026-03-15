## tomatoAgent_v3 

### 앞으로 할거
- codeArchive(ingest, archive 를 합친것)와 code_analize 처럼 서로 다른 graph들은 분리를 시키고 채팅 시작 시 사용자 선택에 graph가 지정되는 것으로 수정(supervisor의 판단으로는 x)
- 폴더 구조를 graphs/(graph1),(graph2).../(node),(state),(config)... 이런식으로 변경할것

### to-do
- nodes의 search_approval_node의 interrupt가 넘어가질 못해서 나오는 에러임. 이걸 고쳐야함


### 트러블 슈팅  
- langgraph의 대화내역 저장 로직문제(langgraph의 memorysaver를 사용못함)

- ag-ui 프로토콜의 활용(state나 config로 db나 minio를 넘겨야하는 문제)
    - copilotkit blog 게시글을 참조하여 커스텀 엔드포인트를 구성

- front의 copilotkit이 백엔드와 연결이 안됨
    - @ag-ui/client의 버전 문제로 CopilotRuntime 클래스의 agents를 제대로 읽지 못하는 오류였음(버전 변경으로 해결)


