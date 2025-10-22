import time

class Timer:
    """
    Una clase de cronómetro simple para medir el tiempo transcurrido.
    """
    def __init__(self):
        """Inicializa el cronómetro sin tiempo de inicio."""
        self.start_time = None

    def start(self):
        """Inicia el cronómetro guardando el tiempo actual."""
        if self.start_time is not None:
            print("Advertencia: El cronómetro ya estaba iniciado. Reiniciando.")
        self.start_time = time.time()

    def stop(self):
        """
        Detiene el cronómetro y devuelve el tiempo transcurrido en segundos,
        redondeado a dos decimales.
        Lanza un error si se intenta detener sin haberlo iniciado.
        """
        if self.start_time is None:
            raise RuntimeError("El cronómetro no fue iniciado antes de detenerlo.")
        
        elapsed_time = time.time() - self.start_time
        self.start_time = None  # Reinicia para que pueda ser usado de nuevo.
        return round(elapsed_time, 2)

# --- Bloque de prueba ---
if __name__ == "__main__":
    print("--- Probando la clase Timer ---")
    my_timer = Timer()
    
    print("Iniciando cronómetro...")
    my_timer.start()
    
    time.sleep(1.5) # Simulamos una tarea
    
    elapsed = my_timer.stop()
    print(f"Tiempo transcurrido: {elapsed} segundos. (Debería ser cercano a 1.5)")

    try:
        my_timer.stop()
    except RuntimeError as e:
        print(f"Prueba de error exitosa: {e}")