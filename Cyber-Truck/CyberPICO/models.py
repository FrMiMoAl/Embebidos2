"""
Modelos de Comportamiento - Raspberry Pi Pico W
Define los diferentes modos de operación del vehículo (Sin threads)
"""

import utime

class BaseModel:
    """Clase base para todos los modelos"""
    def __init__(self, hardware):
        self.hardware = hardware
        self.active = False
        self.running = False
    
    def start(self):
        """Iniciar el modelo"""
        self.active = True
        self.running = True
        print(f"{self.__class__.__name__} started")
    
    def stop(self):
        """Detener el modelo"""
        self.running = False
        self.active = False
        self.hardware.stop_motors()
        print(f"{self.__class__.__name__} stopped")
    
    def update(self):
        """Actualización periódica del modelo"""
        pass


class ModelA(BaseModel):
    """
    Modelo A: Movimiento autónomo con evasión de obstáculos
    - Avanza hasta encontrar un objeto
    - Gira 180° en su lugar
    - Continúa avanzando
    """
    def __init__(self, hardware):
        super().__init__(hardware)
        self.state = "IDLE"  # IDLE, MOVING_FORWARD, ROTATING, TURNING
        self.obstacle_distance = 20  # cm
        self.forward_speed = 50  # velocidad base
        self.rotation_start_time = 0
        self.rotation_duration = 0
        self.turn_active = False
        self.turn_angle_remaining = 0
        self.turn_direction = 'RIGHT'
        self.turn_speed = 30
        self.turn_start_time = 0
    
    def start(self):
        """Iniciar Modelo A"""
        super().start()
        self.state = "MOVING_FORWARD"
        self.hardware.set_headlights('LOW')
        self.hardware.set_brake_lights(False)
        print("Model A: Starting autonomous movement")
    
    def update(self):
        """Loop principal del Modelo A"""
        if not self.running:
            return
        
        # Manejar giro no bloqueante si está activo
        if self.turn_active:
            self._update_turn()
            return
        
        distance = self.hardware.get_distance()
        
        if self.state == "MOVING_FORWARD":
            # Avanzar hasta encontrar obstáculo
            if distance > 0 and distance < self.obstacle_distance:
                print(f"Obstacle detected at {distance:.1f}cm. Rotating 180°")
                self.state = "ROTATING"
                self.hardware.stop_motors()
                self.hardware.set_brake_lights(True)
                self.hardware.set_turn_signals('BOTH', True)
                
                # Calcular tiempo de rotación (180°)
                self.rotation_start_time = utime.ticks_ms()
                self.rotation_duration = 2000  # 2 segundos para 180° (ajustar según velocidad)
                
                # Iniciar rotación en lugar
                self.hardware.set_motor_speed(40, -40)  # Giro a la derecha
            else:
                # Continuar avanzando
                self.hardware.set_motor_speed(self.forward_speed, self.forward_speed)
                self.hardware.set_brake_lights(False)
        
        elif self.state == "ROTATING":
            # Verificar si completó la rotación de 180°
            elapsed = utime.ticks_diff(utime.ticks_ms(), self.rotation_start_time)
            
            if elapsed >= self.rotation_duration:
                # Completó rotación
                self.hardware.stop_motors()
                self.hardware.center_steering()
                self.hardware.set_turn_signals('OFF', False)
                self.state = "MOVING_FORWARD"
                print("Rotation complete. Resuming forward motion")
                utime.sleep_ms(500)  # Pausa breve
    
    def turn(self, angle, direction):
        """
        Realizar un giro de N grados sin detener el programa
        angle: grados a girar (positivo)
        direction: 'LEFT' o 'RIGHT'
        """
        if self.turn_active:
            print("Turn already in progress")
            return False
        
        self.turn_active = True
        self.turn_angle_remaining = abs(angle)
        self.turn_direction = direction.upper()
        self.turn_start_time = utime.ticks_ms()
        
        # Activar señal direccional
        if self.turn_direction == 'LEFT':
            self.hardware.set_turn_signals('LEFT', True)
        else:
            self.hardware.set_turn_signals('RIGHT', True)
        
        print(f"Starting turn: {angle}° {direction}")
        return True
    
    def _update_turn(self):
        """Actualizar estado del giro no bloqueante"""
        # Estimar tiempo necesario por grado (ajustar según calibración)
        ms_per_degree = 20  # 20ms por grado aproximadamente
        target_duration = self.turn_angle_remaining * ms_per_degree
        elapsed = utime.ticks_diff(utime.ticks_ms(), self.turn_start_time)
        
        if elapsed < target_duration:
            # Continuar girando
            angle = (self.turn_angle_remaining / 90) * 45  # Proporcional
            angle = min(45, max(-45, angle))
            
            if self.turn_direction == 'LEFT':
                self.hardware.set_steering_angle(-angle)
            else:
                self.hardware.set_steering_angle(angle)
            
            # Mantener movimiento adelante
            self.hardware.set_motor_speed(self.turn_speed, self.turn_speed)
        else:
            # Giro completado
            self.hardware.center_steering()
            self.hardware.set_turn_signals('OFF', False)
            self.turn_active = False
            print("Turn completed")
    
    def set_speed(self, speed):
        """Establecer velocidad de avance"""
        self.forward_speed = max(0, min(100, speed))
        print(f"Model A: Speed set to {self.forward_speed}")
    
    def stop(self):
        """Detener Modelo A"""
        self.turn_active = False
        super().stop()
        self.hardware.set_turn_signals('OFF', False)
        self.hardware.set_headlights('OFF')
        self.state = "IDLE"


