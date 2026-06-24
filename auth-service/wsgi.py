import os
import threading

from app import create_app
from grpc_server import serve

app = create_app()


# gRPC 도 Flask 와 함께 실행시키기
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    # daemon=True - Flask 프로세스가 종료될 때 gRPC 스레드도 같이 종료
    grpc_thread = threading.Thread(target=serve, daemon=True)
    grpc_thread.start()
