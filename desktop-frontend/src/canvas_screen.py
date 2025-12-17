import os
import json
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton
)

from src.component_library import ComponentLibrary
import src.app_state as app_state
from src.component_widget import ComponentWidget
from src.theme import apply_theme_to_screen
from src.navigation import slide_to_index
import src.app_state as app_state


class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("canvasArea")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        palette = self.palette()
        if app_state.current_theme == "dark":
            palette.setColor(self.backgroundRole(), QtGui.QColor("#0f172a"))
        else:
            palette.setColor(self.backgroundRole(), Qt.white)

        self.setPalette(palette)

        self.setAcceptDrops(True)
        self.setMouseTracking(True)

        # Keep child widgets alive
        self.components = []

        # Load grips.json config
        self.component_config = {}
        self._load_config()

    def update_canvas_theme(self):
        palette = self.palette()
        if app_state.current_theme == "dark":
            palette.setColor(self.backgroundRole(), QtGui.QColor("#0f172a"))
        else:
            palette.setColor(self.backgroundRole(), Qt.white)

        self.setPalette(palette)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if app_state.current_theme == "dark":
            dot_color = QtGui.QColor(90, 90, 90)
        else:
            dot_color = QtGui.QColor(180, 180, 180)

        painter.setPen(dot_color)
        grid_spacing = 30

        for x in range(0, self.width(), grid_spacing):
            for y in range(0, self.height(), grid_spacing):
                painter.drawPoint(x, y)


    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        pos = event.pos()
        text = event.mimeData().text()
        self.add_component_label(text, pos)
        event.acceptProposedAction()

    def add_component_label(self, text, pos: QPoint):
        """Creates a simple label at the drop position. Replace with your real component creation."""
        lbl = QLabel(text, self)
        lbl.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        lbl.move(pos)
        lbl.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,230);
                border: 1px solid #999;
                padding: 6px;
                border-radius: 6px;
                font: 9pt "Segoe UI";
            }
        """)
        lbl.show()
        lbl.adjustSize()
    def mousePressEvent(self, event):
        self.deselect_all()
        super().mousePressEvent(event)

    def deselect_all(self):
        for child in self.findChildren(ComponentWidget):
            child.set_selected(False)

    def handle_selection(self, component, add_to_selection=False):
        if add_to_selection:
            component.set_selected(not component.is_selected)
        else:
            if component.is_selected:
                return
            self.deselect_all()
            component.set_selected(True)


    def _load_config(self):
        try:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base, "ui", "assets", "grips.json")

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    self.component_config[item["component"]] = item
        except Exception as e:
            print("Failed to load grips.json:", e)

    def get_component_config(self, name):
        ID_MAP = {
            'Exchanger905': "905Exchanger",
            'KettleReboiler907': "907Kettle Reboiler",
            'OneCellFiredHeaterFurnace': "One Cell Fired Heater",
            'TwoCellFiredHeaterFurnace': "Two Cell Fired Heater"
        }
        name = ID_MAP.get(name, name)

        # exact match
        if name in self.component_config:
            return self.component_config[name]

        # fuzzy
        def clean(s):
            return s.lower().translate(str.maketrans('', '', ' ,_/-()'))

        target = clean(name)

        for key in self.component_config:
            if clean(key) == target:
                return self.component_config[key]

        return {}

    def find_svg_for_component(self, name):
        ID_MAP = {
            'Exchanger905': "905Exchanger",
            'KettleReboiler907': "907Kettle Reboiler",
            'OneCellFiredHeaterFurnace': "One Cell Fired Heater, Furnace",
            'TwoCellFiredHeaterFurnace': "Two Cell Fired Heater, Furnace"
        }
        name = ID_MAP.get(name, name)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        svg_dir = os.path.join(base_dir, "ui", "assets", "svg")

        def clean(s):
            return s.lower().translate(str.maketrans('', '', ' ,_/-()'))

        target = clean(name)

        for root, _, files in os.walk(svg_dir):
            for f in files:
                if not f.endswith(".svg"):
                    continue

                fname = f[:-4]
                if clean(fname) == target:
                    return os.path.join(root, f)

        return None

    def add_component_label(self, text, pos):
        svg = self.find_svg_for_component(text)
        config = self.get_component_config(text)

        if not config:
            config = {}

        if "default_label" not in config:
            import re
            label_text = re.sub(r"(\w)([A-Z])", r"\1 \2", text)
            config["default_label"] = label_text

        # fallback text if no svg
        if not svg:
            lbl = QLabel(text, self)
            lbl.move(pos)
            lbl.setStyleSheet("color:white; background:rgba(0,0,0,0.5); padding:4px; border-radius:4px;")
            lbl.show()
            lbl.adjustSize()
            return

        comp = ComponentWidget(svg, self, config=config)
        comp.move(pos)
        comp.show()
        self.components.append(comp)


#   MAIN EDITOR WINDOW
class CanvasScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        wrapper = QWidget()
        wrapper.setObjectName("bgwidget")
        self.setCentralWidget(wrapper)

        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # HEADER BAR
        header = QWidget()
        header.setObjectName("editorHeader")
        header.setFixedHeight(50)
        h = QHBoxLayout(header)
        h.setContentsMargins(15, 8, 15, 8)

        back = QPushButton("← Back")
        back.setObjectName("backButton")
        back.clicked.connect(lambda: slide_to_index(3, direction=-1))
        h.addWidget(back)

        title = QLabel("Editor — Process Flow Diagram")
        title.setObjectName("editorTitle")
        title.setAlignment(Qt.AlignCenter)
        h.addWidget(title, stretch=1)

        logout = QPushButton("Logout")
        logout.setObjectName("headerLogout")
        logout.clicked.connect(self.logout)
        h.addWidget(logout)

        layout.addWidget(header)

        # CANVAS
        self.canvas = CanvasWidget(self)
        layout.addWidget(self.canvas)

        # COMPONENT LIBRARY
        self.library = ComponentLibrary(self)
        self.library.setMinimumWidth(280)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library)

        apply_theme_to_screen(self)
        self.canvas.update_canvas_theme()

    def logout(self):
        app_state.access_token = None
        app_state.refresh_token = None
        app_state.current_user = None
        print("Logged out from Editor.")
        slide_to_index(0, direction=-1)
