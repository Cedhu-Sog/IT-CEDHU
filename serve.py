from waitress import serve
from inventario_tecnologico.wsgi import application
import socket

if __name__ == "__main__":
    # Detectar la IP local automáticamente
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print(f"Servidor corriendo en:")
    print(f" 👉 http://127.0.0.1:8080 (solo este PC)")
    print(f" 👉 http://192.168.1.16:8080 (desde tu red local 🚀)")

    serve(application, host="0.0.0.0", port=8080)
