from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint

class Toast(QLabel):
    def __init__(self, parent, message, duration=2000):
        super().__init__(message, parent)
        self.setStyleSheet("""
            QLabel {
                background-color: #323232;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.adjustSize()

        center_x = (parent.width() - self.width()) // 2
        center_y = (parent.height() - self.height()) // 2
        self.move(parent.mapToGlobal(QPoint(center_x, center_y)))

        self.show()
        self.animate_out(duration)

    def animate_out(self, duration):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(1000)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()
        anim.finished.connect(self.deleteLater)
        QTimer.singleShot(duration, self.close)
