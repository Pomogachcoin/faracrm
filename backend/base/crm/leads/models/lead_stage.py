from backend.base.system.dotorm.dotorm.fields import (
    Char,
    Integer,
    Boolean,
    Selection,
)
from backend.base.system.schemas.base_schema import Id
from backend.base.system.dotorm.dotorm.model import DotModel


class LeadStage(DotModel):
    __table__ = "lead_stage"

    id: Id = Integer(primary_key=True)
    name: str = Char(string="Stage Name", required=True)
    sequence: int = Integer(string="Sequence", default=10)
    active: bool = Boolean(default=True)
    fold: bool = Boolean(default=False, string="Folded in Kanban")
    color: str = Char(string="Color", default="#3498db")
    partner_action: str = Selection(
        options=[
            ("none", "Нет"),
            ("set_spam", "Убрать из клиентов"),
            ("set_partner", "Сделать партнёром"),
        ],
        default="none",
        string="Действие с партнёром",
    )


INITIAL_LEAD_STAGES = [
    {
        "name": "Новый",
        "sequence": 10,
        "active": True,
        "fold": False,
        "color": "#17a2b8",
        "partner_action": "none",
    },
    {
        "name": "КП отправлено",
        "sequence": 20,
        "active": True,
        "fold": False,
        "color": "#ffc107",
        "partner_action": "none",
    },
    {
        "name": "В работе",
        "sequence": 30,
        "active": True,
        "fold": False,
        "color": "#fd7e14",
        "partner_action": "none",
    },
    {
        "name": "Выиграно",
        "sequence": 40,
        "active": True,
        "fold": False,
        "color": "#28a745",
        "partner_action": "none",
    },
    {
        "name": "Проиграно",
        "sequence": 50,
        "active": True,
        "fold": True,
        "color": "#dc3545",
        "partner_action": "none",
    },
    {
        "name": "Партнёр",
        "sequence": 500,
        "active": True,
        "fold": False,
        "color": "#20c997",
        "partner_action": "set_partner",
    },
    {
        "name": "Спам / Не целевой",
        "sequence": 999,
        "active": True,
        "fold": True,
        "color": "#6c757d",
        "partner_action": "set_spam",
    },
]