class ModelB(BaseModel):
    """
    Modelo B: Control para visión computacional
    Maneja características básicas mientras espera comandos de visión
    """
    def __init__(self, hardware):
        super().__init__(hardware)
        self.manual_control = True
        self.current_speed = 0
        self.current_steering = 0
    
    def start(self):
        """Iniciar Modelo B"""
        super().start()
        self.hardware.set_headlights('HIGH')
        print("Model B ready for computer vision commands")
    
    def update(self):
        """Modelo B espera comandos externos (de visión computacional)"""
        if not self.running:
            return
        
        # Mantener estado actual
        # Los comandos vienen via UART desde la Raspberry Pi 4
        pass
    
    def set_speed(self, speed):
        """Control manual de velocidad"""
        self.current_speed = speed
        self.hardware.set_motor_speed(speed, speed)
        print(f"Model B: Speed set to {speed}")
    
    def set_steering(self, angle):
        """Control manual de dirección"""
        self.current_steering = angle
        self.hardware.set_steering_angle(angle)
        print(f"Model B: Steering set to {angle}°")
    
    def turn(self, angle, direction):
        """Girar N grados"""
        if direction.upper() == 'LEFT':
            self.set_steering(-abs(angle))
        else:
            self.set_steering(abs(angle))
    
    def stop(self):
        """Detener Modelo B"""
        super().stop()
        self.hardware.set_headlights('OFF')


class ModelC(BaseModel):
    """
    Modelo C: Por implementar
    Placeholder para futura funcionalidad
    """
    def __init__(self, hardware):
        super().__init__(hardware)
        print("Model C initialized (not yet implemented)")
    
    def start(self):
        super().start()
        print("Model C: Not yet implemented")
    
    def update(self):
        if not self.running:
            return
        # Por implementar
        pass


class ModelD(BaseModel):
    """
    Modelo D: Por implementar
    Placeholder para futura funcionalidad
    """
    def __init__(self, hardware):
        super().__init__(hardware)
        print("Model D initialized (not yet implemented)")
    
    def start(self):
        super().start()
        print("Model D: Not yet implemented")
    
    def update(self):
        if not self.running:
            return
        # Por implementar
        pass3