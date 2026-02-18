from __future__ import annotations

from typing import Any

from app.infrastructure.db.function_gateway import CustomerFunctionGateway


class CustomerTools:
    def __init__(self, gateway: CustomerFunctionGateway) -> None:
        self.gateway = gateway

    def customer_create_tool(
        self,
        cust_id: int,
        ani: str | None,
        name: str,
        email: str | None,
        address: str | None,
        dob: str | None,
    ) -> dict[str, Any]:
        return self.gateway.customer_create(
            cust_id=cust_id,
            ani=ani,
            name=name,
            email=email,
            address=address,
            dob=dob,
        )

    def customer_profile_tool(self, ani: str) -> dict[str, Any] | None:
        return self.gateway.get_customer_profile_by_ani(ani)

    def pull_registered_profile_tool(self, Phone_number: str) -> dict[str, Any] | None:
        return self.gateway.pull_customer_profile_by_ani(Phone_number)

    def update_email_tool(self, ani: str, new_email: str) -> dict[str, Any]:
        return self.gateway.update_customer_email_by_ani(ani, new_email)

    def update_address_tool(self, ani: str, new_address: str) -> dict[str, Any]:
        return self.gateway.update_customer_address_by_ani(ani, new_address)

    def change_ani_tool(self, old_ani: str, new_ani: str) -> dict[str, Any]:
        return self.gateway.change_customer_ani(old_ani, new_ani)

    def create_claim_tool(
        self,
        ani: str,
        vehicle_no: str,
        incident_date: str,
        incident_time: str | None,
        incident_place: str | None,
        damage_type: str | None,
        damage_description: str | None,
        fir_filed: bool,
        fir_no: str | None,
    ) -> dict[str, Any]:
        return self.gateway.create_claim_by_ani(
            ani=ani,
            vehicle_no=vehicle_no,
            incident_date=incident_date,
            incident_time=incident_time,
            incident_place=incident_place,
            damage_type=damage_type,
            damage_description=damage_description,
            fir_filed=fir_filed,
            fir_no=fir_no,
        )

    def callback_tool(
        self,
        cust_id: int | None = None,
        ani: str | None = None,
        phone: str | None = None,
        reason: str | None = None,
        preferred_from: str | None = None,
        preferred_to: str | None = None,
        scheduled_at: str | None = None,
        status: str | None = None,
        priority: int = 3,
        assigned_to: str | None = None,
    ) -> dict[str, Any]:
        return self.gateway.callback_create(
            cust_id=cust_id,
            ani=ani,
            phone=phone,
            reason=reason,
            preferred_from=preferred_from,
            preferred_to=preferred_to,
            scheduled_at=scheduled_at,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
        )
