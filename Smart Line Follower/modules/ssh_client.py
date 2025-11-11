# ============================================================================
# SSH_CLIENT.PY - Ejemplo de cliente SSH para Raspberry Pi
# ============================================================================

class SSHClient:
    """
    Cliente SSH para comunicación con Raspberry Pi
    Puede ejecutar comandos y recibir salida en tiempo real
    """
    
    def __init__(self, host, port=22, username="pi", password=None, key_file=None):
        """
        Args:
            host: Dirección IP o hostname
            port: Puerto SSH (default 22)
            username: Usuario SSH
            password: Contraseña (opcional si se usa key_file)
            key_file: Ruta a archivo de clave privada
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file
        self.client = None
        self.connected = False
        
    def connect(self):
        """Establece conexión SSH"""
        # TODO: Implementar con paramiko
        # import paramiko
        # self.client = paramiko.SSHClient()
        # self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 
        # if self.key_file:
        #     self.client.connect(
        #         self.host, 
        #         port=self.port,
        #         username=self.username,
        #         key_filename=self.key_file
        #     )
        # else:
        #     self.client.connect(
        #         self.host,
        #         port=self.port,
        #         username=self.username,
        #         password=self.password
        #     )
        # 
        # self.connected = True
        print(f"[SSH] Conectado a {self.username}@{self.host}:{self.port}")
    
    def execute_command(self, command, callback=None):
        """
        Ejecuta un comando en el servidor remoto
        
        Args:
            command: Comando a ejecutar
            callback: Función a llamar con la salida (opcional)
        
        Returns:
            Tupla (stdout, stderr, exit_status)
        """
        if not self.connected:
            return None, "No conectado", -1
        
        # TODO: Ejecutar comando real
        # stdin, stdout, stderr = self.client.exec_command(command)
        # exit_status = stdout.channel.recv_exit_status()
        # 
        # output = stdout.read().decode()
        # error = stderr.read().decode()
        # 
        # if callback:
        #     callback(output)
        # 
        # return output, error, exit_status
        
        print(f"[SSH] Ejecutando: {command}")
        return "Salida simulada", "", 0
    
    def start_interactive_shell(self, output_callback):
        """
        Inicia una shell interactiva
        
        Args:
            output_callback: Función llamada con cada línea de salida
        """
        # TODO: Implementar shell interactiva
        # channel = self.client.invoke_shell()
        # 
        # while True:
        #     if channel.recv_ready():
        #         output = channel.recv(1024).decode()
        #         output_callback(output)
        pass
    
    def upload_file(self, local_path, remote_path):
        """Sube un archivo al servidor remoto"""
        # TODO: Implementar con SFTP
        # sftp = self.client.open_sftp()
        # sftp.put(local_path, remote_path)
        # sftp.close()
        print(f"[SSH] Subiendo {local_path} -> {remote_path}")
    
    def download_file(self, remote_path, local_path):
        """Descarga un archivo del servidor remoto"""
        # TODO: Implementar con SFTP
        # sftp = self.client.open_sftp()
        # sftp.get(remote_path, local_path)
        # sftp.close()
        print(f"[SSH] Descargando {remote_path} -> {local_path}")
    
    def disconnect(self):
        """Cierra la conexión SSH"""
        if self.client:
            # self.client.close()
            self.connected = False
            print("[SSH] Desconectado")
