from pyPS4Controller.controller import Controller

class MyController(Controller):
    """
    Controlador PS4 personalizado con callbacks configurables
    """
    def __init__(self, interface="/dev/input/js0", connecting_using_ds4drv=False):
        super().__init__(interface=interface, connecting_using_ds4drv=connecting_using_ds4drv)
        self.button_callbacks = {}
    
    def start_listening(self, **kwargs):
        # Inicia la escucha de eventos             self.listen(**kwargs)
        self.listen(**kwargs)
    
    def on_x_press(self):
        self._execute_callback('x_press')
    
    def on_x_release(self):
        self._execute_callback('x_release')
    
    def on_circle_press(self):
        self._execute_callback('circle_press')
    
    def on_circle_release(self):
        self._execute_callback('circle_release')
    
    def on_square_press(self):
        self._execute_callback('square_press')
    
    def on_square_release(self):
        self._execute_callback('square_release')
    
    def on_triangle_press(self):
        self._execute_callback('triangle_press')
    
    def on_triangle_release(self):
        self._execute_callback('triangle_release')
    
    # ===== L1/R1 =====
    def on_L1_press(self):
        self._execute_callback('l1_press')
    
    def on_L1_release(self):
        self._execute_callback('l1_release')
    
    def on_R1_press(self):
        self._execute_callback('r1_press')
    
    def on_R1_release(self):
        self._execute_callback('r1_release')
    
    # ===== L2/R2 (Gatillos) =====
    def on_L2_press(self, value):
        self._execute_callback('l2_press', value)
    
    def on_L2_release(self):
        self._execute_callback('l2_release')
    
    def on_R2_press(self, value):
        self._execute_callback('r2_press', value)
    
    def on_R2_release(self):
        self._execute_callback('r2_release')
    
    # ===== D-PAD =====
    def on_up_arrow_press(self):
        self._execute_callback('up_press')
    
    def on_up_arrow_release(self):
        self._execute_callback('up_release')
    
    def on_down_arrow_press(self):
        self._execute_callback('down_press')
    
    def on_down_arrow_release(self):
        self._execute_callback('down_release')
    
    def on_left_arrow_press(self):
        self._execute_callback('left_press')
    
    def on_left_arrow_release(self):
        self._execute_callback('left_release')
    
    def on_right_arrow_press(self):
        self._execute_callback('right_press')
    
    def on_right_arrow_release(self):
        self._execute_callback('right_release')
    
    # ===== JOYSTICKS =====
    def on_L3_up(self, value):
        self._execute_callback('l3_up', value)
    
    def on_L3_down(self, value):
        self._execute_callback('l3_down', value)
    
    def on_L3_left(self, value):
        self._execute_callback('l3_left', value)
    
    def on_L3_right(self, value):
        self._execute_callback('l3_right', value)
    
    def on_L3_press(self):
        self._execute_callback('l3_press')
    
    def on_L3_release(self):
        self._execute_callback('l3_release')
    
    def on_R3_up(self, value):
        self._execute_callback('r3_up', value)
    
    def on_R3_down(self, value):
        self._execute_callback('r3_down', value)
    
    def on_R3_left(self, value):
        self._execute_callback('r3_left', value)
    
    def on_R3_right(self, value):
        self._execute_callback('r3_right', value)
    
    def on_R3_press(self):
        self._execute_callback('r3_press')
    
    def on_R3_release(self):
        self._execute_callback('r3_release')
    
    # ===== BOTONES ESPECIALES =====
    def on_options_press(self):
        self._execute_callback('options_press')
    
    def on_share_press(self):
        self._execute_callback('share_press')
    
    def on_playstation_button_press(self):
        self._execute_callback('ps_button_press')
    
    # ===== MÉTODOS AUXILIARES =====
    def _execute_callback(self, event_name, value=None):
        """Ejecuta el callback asociado a un evento si existe"""
        if event_name in self.button_callbacks:
            callback = self.button_callbacks[event_name]
            try:
                if value is not None:
                    callback(value)
                else:
                    callback()
            except Exception as e:
                print(f"⚠️ Error en callback '{event_name}': {e}")
    
    def register_callback(self, event_name, callback_function):
        """Registra un callback para un evento específico"""
        if not callable(callback_function):
            raise ValueError("callback_function debe ser una función callable")
        self.button_callbacks[event_name] = callback_function