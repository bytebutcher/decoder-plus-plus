from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QTextLayout
from PyQt5.QtWidgets import QLabel, QSizePolicy


class ElidedLabel(QLabel):
    """
    Label which automatically cuts text at max-length and draws trailing punctuation.
    """

    elisionChanged = pyqtSignal(bool)

    def __init__(self, text):
        super(__class__, self).__init__(text)
        self._content = text
        self._elided = False
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def setText(self, newText):
        self._content = newText
        self.update()

    def paintEvent(self, event: QPaintEvent):
        super(__class__, self).paintEvent(event)

        painter = QPainter(self)
        font_metrics = painter.fontMetrics()

        did_elide = False
        line_spacing = font_metrics.lineSpacing()
        y = 0

        textLayout = QTextLayout(self._content, painter.font())
        textLayout.beginLayout()
        while True:
            line = textLayout.createLine()
            if not line.isValid():
                break

            line.setLineWidth(self.width())
            next_line_y = y + line_spacing

            if self.height() >= next_line_y + line_spacing:
                line.draw(painter, QPoint(y, 6))
                y = next_line_y
            else:
                last_line = self._content[line.textStart():]
                elided_last_line = font_metrics.elidedText(last_line, Qt.ElideRight, self.width())
                painter.drawText(QPoint(0, y + font_metrics.ascent() + 6), elided_last_line)
                line = textLayout.createLine()
                did_elide = line.isValid()
                break

        textLayout.endLayout()

        if did_elide is not self._elided:
            self._elided = did_elide
            self.elisionChanged.emit(did_elide)