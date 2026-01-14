from config import APP_NOMBRE
from oc.auth import ensure_admin_password, login
from oc.menu import menu_principal

def main():
    print(f"\n{APP_NOMBRE}\n")
    ensure_admin_password()
    usuario = login()
    menu_principal(usuario)

if __name__ == "__main__":
    main()