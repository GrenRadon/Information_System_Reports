#importing all required libraries
from pexpect import pxssh
from telethon.tl.types import InputPeerUser
from telethon import TelegramClient, sync, events
import time
import pymysql
import subprocess
import sys
import os
import webview
import PyQt5  # Para la biblioteca QT
import gi  # Para la biblioteca GTK
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
import subprocess
import platform
import threading
import requests


# Bandera para indicar si se debe detener la ejecución de los hilos
stop_threads = False


def menu():
    print("\n<[Menú de opciones]>\n")
    print("1. Establecer conexión SSH con los 2 equipos")
    print("2. Obtener información concerniente a  CPU, RAM, Uso de disco, IP, Hostname de cada equipo constantemente y enviar a la base de datos")
    print("3. Envío notificaciones a telegram por medio de colas")
    print("4. Simulación de envío notificaciones a telegram por medio de colas una vez que algún indicador supera el 75% de su capacidad la cual se actualiza cada 5 segundos")
    print("5. Servicio web usando el método POST y flask")
    print("6. Salir")

def establecerConexion():
    s = pxssh.pxssh()
    print("\t\t\n\n_[Ajustando paramentros del ordenador numero 1...]_\n")
    print("Ordenador personal n1...")
    #Preferiblemente usar el 2222 para la primera computadora
    puerto1 = input("Por favor, indique el puerto a utilizar: ")
    #Preferiblemente usar el hostname: personal-computer1
    hostname1 = input("Por favor, inserte el hostname del primer ordenador: ")
    #preferiblemente usar la contraseña: bambamll214A2?
    password1 = input("Por favor, inserte la contraseña de usuario del primer ordenador: ")


    if not s.login ('127.0.0.1 -p '+puerto1, hostname1, password1):
        print ("SSH session failed on login with PC1.")
        print(str(s))

    else:
        print ("SSH session login successful with PC1")

    p = pxssh.pxssh()

    print("\t\t\n\n_[Ajustando paramentros del ordenador numero 2...]_\n")
    print("Ordenador personal n2...")
    #Preferiblemente usar el 3022 para la primera computadora
    puerto2 = input("Por favor, indique el puerto a utilizar: ")
    #Preferiblemente usar el hostname: pc2
    hostname2 = input("Por favor, inserte el hostname del segundo ordenador: ")
    #preferiblemente usar la contraseña: bambamll214A2?
    password2 = input("Por favor, inserte la contraseña de usuario del segundo ordenador: ")

    if not p.login ('127.0.0.1 -p '+puerto2, hostname2, password2):
        print ("\nSSH session failed on login with PC2.")
        print(str(s))

    else:
        print ("\nSSH session login successful with PC2")

    return s, p

