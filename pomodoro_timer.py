import sys
import time
from PySide6.QtCore import QTimer, Qt, QUrl, QPoint, QEvent
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QFrame,
)
from PySide6.QtGui import QIcon
import os
import ctypes

# Windows API constants for setting window on top
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_NOZORDER = 0x0004
SWP_NOOWNERZORDER = 0x0200
GWL_EXSTYLE = -20
WS_EX_TOPMOST = 0x00000008
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000

# ShowWindow commands
SW_SHOW = 5
SW_SHOWNA = 8

# For Windows-specific handling
if sys.platform == "win32":
    user32 = ctypes.windll.user32


class ClickableButton(QPushButton):
    def __init__(self, text, parent=None, click_sound=None):
        super().__init__(text, parent)
        self.click_sound = click_sound

    def mousePressEvent(self, event):
        if self.click_sound and self.click_sound.isLoaded():
            self.click_sound.play()
        super().mousePressEvent(event)


class PomodoroTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        # Set window flags to make it frameless and always on top
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowFlag(
            Qt.WindowType.BypassWindowManagerHint, True
        )  # Bypass window manager
        self.setWindowFlag(
            Qt.WindowType.X11BypassWindowManagerHint, True
        )  # X11 specific bypass
        # Force the window to stay visible even on "Show Desktop" actions
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        # Set the window to be persistently on top
        self.setWindowOpacity(0.98)  # Slight opacity change to force topmost rendering
        # Create an event filter to capture global events
        app = QApplication.instance()
        app.installEventFilter(self)
        # Windows-specific "always on top" timer
        self.topmost_timer = QTimer()
        self.topmost_timer.timeout.connect(self.ensure_topmost)
        self.topmost_timer.start(500)  # Check every 500ms
        # Additional timer to keep checking visibility
        self.visibility_timer = QTimer()
        self.visibility_timer.timeout.connect(self.ensure_visibility)
        self.visibility_timer.start(100)  # Check visibility more frequently

        self.setFixedSize(200, 39)  # 5px shorter window

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: rgba(255, 255, 255, 0.4);
            }
            QLabel {
                color: black;
            }
            QPushButton {
                font-family: "Arial", sans-serif;
                background-color: rgba(255, 255, 255, 0);
                border-radius: 4px;
                padding: 0px 1px 1px 1px;
                color: black;
                min-width: 22px;
                max-width: 22px;
                min-height: 22px;
                max-height: 22px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.7);
            }
            #closeButton {
                background-color: rgba(255, 0, 0, 0.4);
                border: none;
                border-radius: 8px;
                padding: 1px;
                min-width: 16px;
                max-width: 16px;
                min-height: 16px;
                max-height: 16px;
            }
            #closeButton:hover {
                background-color: rgba(255, 0, 0, 0.6);
            }
            #backgroundFrame {
                background-color: rgba(255, 255, 255, 0.4);
                border-radius: 5px;
            }
        """
        )

        # Durations in minutes
        self.work_duration = 25
        self.short_break = 5
        self.long_break = 15
        self.sessions = 0

        self.time_left = self.work_duration * 60
        self.running = False
        self.is_break = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        # Setup sounds
        self.ding_sound = QSoundEffect()
        self.ding_sound.setSource(
            QUrl.fromLocalFile(os.path.abspath("pomodoro_sounds/ding.wav"))
        )
        self.ding_sound.setVolume(0.5)

        self.click_sound = QSoundEffect()
        self.click_sound.setSource(
            QUrl.fromLocalFile(os.path.abspath("pomodoro_sounds/click.wav"))
        )
        self.click_sound.setVolume(0.9)

        # Create close button
        self.close_button = ClickableButton("×", click_sound=self.click_sound)
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(lambda: sys.exit(0))
        self.close_button.setStyleSheet("font-size: 12px;")

        # Create background frame
        self.background_frame = QFrame()
        self.background_frame.setObjectName("backgroundFrame")
        self.background_frame.setStyleSheet(
            """
            QFrame#backgroundFrame {
                background-color: rgba(255, 255, 255, 0.4);
                border-radius: 5px;
            }
        """
        )

        self.label = QLabel(self.format_time(self.time_left), alignment=Qt.AlignCenter)
        self.label.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            color: black;
        """
        )

        self.status_label = QLabel("🍅", alignment=Qt.AlignCenter)
        self.status_label.setStyleSheet(
            """
            font-size: 12px;
            color: black;
        """
        )

        # Create smaller buttons
        self.play_pause_button = ClickableButton("⏯️", click_sound=self.click_sound)
        self.play_pause_button.clicked.connect(self.toggle_timer)

        self.reset_button = ClickableButton("🔁", click_sound=self.click_sound)
        self.reset_button.clicked.connect(self.reset_timer)

        # Create horizontal layout for buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.play_pause_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.setSpacing(2)

        # Create main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.label)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.close_button)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 5, 10, 5)

        # Set layout to background frame
        self.background_frame.setLayout(main_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def showEvent(self, event):
        """Position the window in the bottom right corner when shown and ensure topmost state"""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 200  # 200px padding from right
        y = screen.height() - self.height()
        self.move(QPoint(x, y))
        self.ensure_topmost()  # Make sure we're topmost when shown
        super().showEvent(event)

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.label.setText(self.format_time(self.time_left))
        else:
            self.ding_sound.play()
            self.timer.stop()
            self.running = False

            # sleep 2 seconds
            time.sleep(2)
            self.ding_sound.play()

            if not self.is_break:
                self.sessions += 1
                self.is_break = True
                self.status_label.setText("☕" if self.sessions % 4 else "☕☕")
                self.time_left = (
                    self.short_break * 60 if self.sessions % 4 else self.long_break * 60
                )
            else:
                self.is_break = False
                self.status_label.setText("🍅")
                self.time_left = self.work_duration * 60

            self.label.setText(self.format_time(self.time_left))

    def start_timer(self):
        if not self.running:
            self.running = True
            self.timer.start(1000)

    def pause_timer(self):
        if self.running:
            self.timer.stop()
            self.running = False

    def reset_timer(self):
        self.timer.stop()
        self.running = False
        self.is_break = False
        self.time_left = self.work_duration * 60
        self.label.setText(self.format_time(self.time_left))
        self.status_label.setText("🍅")

    def toggle_timer(self):
        if self.running:
            self.pause_timer()
        else:
            self.start_timer()

    def ensure_topmost(self):
        """Windows-specific function to ensure the window stays topmost"""
        if sys.platform == "win32":
            # Get window handle
            hwnd = int(self.winId())

            # Set extended window style to include TOPMOST and NOACTIVATE
            exstyle = user32.GetWindowLongA(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongA(
                hwnd,
                GWL_EXSTYLE,
                exstyle | WS_EX_TOPMOST | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW,
            )

            # Set window to be topmost with more aggressive flags
            user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST,
                0,
                0,
                0,
                0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
            )

            # Make sure the window is visible
            user32.ShowWindow(hwnd, SW_SHOWNA)

    def ensure_visibility(self):
        """Ensure the window is visible even after Show Desktop (Win+D)"""
        if not self.isVisible() and self.running:
            self.show()
            self.ensure_topmost()

    def eventFilter(self, obj, event):
        """Global event filter to catch desktop state changes"""
        # For any desktop state change events, ensure our window stays visible
        if event.type() == QEvent.ApplicationStateChange:
            self.ensure_topmost()
        return super().eventFilter(obj, event)

    def focusOutEvent(self, event):
        """Ensure topmost when focus is lost"""
        self.ensure_topmost()
        super().focusOutEvent(event)

    def changeEvent(self, event):
        """Handle window state changes"""
        if event.type() == QEvent.WindowStateChange:
            # Force the window to be visible if minimized
            if self.windowState() & Qt.WindowState.Minimized:
                self.setWindowState(self.windowState() & ~Qt.WindowState.Minimized)
                self.ensure_topmost()
        super().changeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroTimer()
    window.show()
    sys.exit(app.exec())
