TO INSTALL THE FRAMEWORK
pip install -r requirements.txt

TO CONFIGURE THE DELPHES APP (Projet des préfectures)
- Edit .\apps\delphes\runtime\configuration_delphes.xlsx

TO RUN THE DELPHES APP

To run the ODM decision service:
cd .\apps\delphes\runtime\odm_databases\9.0\
docker run -e LICENSE=accept -m 2048M --memory-reservation 2048M -p 9060:9060 -p 9443:9443 -v .:/config/dbdata/ -e SAMPLE=false icr.io/cpopen/odm-k8s/odm:9.0

To use the backend FastAPI server
- In frontend\src\streamlit_main.py, switch:
        # self.api_client: ApiClient = ApiClientHttp()
        self.api_client: ApiClient = ApiClientDirect()
- Type from the home directory:
fastapi dev .\launcher_fastapi.py --port 8002

To launch the test UI
streamlit run .\launcher_streamlit.py