def ddlDatabaseCreation():

    connection = pymysql.connect(
        host='localhost',
        user='casa',
        password='contraseña',
    )

    # Ejecutar el script DDL
    ddl_script = '''
    CREATE DATABASE IF NOT EXISTS guests_db;
    '''

    table_script = '''
    CREATE TABLE IF NOT EXISTS guests_db.guest_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        hostname VARCHAR(255),
        ip VARCHAR(15),
        diskusage FLOAT,
        ramusage FLOAT,
        cpuusage FLOAT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''

    try:
        with connection.cursor() as cursor:
            # Crear la base de datos
            cursor.execute(ddl_script)

            # Seleccionar la base de datos
            cursor.execute("USE guests_db")

            # Crear la tabla
            cursor.execute(table_script)

        # Confirmar los cambios en la base de datos
        connection.commit()

        print("Estructura de la base de datos creada correctamente.")
    except Exception as e:
        print("Error al crear la estructura de la base de datos:", str(e))
    finally:
        # Cerrar la conexión a la base de datos
        connection.close()



def updateinfoDatabase(hostname,ip,ramUsage,Cpu,diskUsage,hostname2,ip2,ramUsage2,Cpu2,diskUsage2):

    #Limpiando la data de caracteres no necesarios
    a = hostname.replace('%','')
    b = ip.replace('%','')
    c = ramUsage.replace('%','')
    d = Cpu.replace('%','')
    e = diskUsage.replace('%','')

    a1 = hostname2.replace('%','')
    b1 = ip2.replace('%','')
    c1 = ramUsage2.replace('%','')
    d1 = Cpu2.replace('%','')
    e1 = diskUsage2.replace('%','')

    # Establecer la conexión a la base de datos
    connection = pymysql.connect(
        host='localhost',
        user='casa',
        password='bambamll214A2?',
        database='guests_db'
    )

    # Actualizar la información de los guests

    guest1 = {
        'hostname': a,
        'ip': b,
        'diskusage': e,
        'ramusage': c,
        'cpuusage': d
    }

    guest2  = {
        'hostname': a1,
        'ip': b1,
        'diskusage': e1,
        'ramusage': c1,
        'cpuusage': d1
    }

    try:
        with connection.cursor() as cursor:
            # Insertar información del guest 1
            sql = "INSERT INTO guest_info (hostname, ip, diskusage, ramusage, cpuusage) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (
                guest1["hostname"],
                guest1["ip"],
                guest1["diskusage"],
                guest1["ramusage"],
                guest1["cpuusage"]
            ))

            # Insertar información del guest 2
            cursor.execute(sql, (
                guest2["hostname"],
                guest2["ip"],
                guest2["diskusage"],
                guest2["ramusage"],
                guest2["cpuusage"]
            ))

        # Confirmar los cambios en la base de datos
        connection.commit()

        print("Información de los invitados insertada correctamente.")
    except Exception as e:
        print("Error al insertar la información de los invitados:", str(e))
    finally:
        # Cerrar la conexión a la base de datos
        connection.close()

def expressNotifications(queueHost1, queueHost2, mensajeEntrada):

        # get your api_id, api_hash, token
        # from telegram as described above
        api_id = API_ID
        api_hash = 'APIHASH'
        token = 'TOKEN_BOTFATHER'
        mensaje0 = mensajeEntrada
        message = mensaje0 + 'Host1: '+queueHost1[0]+' ip: ' \
                                          ''+queueHost1[1]+' ' \
                                        'ramUsage: '+queueHost1[2]+' ' \
                                        'CpuUsage: '+queueHost1[3]+' ' \
                                        'DiskUsage: '+queueHost1[4]+'\n' \
                                        'Host2: '+queueHost2[0]+' ' \
                                        'ip: '+queueHost2[1]+' ' \
                                        'ramUsage: '+queueHost2[2]+' ' \
                                        'CpuUsage: '+queueHost2[3]+' ' \
                                        'DiskUsage: '+queueHost2[4]


        # your phone number
        phone = '+57...'

        # creating a telegram session and assigning
        # it to a variable client
        client = TelegramClient('session', api_id, api_hash)

        # connecting and building the session
        client.connect()

        # in case of script ran first time it will
        # ask either to input token or otp sent to
        # number or sent or your telegram id
        if not client.is_user_authorized():

            client.send_code_request(phone)

            # signing in the client
            client.sign_in(phone, input('Enter the code: '))


        try:
            #this user_id is got it by commenting with @username_to_id_bot in telegram
            #aquí debe ir el user_id de la persona a la cual se le va a enviar los mensajes
            user_id = USER_ID
            access_hash = client.get_input_entity(user_id)
            # receiver user_id and access_hash, use
            # my user_id and access_hash for reference
            receiver = InputPeerUser(user_id, access_hash).access_hash

            # sending message using telegram client
            client.send_message(receiver, message, parse_mode='html')
        except Exception as e:

            # there may be many error coming in while like peer
            # error, wrong access_hash, flood_error, etc
            print(e);

        # disconnecting the telegram session
        client.disconnect()

def telegramNotifications(s, p, pauta):

    if (pauta == 1):

        queueHost1 = []
        queueHost2 = []

        a,b = gettingInfo(s,p,2)

        #Llenando las colas
        for i in range(len(a)):
            queueHost1.append(a[i])
        for i in range(len(b)):
            queueHost2.append(b[i])

        expressNotifications(queueHost1,queueHost2,'')

        for i in range(len(a)):
            queueHost1.pop(0)
        for i in range(len(b)):
            queueHost2.pop(0)

    else:
        counter = 200
        while(True):
            queueHost1 = []
            queueHost2 = []

            a,b = gettingInfo(s,p,2)

            #Llenando las colas

            for i in range(len(a)):
                queueHost1.append(a[i])
            for i in range(len(b)):
                queueHost2.append(b[i])


            #Notificaciones para host1
            #[hostname,ip, ramUsage, Cpu, diskUsage]
            if(float(queueHost1[2].replace('%','')) > 75):
                mensaje = 'Host1, ha superado el límite recomendable de uso de RAM\n\n'
                expressNotifications(queueHost1,queueHost2, mensaje)
                break;
            elif(float(queueHost1[3].replace('%','')) > 75):
                mensaje = 'Host1, ha superado el límite recomendable de uso de CPU\n\n'
                expressNotifications(queueHost1,queueHost2, mensaje)
                break;
            elif(float(queueHost1[4].replace('%','')) > 75):
                mensaje = 'Host1, ha superado el límite recomendable de uso de Disco\n\n'
                expressNotifications(queueHost1,queueHost2, mensaje)
                break;
            else:
                pass

            #Notificaciones para host2
            #[hostname,ip, ramUsage, Cpu, diskUsage]
            if(float(queueHost2[2].replace('%','')) > 75):
                mensaje = 'Host2, ha superado el límite recomendable de uso de RAM\n\n'
                expressNotifications(queueHost1,queueHost2, mensaje)
                break;
            elif(float(queueHost2[3].replace('%','')) > 75):
                mensaje = 'Host2, ha superado el límite recomendable de uso de CPU\n\n'
                expressNotifications(queueHost1,queueHost2, mensaje)
                break;
            elif(float(queueHost2[4].replace('%','')) > 75):
                mensaje = 'Host2, ha superado el límite recomendable de uso de Disco\n\n'
                expressNotifications(queueHost1,queueHost2, mensaje)
                break;
            else:
                pass

            #Vaciando colas FIFO
            for i in range(len(a)):
                queueHost1.pop(0)
            for i in range(len(b)):
                queueHost2.pop(0)

            counter = counter-1
            if(counter == 0):
                opt = input("¿Desea continuar con el modo escucha?[S/N]: ")
                if (opt == 'N'):
                    break;
                else:
                    counter = 200

            else:
                pass


def gettingInfo(s,p,decision):

        if (decision == 1):
            #Aquí empezamos a capturar la información
            s.sendline ('curl -4 icanhazip.com')
            s.prompt()
            ip = s.before.split()[-1].decode('UTF-8')

            s.sendline ('hostname')
            s.prompt()
            hostname = s.before.split()[-1].decode('UTF-8')

            s.sendline ('./ram.sh')
            s.prompt()
            ramUsage = s.before.split()[-1].decode('UTF-8')


            s.sendline('./cpu.sh')
            s.prompt()
            Cpu = s.before.split()[-1].decode('UTF-8')

            s.sendline('./disk_usage.sh')
            s.prompt()
            diskUsage = s.before.split()[-1].decode('UTF-8')

            #s.logout()

            print("\n\nListening...\n")
            print("Hostname: "+str(hostname)+", "+"IP: "+str(ip)+", "+"RamUsage: "+str(ramUsage)+", "+"Cpu: "+str(Cpu)+"%, "+"DiskUsage: "+str(diskUsage))

            #Aquí empezamos a capturar la información
            p.sendline ('curl -4 icanhazip.com')
            p.prompt()
            ip2 = p.before.split()[-1].decode('UTF-8')

            p.sendline ('hostname')
            p.prompt()
            hostname2 = p.before.split()[-1].decode('UTF-8')

            p.sendline ('./ram.sh')
            p.prompt()
            ramUsage2 = p.before.split()[-1].decode('UTF-8')


            p.sendline('./cpu.sh')
            p.prompt()
            Cpu2 = p.before.split()[-1].decode('UTF-8')

            p.sendline('./disk_usage.sh')
            p.prompt()
            diskUsage2 = p.before.split()[-1].decode('UTF-8')

            print("Hostname: "+str(hostname2)+", "+"IP: "+str(ip2)+", "+"RamUsage: "+str(ramUsage2)+", "+"Cpu: "+str(Cpu2)+"%, "+"DiskUsage: "+str(diskUsage2)+"\n\n")

            #Sección de inserción en la base de datos
            #CREATE USER 'casa'@'localhost' IDENTIFIED BY 'bambamll214A2?';
            #guests_db


            ddlDatabaseCreation()
            updateinfoDatabase(hostname,ip,ramUsage,Cpu,diskUsage,hostname2,ip2,ramUsage2,diskUsage2,Cpu2)

        else:
            #Aquí empezamos a capturar la información
            s.sendline ('curl -4 icanhazip.com')
            s.prompt()
            ip = s.before.split()[-1].decode('UTF-8')

            s.sendline ('hostname')
            s.prompt()
            hostname = s.before.split()[-1].decode('UTF-8')

            s.sendline ('./ram.sh')
            s.prompt()
            ramUsage = s.before.split()[-1].decode('UTF-8')


            s.sendline('./cpu.sh')
            s.prompt()
            Cpu = s.before.split()[-1].decode('UTF-8')

            s.sendline('./disk_usage.sh')
            s.prompt()
            diskUsage = s.before.split()[-1].decode('UTF-8')

            #Aquí empezamos a capturar la información
            p.sendline ('curl -4 icanhazip.com')
            p.prompt()
            ip2 = p.before.split()[-1].decode('UTF-8')

            p.sendline ('hostname')
            p.prompt()
            hostname2 = p.before.split()[-1].decode('UTF-8')

            p.sendline ('./ram.sh')
            p.prompt()
            ramUsage2 = p.before.split()[-1].decode('UTF-8')


            p.sendline('./cpu.sh')
            p.prompt()
            Cpu2 = p.before.split()[-1].decode('UTF-8')

            p.sendline('./disk_usage.sh')
            p.prompt()
            diskUsage2 = p.before.split()[-1].decode('UTF-8')

            updateinfoDatabase(hostname,ip,ramUsage,Cpu,diskUsage,hostname2,ip2,ramUsage2,diskUsage2,Cpu2)

            return [hostname,ip, ramUsage, Cpu, diskUsage], [hostname2,ip2,ramUsage2,Cpu2,diskUsage2]

def delete_all_records():

    try:
        # Establecer la conexión a la base de datos
        connection = pymysql.connect(
            host='localhost',
            user='casa',
            password='contraseña',
            database='guests_db'
        )

        try:
            with connection.cursor() as cursor:
                # Borrar todos los registros de la tabla guest_info
                cursor.execute("DELETE FROM guest_info")

            # Confirmar los cambios en la base de datos
            connection.commit()

            print("Registros eliminados correctamente.")

        except Exception as e:
            print("Error al eliminar los registros:", str(e))

        finally:
            # Cerrar la conexión a la base de datos
            connection.close()
    except:
        print("\nNo hay registro alguno de la base de datos...\n\n")

def drop_database():

    try:
        # Establecer la conexión a la base de datos
        connection = pymysql.connect(
            host='localhost',
            user='casa',
            password='contraseña',
            database='guests_db'
        )

        try:
            with connection.cursor() as cursor:
                # Eliminar la base de datos guests_db
                cursor.execute("DROP DATABASE IF EXISTS guests_db")

            #Confirmar los cambios en la base de datos
            connection.commit()

            print("Base de datos eliminada correctamente.")

        except Exception as e:
            print("Error al eliminar la base de datos:", str(e))

        finally:
            # Cerrar la conexión a la base de datos
            connection.close()

    except:
        print("\nNo hay base de datos alguna creada...\n\n")

def run_flask_app(port):
    python_executable = sys.executable
    script_path = os.path.join(os.getcwd(), 'app.py')

    if sys.platform == 'win32':
        # Ejecutar en Windows
        subprocess.Popen([python_executable, script_path, '--port', str(port)], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        # Ejecutar en Linux
        subprocess.Popen([python_executable, script_path, '--port', str(port)])




def main():

    # Crear el objeto Event para sincronizar los hilos
    event = threading.Event()
    while(True):
        menu()
        seleccion = int(input("Seleccione su opción>> "))
        if(seleccion == 1):
           s,p = establecerConexion()
        if(seleccion == 2):
            gettingInfo(s,p,1)
        if(seleccion == 3):
            gettingInfo(s,p,2)
            telegramNotifications(s, p, 1)
        if(seleccion == 4):
            telegramNotifications(s, p, 2)
        if(seleccion == 5):

            # Detener cualquier proceso de Flask existente antes de iniciar uno nuevo
            # Realiza una solicitud HTTP para detener el servidor de Flask

            global stop_threads  # Acceder a la variable de control global

            # Iniciar el hilo para ejecutar la aplicación Flask

            telegram_thread = threading.Thread(target=telegramNotifications, args=(s, p, 2))
            telegram_thread.start()

            flask_thread = threading.Thread(target=run_flask_app, args=(5001,))
            flask_thread.start()

            # Agregar un retraso de 1 segundo para permitir que la aplicación Flask se inicie completamente
            time.sleep(1)

            # Iniciar el hilo para las notificaciones de Telegram

            webview.create_window("Guest Information", "http://localhost:5000")
            webview.start()

            time.sleep(200)
            stop_threads = True
            flask_thread.join()
            telegram_thread.join()
            # Esperar a que se cierre la ventana del navegador
            #webview.destroy_window()

        if(seleccion == 6):
            try:
                delete_all_records()
                drop_database()
                s.logout()
                p.logout()
                # Detener cualquier proceso de Flask existente antes de iniciar uno nuevo
                # Realiza una solicitud HTTP para detener el servidor de Flask
                response = requests.post('http://localhost:5001/shutdown')
                break;
            except NameError as error:
                print("No se ha iniciado la primera conexión")
                break;


if __name__ == "__main__":
    main()
