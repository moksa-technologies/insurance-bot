from __future__ import annotations

from typing import Any

from app.infrastructure.tools.assistance_tools import AssistanceTools
from app.infrastructure.tools.customer_tools import CustomerTools
from app.infrastructure.tools.rag_tool import RagTool


class ToolExecutor:
    def __init__(
        self,
        customer_tools: CustomerTools,
        assistance_tools: AssistanceTools,
        rag_tool: RagTool,
    ) -> None:
        self.customer_tools = customer_tools
        self.assistance_tools = assistance_tools
        self.rag_tool = rag_tool

    def run(self, tool_name: str, args: dict[str, Any]) -> Any:
        if tool_name == "customer_create_tool":
            cust_id = args.get("cust_id")
            if cust_id in (None, ""):
                raise ValueError("cust_id is required")
            return self.customer_tools.customer_create_tool(
                cust_id=int(cust_id),
                ani=args.get("ani"),
                name=args["name"],
                email=args.get("email"),
                address=args.get("address"),
                dob=args.get("dob"),
            )
        if tool_name == "customer_profile_tool":
            return self.customer_tools.customer_profile_tool(args["ani"])
        if tool_name == "pull_registered_profile_tool":
            return self.customer_tools.pull_registered_profile_tool(args.get("phone_number"))
        if tool_name == "update_email_tool":
            return self.customer_tools.update_email_tool(args["ani"], args["new_email"])
        if tool_name == "update_address_tool":
            return self.customer_tools.update_address_tool(args["ani"], args["new_address"])
        if tool_name == "change_ani_tool":
            return self.customer_tools.change_ani_tool(args["old_ani"], args["new_ani"])
        if tool_name == "create_claim_tool":
            return self.customer_tools.create_claim_tool(
                ani=args["ani"],
                vehicle_no=args["vehicle_no"],
                incident_date=args["incident_date"],
                incident_time=args.get("incident_time"),
                incident_place=args.get("incident_place"),
                damage_type=args.get("damage_type"),
                damage_description=args.get("damage_description"),
                fir_filed=bool(args.get("fir_filed", False)),
                fir_no=args.get("fir_no"),
            )
        if tool_name == "callback_tool":
            return self.customer_tools.callback_tool(
                cust_id=args.get("cust_id"),
                ani=args.get("ani"),
                phone=args.get("phone"),
                reason=args.get("reason"),
                preferred_from=args.get("preferred_from"),
                preferred_to=args.get("preferred_to"),
                scheduled_at=args.get("scheduled_at"),
                status=args.get("status"),
                priority=int(args.get("priority", 3)),
                assigned_to=args.get("assigned_to"),
            )
        if tool_name == "hospital_tool":
            return self.assistance_tools.hospital_tool(
                area=args.get("area"),
                city=args.get("city"),
                pincode=args.get("pincode"),
                limit=int(args.get("limit", 5)),
            )
        if tool_name == "garage_tool":
            return self.assistance_tools.garage_tool(
                area=args.get("area"),
                city=args.get("city"),
                pincode=args.get("pincode"),
                vehicle_type=args.get("vehicle_type"),
                manufacturer=args.get("manufacturer"),
                limit=int(args.get("limit", 5)),
            )
        if tool_name == "rag_kb_tool":
            return self.rag_tool.rag_kb_tool(
                query_en=args["query_en"],
                top_k=int(args.get("top_k", 4)),
            )
        raise ValueError(f"Unsupported tool: {tool_name}")

    def self_test(self) -> dict[str, bool]:
        checks = {}
        checks["hospital_file_read"] = bool(
            self.assistance_tools.excel_service._hospitals is not None)
        checks["garage_file_read"] = bool(
            self.assistance_tools.excel_service._garages is not None)
        checks["rag_service_ready"] = self.rag_tool.rag_service.records is not None
        return checks
