# src/main.py

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt

# Importamos la lógica central (core_logic)
from core_logic import stats, reading, writing
from core_logic.timer import Timer # Necesitamos la clase Timer directamente

class HangulSprintApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangul Sprint - Aplicación de Prueba UI")
        self.setGeometry(100, 100, 600, 400) # x, y, ancho, alto
        self.current_practice_item = None
        self.timer = Timer() # Instancia del cronómetro

        self.init_ui()
        self.update_dashboard_summary()

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()

        # Etiqueta de resumen del Dashboard
        self.dashboard_label = QLabel("Cargando resumen del dashboard...")
        self.dashboard_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.dashboard_label)

        # Botón para mostrar una frase (Modo Lectura/Silencioso)
        self.read_button = QPushButton("Obtener Frase para Lectura (Nivel 1)")
        self.read_button.clicked.connect(self.get_reading_item)
        main_layout.addWidget(self.read_button)

        # Etiqueta para mostrar la frase Hangul
        self.hangul_label = QLabel("Frase Hangul: ")
        self.hangul_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px;")
        self.hangul_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.hangul_label)

        # Etiqueta para mostrar la romanización (respuesta)
        self.roman_label = QLabel("Romanización: ")
        self.roman_label.setStyleSheet("font-size: 18px; margin-bottom: 20px;")
        self.roman_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.roman_label)
        
        # Botón para mostrar la romanización (simula "revelar respuesta" o "modo silencioso")
        self.reveal_button = QPushButton("Mostrar Romanización")
        self.reveal_button.clicked.connect(self.reveal_romanization)
        self.reveal_button.setEnabled(False) # Desactivado hasta que haya una frase
        main_layout.addWidget(self.reveal_button)

        # Botón de prueba para simular guardar una sesión (escritura)
        self.save_test_session_button = QPushButton("Guardar Sesión de Escritura (Test)")
        self.save_test_session_button.clicked.connect(self.save_dummy_writing_session)
        main_layout.addWidget(self.save_test_session_button)

        self.setLayout(main_layout)

    def update_dashboard_summary(self):
        summary = stats.get_dashboard_summary()
        
        # CORRECCIÓN: Usar una sola f-string multilínea con triple comillas (""")
        summary_text = f"""Velocidad Media (WPM): {summary['avg_wpm']:.2f}
Precisión Media: {summary['avg_accuracy']:.2f}%
Errores Escritura: {', '.join([f"{e['letter']}({e['count']})" for e in summary['frequent_writing_errors']]) or 'Ninguno'}
Errores Lectura (frases): {', '.join([f"{e['hangul_phrase']}({e['count']})" for e in summary['frequent_reading_errors']]) or 'Ninguno'}"""
        
        self.dashboard_label.setText(f"Resumen del Dashboard:\n{summary_text}")

    def get_reading_item(self):
        level = 1 # Por ahora, siempre nivel 1 para la prueba
        item_data = reading.start_reading_session(level=level)
        
        if item_data.get("error"):
            QMessageBox.warning(self, "Error", item_data["error"])
            self.hangul_label.setText("Frase Hangul: (Error al cargar)")
            self.roman_label.setText("Romanización: ")
            self.reveal_button.setEnabled(False)
            self.current_practice_item = None
        else:
            self.current_practice_item = item_data['practice_item']
            self.hangul_label.setText(f"Frase Hangul: {self.current_practice_item['hangul']}")
            self.roman_label.setText("Romanización: (Haz clic en 'Mostrar Romanización')")
            self.reveal_button.setEnabled(True)
            self.timer.start() # Iniciar el cronómetro para esta frase

    def reveal_romanization(self):
        if self.current_practice_item:
            self.roman_label.setText(f"Romanización: {self.current_practice_item['roman']}")
            self.reveal_button.setEnabled(False) # Desactivar una vez mostrada

    def save_dummy_writing_session(self):
        # Simular una pequeña sesión de escritura con datos de ejemplo
        dummy_level = 1
        dummy_duration = self.timer.stop() if self.timer.start_time is not None else 5.0
        dummy_accuracy = 75.0
        dummy_wpm = 35.0
        dummy_total_chars = 60
        dummy_correct_chars = 45
        dummy_wrong_chars = 15
        dummy_errors = ['ㅂ', 'ㅁ', 'ㅊ']

        try:
            session_id = stats.save_session_results(
                mode='writing',
                level=dummy_level,
                duration=dummy_duration,
                accuracy=dummy_accuracy,
                wpm=dummy_wpm,
                total_chars=dummy_total_chars,
                correct_chars=dummy_correct_chars,
                wrong_chars=dummy_wrong_chars,
                letter_errors=dummy_errors
            )
            QMessageBox.information(self, "Sesión Guardada", f"Sesión de escritura de prueba guardada con ID: {session_id}")
            self.update_dashboard_summary() # Actualizar el resumen después de guardar
        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar", f"Hubo un error al guardar la sesión: {e}")


def main():
    app = QApplication(sys.argv)
    window = HangulSprintApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()