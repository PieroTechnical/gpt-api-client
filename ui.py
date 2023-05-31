import sys
import importlib

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QPlainTextEdit, QSizePolicy, QWidget, QTextEdit, QVBoxLayout, QPushButton, QTabWidget, QLabel, QLineEdit, QComboBox)
from PyQt5.QtGui import QColor, QPalette, QTextCursor
from PyQt5.QtCore import Qt

import wrap_gpt

importlib.reload(wrap_gpt)


class AIAssistantUI(QMainWindow):
    def __init__(self, application_manager):
        super().__init__()
        self.build_ui()

#        self.update_personality_dropdown()
        self.update_chat_display()

    def build_ui(self):
        self.setWindowTitle('AI Assistant')
        self.setMinimumSize(800, 800)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.build_chat_tab()
        self.build_script_tab()
        self.build_customize_tab()

        self.connect_shortcuts()

    def build_chat_tab(self):
        self.chat_tab = QWidget()
        chat_layout = QVBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(100)
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_user_input)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.personality_switch_combo = QComboBox()
        self.personality_switch_combo.currentIndexChanged.connect(self.switch_personality)

        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(self.input_text)
        chat_layout.addWidget(self.send_button)
        chat_layout.addWidget(self.personality_switch_combo)

        self.chat_tab.setLayout(chat_layout)
        self.tab_widget.addTab(self.chat_tab, 'Chat')
        self.update_personality_dropdown()

    def build_script_tab(self):
        self.script_tab = QWidget()
        self.script_tab_widget = QTabWidget()
        self.script_tab_widget.setTabsClosable(True) # Enable close button on each tab
        self.script_tab_widget.tabCloseRequested.connect(self.on_tab_close_requested) # Connect close button to custom slot

        # Create add tab button and set as corner widget
        self.add_tab_button = QPushButton('+')
        self.add_tab_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.add_tab_button.clicked.connect(self.add_script_tab)
        self.script_tab_widget.setCornerWidget(self.add_tab_button)

        script_main_layout = QVBoxLayout()
        script_main_layout.addWidget(self.script_tab_widget)
        self.script_tab.setLayout(script_main_layout)
        self.tab_widget.addTab(self.script_tab, 'Script')
        self.add_script_tab()

    def on_tab_close_requested(self, index):
        self.script_tab_widget.removeTab(index)  # remove the requested tab
        
        if self.script_tab_widget.count() == 0:
            self.add_script_tab()

    def add_script_tab(self):
        # Create a new tab for the script tab widget
        self.script_subtab = QWidget()
        script_layout = QVBoxLayout()

        # Create the text field, execute button, and output window
        script_input_text = QPlainTextEdit()
        script_execute_button = QPushButton('Execute')
        # Connect button to the function that executes the script
        script_execute_button.clicked.connect(lambda: self.execute_script(script_input_text, script_output_window))
        script_output_window = QTextEdit()
        script_output_window.setReadOnly(True)

        # Add the components to the layout
        script_layout.addWidget(script_input_text)
        script_layout.addWidget(script_output_window)
        script_layout.addWidget(script_execute_button)

        # Set the layout for the tab
        self.script_subtab.setLayout(script_layout)

        # Add the subtab to the script tab widget
        self.script_tab_widget.addTab(self.script_subtab, f'Tab {self.script_tab_widget.count() + 1}')

    def execute_script(self, input_text, output_window):
        pass

    def build_customize_tab(self):
        self.customize_tab = QWidget()
        customize_layout = QVBoxLayout()

        self.personality_label = QLabel('Personality Name:')
        self.personality_name_input = QLineEdit()
        self.prompt_label = QLabel('Prompt:')
        self.prompt_input = QTextEdit()
        self.model_label = QLabel('GPT Model:')
        self.model_combo = QComboBox()
        self.model_combo.addItems(wrap_gpt.ApplicationManager.get_list_models())

        customize_layout.addWidget(self.personality_label)
        customize_layout.addWidget(self.personality_name_input)
        customize_layout.addWidget(self.prompt_label)
        customize_layout.addWidget(self.prompt_input)
        customize_layout.addWidget(self.model_label)
        customize_layout.addWidget(self.model_combo)

        self.customize_tab.setLayout(customize_layout)
        self.tab_widget.addTab(self.customize_tab, 'Customize')

    def connect_shortcuts(self):
        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_Return), self)
        shortcut.activated.connect(self.send_user_input)

    def update_personality_dropdown(self):
        self.personality_switch_combo.clear()
        self.personality_switch_combo.addItems(wrap_gpt.ApplicationManager.get_entity_personality_names())

    def switch_personality(self, index):
        selected_personality = self.personality_switch_combo.itemText(index)
        self.load_personality(selected_personality)
        self.update_chat_display()

    def update_chat_display(self):
        self.chat_display.clear()
        self.chat_display.append(wrap_gpt.ApplicationManager.get_chat_history())

    def send_user_input(self):
        user_input = self.input_text.toPlainText()
        wrap_gpt.ApplicationManager.user_ask_message('user', user_input)
        self.update_chat_display()
        self.input_text.clear()
        self.chat_display.moveCursor(QTextCursor.End)  # Scroll to the bottom of the chat display

    def load_personality(self, personality_name):
        personality = wrap_gpt.ApplicationManager.get_entity_personality_by_name(personality_name)
        print(f"Changed ai instance to: {personality['name']}")
        wrap_gpt.ApplicationManager.chat_environment.ai_instances = [wrap_gpt.AIInstance(personality)]


def main():    
    # Create the application
    app = QApplication(sys.argv)

    # Use a palette to switch to dark colors:
    setup_dark_palette(app)

    # Create the main window
    window = AIAssistantUI(wrap_gpt.ApplicationManager)
    window.show()

    # Run the event loop
    sys.exit(app.exec_())

def setup_dark_palette(app):
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    # Set the style sheet to decrease the border size
    app.setStyleSheet("QWidget::pane { border-width: 1px; }")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

if __name__ == '__main__':
    main()

