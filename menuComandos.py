class colors: #clases de colores para usar
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[1;97m'

def menuComandos(): # se define la funcion menu para los comandos
    print("+-----------------------------MENU DE COMANDOS-----------------------+")
    print(f"{colors.OKBLUE}[+] Escoge una opción:" + '\n')
    print(f"{colors.OKBLUE}1) shell" + f"{colors.ENDC} : Obtener Una Shell")
    print(f"{colors.OKBLUE}2) info" + f"{colors.ENDC} : Obetener Informacion De La Maquina Victima")
    print(f"{colors.OKBLUE}3) shutdown" + f"{colors.ENDC} : Apagar maquina")
    print(f"{colors.OKBLUE}4) close" + f"{colors.ENDC} : Cerrar La Conexion")
    print(f"{colors.OKBLUE}5) screenshot" + f"{colors.ENDC} : Tomar Un Screenshot")
    print(f"{colors.OKBLUE}6) upload" + f"{colors.ENDC} : Subir Archivo A La Maquina Víctima")
    print(f"{colors.OKBLUE}7) download" + f"{colors.ENDC} : Descargar Archivos De La Víctima")
    print(f"{colors.OKBLUE}8) getlogs" + f"{colors.ENDC} : Obtener Registro Del Keylogger" )
    print(f"{colors.OKBLUE}9) stop" + f"{colors.ENDC} : Detener Keylogger" + '\n')
    print(f"{colors.FAIL}esc" + f"{colors.ENDC} : SALIR")
    print("__________________________" + '\n' + "> ", end = '')
    