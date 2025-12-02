class CounterModule:
    
    def __init__(self, label_columns):
        self.label_columns = label_columns
        self.contadores = {label: 0 for label in label_columns}
        self.ultimo_detectado = set()
    
    def update(self, detecciones):
        detectado_ahora = set(detecciones.keys())
        nuevos = detectado_ahora - self.ultimo_detectado
        
        for clase in nuevos:
            self.contadores[clase] += 1
            print(f"Detectado: {clase} (Total: {self.contadores[clase]})")
        
        self.ultimo_detectado = detectado_ahora
        
        return list(nuevos)
    
    def get_counts(self):
        return self.contadores.copy()
    
    def reset(self):
        self.contadores = {label: 0 for label in self.label_columns}
        self.ultimo_detectado = set()
        print("Contadores reiniciados")
    
    def get_formatted_counts(self):
        partes = [f"N{label}:{count}" for label, count in self.contadores.items()]
        return ",".join(partes)