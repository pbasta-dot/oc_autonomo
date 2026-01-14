import json
import os
import hashlib
import getpass

USERS_FILE = "users.json"

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _load_users():
    if not os.path.exists(USERS_FILE):
        raise FileNotFoundError(f"No existe {USERS_FILE} en la carpeta del sistema.")
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_admin_password():
    """
    Si el admin tiene password_hash vacío, pide crear una clave y la guarda.
    """
    data = _load_users()
    users = data.get("users", [])

    for u in users:
        if u.get("username") == "admin" and not u.get("password_hash"):
            print("Primera ejecución: debes crear clave para 'admin'.")
            while True:
                p1 = getpass.getpass("Nueva clave admin: ")
                p2 = getpass.getpass("Repite clave: ")

                if len(p1) < 6:
                    print("La clave debe tener al menos 6 caracteres.")
                    continue
                if p1 != p2:
                    print("No coinciden. Intenta de nuevo.")
                    continue

                u["password_hash"] = _sha256(p1)
                _save_users(data)
                print("✅ Clave admin creada.\n")
                return

def login() -> str:
    data = _load_users()
    users = data.get("users", [])

    for intento in range(1, 4):
        print("=== LOGIN ===")
        username = input("Usuario: ").strip()
        password = getpass.getpass("Clave: ")

        h = _sha256(password)
        ok = any(
            u.get("username") == username and u.get("password_hash") == h
            for u in users
        )

        if ok:
            print("✅ Acceso correcto.\n")
            return username

        print(f"❌ Usuario o clave incorrectos (intento {intento}/3).\n")

    raise SystemExit("Acceso denegado (3 intentos).")
