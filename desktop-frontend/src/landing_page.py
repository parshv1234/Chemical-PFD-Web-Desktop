from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from src.theme import apply_theme_to_screen
from src.navigation import slide_to_index


class ActionCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, icon_text, title, description, parent=None):
        super().__init__(parent)
        self.setObjectName("actionCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(240, 140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        icon_label = QLabel(icon_text)
        icon_label.setObjectName("cardIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("cardDesc")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class RecentProjectItem(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, project_name, last_opened, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.project_name = project_name
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(15)

        icon_label = QLabel("📄")
        icon_label.setObjectName("recentIcon")
        layout.addWidget(icon_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(project_name)
        name_label.setObjectName("recentName")
        info_layout.addWidget(name_label)

        time_label = QLabel(last_opened)
        time_label.setObjectName("recentTime")
        info_layout.addWidget(time_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        arrow_label = QLabel("→")
        arrow_label.setObjectName("recentArrow")
        layout.addWidget(arrow_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.project_name)
        super().mousePressEvent(event)


class LandingPage(QWidget):
    new_project_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("landingPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # background
        self.bgwidget = QWidget(self)
        self.bgwidget.setObjectName("bgwidget")
        layout.addWidget(self.bgwidget)

        self.content_layout = QVBoxLayout(self.bgwidget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)

        # HEADER BAR (Logout only)
        header_bar = QWidget(self.bgwidget)
        header_bar.setObjectName("headerBar")

        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setSpacing(10)
        header_layout.addStretch()

        # LOGOUT button
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setObjectName("logoutButton")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(self.logout_btn)

        self.content_layout.addWidget(header_bar)

        # ------------------------
        # Main center content
        # ------------------------
        center_widget = QWidget()
        center_widget.setMaximumWidth(800)
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(30)

        header_layout2 = QVBoxLayout()
        header_layout2.setSpacing(5)

        header_label = QLabel("Welcome to Chemical PFD")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignCenter)
        header_layout2.addWidget(header_label)

        subtitle_label = QLabel("Create or edit your process flow diagrams")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout2.addWidget(subtitle_label)

        center_layout.addLayout(header_layout2)
        center_layout.addSpacing(20)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignCenter)

        self.new_card = ActionCard("📝", "New Project", "Start a new diagram from scratch")
        self.new_card.clicked.connect(self.new_project_clicked.emit)
        cards_layout.addWidget(self.new_card)

        self.open_card = ActionCard("📂", "Open Project", "Open an existing PFD file")
        cards_layout.addWidget(self.open_card)

        center_layout.addLayout(cards_layout)
        center_layout.addSpacing(30)

        recent_header = QLabel("Recent Projects")
        recent_header.setObjectName("sectionHeader")
        center_layout.addWidget(recent_header)

        recent_container = QFrame()
        recent_container.setObjectName("recentContainer")
        recent_layout = QVBoxLayout(recent_container)
        recent_layout.setContentsMargins(0, 0, 0, 0)
        recent_layout.setSpacing(0)

        placeholder_projects = [
            ("Distillation_Unit_A.pfd", "2 hours ago"),
            ("Heat_Exchanger_Network.pfd", "Yesterday"),
            ("Reactor_Setup_V2.pfd", "3 days ago")
        ]

        for name, time in placeholder_projects:
            item = RecentProjectItem(name, time)
            recent_layout.addWidget(item)

            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setObjectName("divider")
            recent_layout.addWidget(line)

        center_layout.addWidget(recent_container)

        hlayout = QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(center_widget)
        hlayout.addStretch()
        self.content_layout.addLayout(hlayout)
        self.content_layout.addStretch()

        # apply theme (static)
        apply_theme_to_screen(self)

        # Logout handling
        self.logout_btn.clicked.connect(self.on_logout_clicked)

    def go_to_welcome(self):
        slide_to_index(0, direction=-1)

    # LOGOUT
    def on_logout_clicked(self):
        import src.app_state as app_state
        from src.navigation import slide_to_index

        # Clear authentication state
        app_state.access_token = None
        app_state.refresh_token = None
        app_state.current_user = None

        print("Logged out. Tokens cleared.")

        # Navigate to welcome screen
        slide_to_index(0, direction=-1)