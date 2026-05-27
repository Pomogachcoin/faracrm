import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from backend.base.crm.company.models.company import Company
    from backend.base.crm.users.models.users import User
    from backend.base.crm.partners.models.partners import Partner
    from backend.base.crm.chat.models.chat_connector import ChatConnector
    from .lead_stage import LeadStage

from ...partners.models.contact import Contact
from backend.base.system.dotorm.dotorm.fields import (
    Char,
    Integer,
    Boolean,
    Many2one,
    One2many,
    Selection,
    Text,
)
from backend.base.system.schemas.base_schema import Id
from backend.base.crm.users.audit_mixin import AuditMixin
from backend.base.system.core.enviroment import env
from backend.base.crm.security.polymorphic_parent import (
    PolymorphicParentMixin,
)


class Lead(AuditMixin, PolymorphicParentMixin):
    __table__ = "leads"

    id: Id = Integer(primary_key=True)
    name: str = Char(string="Lead Name")
    active: bool = Boolean(default=True)
    stage_id: "LeadStage" = Many2one(
        lambda: env.models.lead_stage,
        string="Stage",
        index=True,
        ondelete="restrict",
    )
    user_id: "User | None" = Many2one(
        lambda: env.models.user,
        string="Salesperson",
        # index=True,
        ondelete="restrict",
    )
    parent_id: "Partner | None" = Many2one(
        lambda: env.models.partner,
        string="Parent partner",
        index=True,
        ondelete="restrict",
    )
    company_id: "Company | None" = Many2one(
        lambda: env.models.company, string="Company"
    )
    notes: str | None = Text(string="Notes")
    type: str = Selection(
        options=[
            ("lead", "Lead"),
            ("opportunity", "Opportunity"),
        ],
        default="lead",
        string="Type",
    )

    connector_id: "ChatConnector | None" = Many2one(
        relation_table=lambda: env.models.chat_connector,
        string="Connector",
        ondelete="set null",
        description="Коннектор, через который создан лид",
    )

    website: str | None = Char(
        max_length=500,
        string="Website URL",
        description="URL объявления / контекста лида",
    )

    # Контакты (телефоны, email, telegram и т.д.)
    # Внешние аккаунты доступны через contact_ids.external_account_ids
    contact_ids: list["Contact"] = One2many(
        store=False,
        relation_table=lambda: env.models.contact,
        relation_table_field="partner_id",
        description="Контакты",
    )

    async def update(self, payload: "Lead", fields: list[str] | None = None, session=None, depends_jobs=None):
        """Override to sync partner type when stage changes."""
        result = await super().update(payload, fields=fields, session=session, depends_jobs=depends_jobs)

        # Check if stage_id was included in the update
        assigned = payload.assigned_fields() if fields is None else fields
        if "stage_id" in assigned and payload.stage_id is not None:
            try:
                await self._sync_partner_type_for_stage(payload.stage_id)
            except Exception as exc:
                logger.warning("Could not sync partner type on stage change: %s", exc)

        return result

    async def _sync_partner_type_for_stage(self, new_stage) -> None:
        """Update partner.type based on the new stage's partner_action."""
        # Resolve stage id
        stage_id_val = (
            new_stage.id
            if hasattr(new_stage, "id") and new_stage.id
            else new_stage
        )
        if not stage_id_val:
            return

        # Load stage to read partner_action
        stages = await env.models.lead_stage.search(
            filter=[("id", "=", stage_id_val)],
            fields=["id", "partner_action"],
            limit=1,
        )
        if not stages:
            return

        action = getattr(stages[0], "partner_action", "none") or "none"
        if action not in ("set_spam", "set_partner"):
            return

        new_type = "lead" if action == "set_spam" else "partner"

        # Resolve partner reference from self
        partner_ref = self.parent_id
        if not partner_ref:
            # Try loading the lead's parent_id if it wasn't fetched
            leads = await env.models.lead.search(
                filter=[("id", "=", self.id)],
                fields=["id", "parent_id"],
                limit=1,
            )
            if leads:
                partner_ref = leads[0].parent_id

        if not partner_ref:
            return

        partner_id_val = (
            partner_ref.id
            if hasattr(partner_ref, "id") and partner_ref.id
            else partner_ref
        )
        if not partner_id_val:
            return

        # Load partner and update type
        partners = await env.models.partner.search(
            filter=[("id", "=", partner_id_val)],
            fields=["id", "type"],
            limit=1,
        )
        if not partners:
            return

        partner = partners[0]
        await partner.update(env.models.partner(type=new_type))
        logger.info(
            "Lead %s: stage→%s (action=%s), partner %s type→%s",
            self.id,
            stage_id_val,
            action,
            partner_id_val,
            new_type,
        )
