# src/ui/main_window.py

import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt

# Importamos nuestra lógica central
from ..core_logic import reading
from ..core_logic.timer import Timer # Para medir la duración de la sesión

class HangulSprintApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangul Sprint - Modo Lectura Silencioso")
        self.setGeometry(100, 100, 600, 400) # x, y, ancho, alto

        self.current_level = 1 # Nivel de práctica inicial
        self.session_timer = Timer() # Cronómetro para la sesión global
        self.correct_phrases_in_session = 0
        self.total_phrases_in_session = 0
        self.session_started = False

        self.init_ui()
        self.start_new_round() # Cargar la primera frase al iniciar

    def init_ui(self):
        # Layout principal vertical
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 1. Etiqueta para la frase Hangul
        self.hangul_label = QLabel("Pulsa 'Empezar' para una nueva frase")
        self.hangul_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hangul_label.setStyleSheet("font-size: 36px; font-weight: bold; padding: 20px; color: #333;")
        main_layout.addWidget(self.hangul_label)

        # 2. Etiqueta para la traducción
        self.translation_label = QLabel("Traducción aquí")
        self.translation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.translation_label.setStyleSheet("font-size: 18px; font-style: italic; color: #666; margin-bottom: 20px;")
        main_layout.addWidget(self.translation_label)

        # 3. Contenedor para los botones de opción (romanización)
        options_layout = QVBoxLayout()
        self.option_buttons = []
        for i in range(4):
            btn = QPushButton(f"Opción {i+1}")
            btn.setStyleSheet("font-size: 16px; padding: 10px; margin: 5px; background-color: #f0f0f0; border: 1px solid #ccc;")
            btn.clicked.connect(self.check_answer) # Conectar al método de verificación
            options_layout.addWidget(btn)
            self.option_buttons.append(btn)
        
        main_layout.addLayout(options_layout)

        # 4. Etiqueta de feedback (Correcto/Incorrecto)
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 15px;")
        main_layout.addWidget(self.feedback_label)

        # 5. Botón de Siguiente/Empezar y contador de progreso
        control_layout = QHBoxLayout()
        self.next_button = QPushButton("Empezar")
        self.next_button.setStyleSheet("font-size: 18px; padding: 12px; background-color: #4CAF50; color: white; border-radius: 5px;")
        self.next_button.clicked.connect(self.start_new_round)
        control_layout.addWidget(self.next_button)

        self.progress_label = QLabel("Progreso: 0/0 (0%)")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.progress_label.setStyleSheet("font-size: 14px; color: #555;")
        control_layout.addWidget(self.progress_label)

        main_layout.addLayout(control_layout)

    def start_new_round(self):
        if not self.session_started:
            self.session_timer.start()
            self.session_started = True
            self.next_button.setText("Siguiente Frase")
            self.feedback_label.setText("") # Limpiar feedback al iniciar

        # Desactivar botones de opción para evitar clics dobles o antes de cargar
        for btn in self.option_buttons:
            btn.setEnabled(True)
            btn.setStyleSheet("font-size: 16px; padding: 10px; margin: 5px; background-color: #f0f0f0; border: 1px solid #ccc;")


        self.current_item_data = reading.start_reading_session(level=self.current_level)
        
        if self.current_item_data.get("error"):
            QMessageBox.warning(self, "Error", self.current_item_data["error"])
            self.hangul_label.setText("Error al cargar frase.")
            self.translation_label.setText("")
            for btn in self.option_buttons:
                btn.setText("")
                btn.setEnabled(False)
            return

        item = self.current_item_data['practice_item']
        options = self.current_item_data['silent_mode_options']

        self.hangul_label.setText(item['hangul'])
        self.translation_label.setText(item['translation_en'])
        self.correct_romanization = item['roman'] # Guardar la respuesta correcta

        # Asignar opciones a los botones
        for i, btn in enumerate(self.option_buttons):
            btn.setText(options[i])
            btn.setProperty("is_correct", options[i] == self.correct_romanization) # Guardar si es correcto

        self.update_progress_display()


    def check_answer(self):
        sender_button = self.sender() # El botón que fue clicado
        user_choice = sender_button.text()

        self.total_phrases_in_session += 1

        if user_choice == self.correct_romanization:
            self.correct_phrases_in_session += 1
            self.feedback_label.setText("¡Correcto!")
            self.feedback_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 15px; color: green;")
            sender_button.setStyleSheet("font-size: 16px; padding: 10px; margin: 5px; background-color: #d4edda; border: 1px solid #28a745;")
        else:
            self.feedback_label.setText("Incorrecto.")
            self.feedback_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 15px; color: red;")
            sender_button.setStyleSheet("font-size: 16px; padding: 10px; margin: 5px; background-color: #f8d7da; border: 1px solid #dc3545;")
            # Mostrar también cuál era la respuesta correcta
            for btn in self.option_buttons:
                if btn.property("is_correct"):
                    btn.setStyleSheet("font-size: 16px; padding: 10px; margin: 5px; background-color: #cce5ff; border: 1px solid #007bff;") # Azul para la correcta

        # Desactivar todos los botones después de una respuesta
        for btn in self.option_buttons:
            btn.setEnabled(False)
        
        self.update_progress_display()

    def update_progress_display(self):
        percentage = (self.correct_phrases_in_session / self.total_phrases_in_session) * 100 if self.total_phrases_in_session > 0 else 0
        self.progress_label.setText(f"Progreso: {self.correct_phrases_in_session}/{self.total_phrases_in_session} ({percentage:.0f}%)")

    def closeEvent(self, event):
        # Esto se ejecuta cuando la ventana se cierra
        if self.session_started:
            # Preguntar al usuario si quiere guardar la sesión
            reply = QMessageBox.question(self, 'Finalizar Sesión', 
                                         "¿Quieres guardar los resultados de tu sesión de lectura silenciosa?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.Yes)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Guardar la sesión
                reading.end_reading_session_and_save(
                    mode='silent_reading',
                    level=self.current_level,
                    timer=self.session_timer,
                    correct_phrases=self.correct_phrases_in_session,
                    total_phrases=self.total_phrases_in_session,
                    failed_phrases=[] # En modo silencioso no hay errores de caracteres/frases específicos
                )
                QMessageBox.information(self, "Sesión Guardada", "Tu sesión ha sido guardada.")
            else:
                QMessageBox.information(self, "Sesión No Guardada", "Tu sesión no ha sido guardada.")

        event.accept() # Aceptar el evento de cierre de ventana


# Este bloque es el punto de entrada de la aplicación de escritorio
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HangulSprintApp()
    window.show()
    sys.exit(app.exec())