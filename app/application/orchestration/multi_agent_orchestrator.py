from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo
import textwrap
from app.config import Settings
from app.infrastructure.db.chat_history_repository import ChatHistoryRepository
from app.infrastructure.external.transcript_store import TranscriptStore
from app.infrastructure.llm.structured_json import StructuredJSONClient
from app.infrastructure.tools.tool_executor import ToolExecutor
from app.interfaces.api.schemas import ChatRequest, ChatResponse, DataReferences


LOGGER = logging.getLogger(__name__)


ALLOWED_TOOLS = {
    "customer_create_tool",
    "customer_profile_tool",
    "pull_registered_profile_tool",
    "update_email_tool",
    "update_address_tool",
    "change_ani_tool",
    "create_claim_tool",
    "callback_tool",
    "hospital_tool",
    "garage_tool",
    "rag_kb_tool",
}

SYSTEM_PROMPT = textwrap.dedent(r"""
You are Priya, an insurance executive at ** MokSa Insurance**. Always greet the user by their name and warmly introduce yourself at the beginning of every conversation as “Priya from MokSa Insurance.” 
If the user explicitly requests, reintroduce yourself with the same warm, empathetic, and professional tone. Provide accurate, timely, and personalized assistance that reflects excellent customer service standards. 
Respond in the user’s preferred language whenever possible, but ensure all tool inputs are in English. Avoid unnecessary language switching unless explicitly requested by the user.

Actively utilize the tools provided to perform your tasks efficiently and adhere to the structured workflow, rules, and the JSON output format described below.

# Key Responsibilities

1. ** Introduction and Personalization: **

   - Always start the conversation by greeting the customer with their name and introducing yourself as “Priya from MokSa Insurance.”

   - Retrieve the customer’s profile using the `customer_profile_tool` by entering the ANI(Automatic Number Identification). Use the profile data to personalize your responses to the user’s query.

     - If no profile is found:

       - Politely ask if the user is a new or existing customer.

       - Proceed according to their response:

         - **New Customer: **

           - Acknowledge the user’s status as a new customer and confirm how you can assist.

           - For claims-related inquiries, inform them that claim registration is only available to active policyholders. Offer assistance if they wish to purchase a new policy. Clearly inform them that all sales representatives are currently busy and offer to arrange a callback within 30 minutes.

           - Collect the following details, step-by-step, to register the callback and create a new customer profile:

             - `ani`

             - `cust_id` (defined as the last 5 digits of the `ani`)

             - `name`

             - `email`

             - `address`

             - `dob`

           - Once gathered, first call the `customer_create_tool` to create the user profile. Then call the `callback_tool` with the aforementioned details using the following structure:

             ```json

             {

               "tool_name": "callback_tool",

               "args": {

                 "cust_id": "<cust_id>",

                 "ani": "<ani>",

                 "phone": "<ani>",

                 "reason": "<user’s request>",

                 "preferred_from": "9am",

                 "preferred_to": "6pm",

                 "scheduled_at": "<current date/time in Asia/Kolkata time>",

                 "status": "active",

                 "priority": 3,

                 "assigned_to": "all"

               }

             }

             ```

           - Confirm the callback setup and inform the user to expect a call within 30 minutes. Ask if there is anything else they need help with .

         - **Existing Customer: **

           - Ask for their registered Phone Number(if the provided ANI does not match).
           - Retrieve the customer’s profile using the `pull_registered_profile_tool` instead of customer_profile_tool

           - Verify their identity by asking for their date of birth.

           - Upon successful verification, proceed to share the profile data and assist based on their query.



2. ** Accident Assistance: **

   - When users report an accident, express concern and start by inquiring about their safety:

     - **If not safe: **

       - Ask detailed location information step-by-step(area, city, pincode), ensuring all inputs are in English.

       - Use the `hospital_tool` to find nearby hospitals and provide the details to the user.

       - Follow up to confirm if further assistance like contacting authorities or arranging medical help is required.

     - **If safe: **

       - Ask if medical assistance is required:

          - If yes: Execute the hospital search and assistance process above.

          - If no: Ask if roadside assistance is needed.

            - If yes: Collect detailed location information(area, city, pincode) and use the `garage_tool` to find nearby garage details to assist.



3. ** Claim Assistance: **

   - **Existing Claims: **

     - Use the `customer_profile_tool` to retrieve and provide claim status.

   - **Filing a New Claim: **

     - If the user wishes to file a new claim, explain the process in simple and clear terms.

     - Pre-fill data from the profile and collect only the missing information, including:

       - Incident Date
                                
       - Inciden Time
                                
       - Incident location(area, city, pincode)

       - Damage type(infer from the conversation; if unclear, ask directly)

       - Damage description(mandatory)

       - FIR details(ask if an FIR was filed; collect FIR number if yes)
                                
       - vehicle number (if there is only one vehicle in user details just skip this question and use it. but if more hen one is present ask user to select from options which one.)

     - Submit the claim using the `create_claim_tool`.

     - Provide a summary of the process, inform the user about next steps, and confirm the successful submission of the claim.



4. ** Policy and General Queries: **

   - For policy-related inquiries:

   - Identify which policy the user refers to using their profile data. Accurately respond to FAQs or specific queries using the `rag_kb_tool`.

   - For account updates or changes(e.g., email, address, etc.), use tools like `update_email_tool`, `update_address_tool` as necessary.

   - For callback requests, collect required details and register the request using the `callback_tool`.

5 ** Roadside Assistance (RSA) **
   - Check RSA coverage using `customer_profile_tool`.
    - **Eligible Customers**:
    - Collect location **one-by-one**:
        1) City  
        2) Area/Locality  
        3) Pincode  
    - Use `garage_tool` to locate nearby garages and share details.
    - Confirm arrangement with a single yes/no question.
    - Communicate estimated wait time.
   - **Ineligible Customers**:
    - Inform politely RSA isn’t covered.
    - Ask only: *“Would you like me to arrange paid roadside assistance?”*
    - If yes → collect location one-by-one as above.

6. ** Follow-Up and Closing: **

   - Confirm that all the user’s questions have been addressed before closing the interaction.

   - End the conversation in a polite and professional manner, expressing gratitude(e.g., “Thank you for choosing MokSa Insurance! Have a wonderful day.”).



# Tool Usage Rules



- Utilize only the following tools: `customer_create_tool`, `customer_profile_tool`, `pull_registered_profile_tool`, `update_email_tool`, `update_address_tool`, `change_ani_tool`, `create_claim_tool`, `callback_tool`, `hospital_tool`, `garage_tool`, `rag_kb_tool`.

- All tool inputs must be in **English ** regardless of the user's preference or query language.

- Never modify immutable fields like ANI, pincode, policy numbers, emails, etc.  

- Use a single tool call per turn. Respond to the result from the current tool call before invoking another.



# Output Format



Respond strictly in the following JSON format:



```json

{

  "intent": "<concise intent label in snake_case>",

  "language": "<ISO-like language code, e.g., en, hi, te, ta>",

  "response": "<final user-facing string response, or null>",

  "follow_up_needed": "<boolean: either true or false>",

  "follow_up_query": "<string: follow-up question, or null>",

  "tool_call": "<null OR structured tool call: {'tool_name': '<tool_name>', 'args': {...}}>"

}

```



# Notes

- current sysyem date time is now_ist

- Always prioritize user safety in accident-related scenarios.  

- For callback requests, set `scheduled_at` to the current time in Asia/Kolkata time.  

- Ensure all responses and queries are clear, friendly, and professional.""").strip()


class MultiAgentOrchestrator:
    def __init__(
        self,
        settings: Settings,
        tool_executor: ToolExecutor,
        history_repo: ChatHistoryRepository,
        llm_client: Any,
        model: str,
        transcript_store: TranscriptStore | None = None,
    ) -> None:
        self.settings = settings
        self.tool_executor = tool_executor
        self.history_repo = history_repo
        self.transcript_store = transcript_store
        self.structured = StructuredJSONClient(
            llm_client=llm_client, model=model, max_retries=2)

    async def close(self) -> None:
        return

    @staticmethod
    def _coerce_bool(value: Any) -> bool | None:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            if value in (0, 1):
                return bool(value)
            return None
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "yes", "1"}:
                return True
            if normalized in {"false", "no", "0"}:
                return False
        return None

    @staticmethod
    def _normalize_tool_name(tool_name: str) -> str:
        normalized = tool_name.strip().lower()
        aliases = {
            "get_customer_profile_by_ani": "customer_profile_tool",
            "pull_registered_profile": "pull_registered_profile_tool",
            "customer_create": "customer_create_tool",
            "update_customer_email_by_ani": "update_email_tool",
            "update_customer_address_by_ani": "update_address_tool",
            "change_customer_ani": "change_ani_tool",
            "create_claim_by_ani": "create_claim_tool",
            "callback_create": "callback_tool",
            "faq_rag_tool": "rag_kb_tool",
            "rag_tool": "rag_kb_tool",
            "hospital_search_tool": "hospital_tool",
            "garage_search_tool": "garage_tool",
        }
        return aliases.get(normalized, normalized)

    @classmethod
    def _validate_agent_payload(cls, payload: dict[str, Any]) -> tuple[bool, dict[str, Any] | str]:
        if not isinstance(payload, dict):
            return False, "payload_not_dict"

        intent = payload.get("intent")
        if not isinstance(intent, str) or not intent.strip():
            return False, "invalid_intent"
        intent = intent.strip().lower()

        language = str(payload.get("language", "en")).strip().lower() or "en"

        response = payload.get("response")
        if response is not None and not isinstance(response, str):
            response = str(response)
        response = response.strip() if isinstance(response, str) else None

        follow_up_needed = cls._coerce_bool(
            payload.get("follow_up_needed", False))
        if follow_up_needed is None:
            return False, "invalid_follow_up_needed"

        follow_up_query = payload.get("follow_up_query")
        if follow_up_query is not None and not isinstance(follow_up_query, str):
            follow_up_query = str(follow_up_query)
        follow_up_query = follow_up_query.strip() if isinstance(
            follow_up_query, str) else None
        if follow_up_query == "":
            follow_up_query = None

        tool_call = payload.get("tool_call")
        normalized_tool_call: dict[str, Any] | None = None
        if isinstance(tool_call, str):
            raw_tool_call = tool_call.strip()
            if raw_tool_call and raw_tool_call.lower() != "null":
                try:
                    tool_call = json.loads(raw_tool_call)
                except json.JSONDecodeError:
                    tool_call = StructuredJSONClient.extract_json(
                        raw_tool_call)
            else:
                tool_call = None

        if tool_call is not None:
            if not isinstance(tool_call, dict):
                return False, "invalid_tool_call"
            tool_name = cls._normalize_tool_name(
                str(tool_call.get("tool_name", "")))
            args = tool_call.get("args", {})
            if isinstance(args, str):
                parsed_args = StructuredJSONClient.extract_json(args)
                args = parsed_args if isinstance(parsed_args, dict) else {}
            if not isinstance(args, dict):
                return False, "invalid_tool_args"
            if tool_name in ALLOWED_TOOLS:
                normalized_tool_call = {"tool_name": tool_name, "args": args}

        if follow_up_query and not follow_up_needed:
            follow_up_needed = True

        if normalized_tool_call is None and response is None:
            if follow_up_needed and follow_up_query:
                response = follow_up_query
            else:
                return False, "missing_response_or_tool_call"

        normalized = {
            "intent": intent,
            "language": language,
            "response": response,
            "follow_up_needed": follow_up_needed,
            "follow_up_query": follow_up_query,
            "tool_call": normalized_tool_call,
        }
        return True, normalized

    def _agent_turn(self, payload: dict[str, Any]) -> dict[str, Any]:
        fallback = {
            "intent": "unknown",
            "language": "en",
            "response": "I am here to help.",
            "follow_up_needed": False,
            "follow_up_query": None,
            "tool_call": None,
        }
        now_ist = datetime.now(ZoneInfo("Asia/Kolkata")
                               ).strftime("%Y-%m-%d %H:%M:%S")
        SYSTEM_PROMPT_TEMPLATE = SYSTEM_PROMPT.replace("now_ist", now_ist)
        return self.structured.call_json(
            system_prompt=SYSTEM_PROMPT_TEMPLATE,
            payload=payload,
            validator=self._validate_agent_payload,
            fallback=fallback,
        )

    @staticmethod
    def _opt_str(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _prepare_tool_args(self, tool_name: str, args: dict[str, Any], ani: str) -> dict[str, Any]:
        if tool_name == "customer_create_tool":
            cust_id_raw = args.get("cust_id")
            if cust_id_raw in (None, ""):
                cust_id = None
            else:
                try:
                    cust_id = int(cust_id_raw)
                except (TypeError, ValueError):
                    cust_id = None
            return {
                "cust_id": cust_id,
                "ani": self._opt_str(args.get("ani")) or ani,
                "name": self._opt_str(args.get("name")) or "",
                "email": self._opt_str(args.get("email")),
                "address": self._opt_str(args.get("address")),
                "dob": self._opt_str(args.get("dob")),
            }

        if tool_name == "customer_profile_tool":
            return {
                "ani": ani or self._opt_str(args.get("phone_number")) or self._opt_str(args.get("registered_phone")) or self._opt_str(args.get("ani"))
            }

        if tool_name == "pull_registered_profile_tool":
            return {
                "phone_number": self._opt_str(args.get("phone_number")) or self._opt_str(args.get("registered_phone")) or self._opt_str(args.get("ani"))
            }

        if tool_name == "update_email_tool":
            return {
                "ani": ani,
                "new_email": self._opt_str(args.get("new_email")) or "",
            }

        if tool_name == "update_address_tool":
            return {
                "ani": ani,
                "new_address": self._opt_str(args.get("new_address")) or "",
            }

        if tool_name == "change_ani_tool":
            return {
                "old_ani": self._opt_str(args.get("old_ani")) or ani,
                "new_ani": self._opt_str(args.get("new_ani")) or "",
            }

        if tool_name == "create_claim_tool":
            return {
                "ani": ani,
                "vehicle_no": self._opt_str(args.get("vehicle_no")) or "",
                "incident_date": self._opt_str(args.get("incident_date")) or "",
                "incident_time": self._opt_str(args.get("incident_time")),
                "incident_place": self._opt_str(args.get("incident_place")),
                "damage_type": self._opt_str(args.get("damage_type")),
                "damage_description": self._opt_str(args.get("damage_description")),
                "fir_filed": bool(args.get("fir_filed", False)),
                "fir_no": self._opt_str(args.get("fir_no")),
            }

        if tool_name == "callback_tool":
            cust_id_raw = args.get("cust_id")
            if cust_id_raw in (None, ""):
                cust_id = None
            else:
                try:
                    cust_id = int(cust_id_raw)
                except (TypeError, ValueError):
                    cust_id = None
            priority_raw = args.get("priority", 3)
            if priority_raw in (None, ""):
                priority = 3
            else:
                try:
                    priority = int(priority_raw)
                except (TypeError, ValueError):
                    priority = 3
            return {
                "cust_id": cust_id,
                "ani": self._opt_str(args.get("ani")) or ani,
                "phone": self._opt_str(args.get("phone")),
                "reason": self._opt_str(args.get("reason")),
                "preferred_from": self._opt_str(args.get("preferred_from")),
                "preferred_to": self._opt_str(args.get("preferred_to")),
                "scheduled_at": self._opt_str(args.get("scheduled_at")),
                "status": self._opt_str(args.get("status")),
                "priority": priority,
                "assigned_to": self._opt_str(args.get("assigned_to")),
            }

        if tool_name == "hospital_tool":
            return {
                "area": self._opt_str(args.get("area")),
                "city": self._opt_str(args.get("city")),
                "pincode": self._opt_str(args.get("pincode")),
                "limit": int(args.get("limit", 1)),
            }

        if tool_name == "garage_tool":
            return {
                "area": self._opt_str(args.get("area")),
                "city": self._opt_str(args.get("city")),
                "pincode": self._opt_str(args.get("pincode")),
                "vehicle_type": self._opt_str(args.get("vehicle_type")),
                "manufacturer": self._opt_str(args.get("manufacturer")),
                "limit": int(args.get("limit", 1)),
            }

        if tool_name == "rag_kb_tool":
            return {
                "query_en": self._opt_str(args.get("query_en")) or "",
                "top_k": int(args.get("top_k", self.settings.rag_top_k)),
            }

        return args

    @staticmethod
    def _summarize_recent_chat(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ordered = list(reversed(rows))
        return [
            {
                "user": row.get("input_message", ""),
                "assistant": row.get("response_message", ""),
                "intent": row.get("intent", ""),
                "language": row.get("language", "en"),
            }
            for row in ordered
        ]

    @staticmethod
    def _normalize_external_source(values: list[str]) -> str | list[str] | None:
        unique = sorted({v for v in values if v})
        if not unique:
            return None
        if len(unique) == 1:
            return unique[0]
        return unique

    def _apply_tool_reference(
        self,
        tool_name: str,
        result: Any,
        db_function: str | None,
        external_sources: list[str],
    ) -> tuple[str | None, list[str]]:
        if tool_name == "customer_profile_tool":
            return "get_customer_profile_by_ani", external_sources
        if tool_name == "pull_registered_profile_tool":
            return "pull_customer_profile_by_ani", external_sources
        if tool_name == "customer_create_tool":
            return "customer_create", external_sources
        if tool_name == "update_email_tool":
            return "update_customer_email_by_ani", external_sources
        if tool_name == "update_address_tool":
            return "update_customer_address_by_ani", external_sources
        if tool_name == "change_ani_tool":
            return "change_customer_ani", external_sources
        if tool_name == "create_claim_tool":
            return "create_claim_by_ani", external_sources
        if tool_name == "callback_tool":
            return "callback_create", external_sources
        if tool_name == "hospital_tool":
            return db_function, [*external_sources, "hospitals.xlsx"]
        if tool_name == "garage_tool":
            return db_function, [*external_sources, "garages.xlsx"]
        if tool_name == "rag_kb_tool":
            if isinstance(result, list):
                files = [str(x.get("source_file", ""))
                         for x in result if isinstance(x, dict)]
                files = [f for f in files if f]
                if files:
                    return db_function, [*external_sources, *files]
            return db_function, [*external_sources, "pdf_kb"]
        return db_function, external_sources

    async def handle_chat(self, request: ChatRequest) -> ChatResponse:
        session_uuid = request.session_uuid or ""
        LOGGER.info(
            "chat_turn:start ani=%s session=%s message=%s",
            request.ani,
            session_uuid,
            request.input_message,
        )
        recent_chat = self.history_repo.recent_messages(
            request.ani, session_uuid, limit=8)
        chat_context = self._summarize_recent_chat(recent_chat)

        profile = self.tool_executor.run(
            "customer_profile_tool", {"ani": request.ani})
        profile_obj = profile if isinstance(profile, dict) else None
        customer_name = (profile_obj or {}).get("name") or "Customer"

        db_function: str | None = "get_customer_profile_by_ani"
        external_sources: list[str] = []

        tool_trace: list[dict[str, Any]] = []
        final_payload: dict[str, Any] | None = None

        for turn_idx in range(4):
            payload = {
                "ani": request.ani,
                "session_uuid": session_uuid,
                "user_message": request.input_message,
                "customer_name": customer_name,
                "customer_profile": profile_obj,
                "has_prior_messages": bool(chat_context),
                "recent_chat": chat_context,
                "tool_results": tool_trace,
            }
            decision = self._agent_turn(payload)
            final_payload = decision
            LOGGER.info(
                "chat_turn:llm_decision step=%s intent=%s follow_up_needed=%s tool_call=%s",
                turn_idx + 1,
                decision.get("intent"),
                decision.get("follow_up_needed"),
                (decision.get("tool_call") or {}).get("tool_name"),
            )
            if LOGGER.isEnabledFor(logging.DEBUG):
                LOGGER.debug(
                    "chat_turn:llm_payload step=%s payload=%s", turn_idx + 1, decision)

            tool_call = decision.get("tool_call")
            if not tool_call:
                break

            tool_name = str(tool_call["tool_name"])
            raw_args = tool_call.get("args", {})
            args = self._prepare_tool_args(tool_name, raw_args, request.ani)
            LOGGER.info("chat_turn:tool_call tool=%s args=%s", tool_name, args)

            try:
                result = self.tool_executor.run(tool_name, args)
            except Exception as exc:
                result = {
                    "ok": False, "message": f"Tool execution failed: {type(exc).__name__}"}
                LOGGER.exception("chat_turn:tool_error tool=%s", tool_name)
            else:
                LOGGER.info("chat_turn:tool_result tool=%s result_type=%s",
                            tool_name, type(result).__name__)
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug(
                        "chat_turn:tool_result_payload tool=%s result=%s", tool_name, result)

            db_function, external_sources = self._apply_tool_reference(
                tool_name=tool_name,
                result=result,
                db_function=db_function,
                external_sources=external_sources,
            )

            tool_trace.append(
                {
                    "tool_name": tool_name,
                    "args": args,
                    "result": result,
                }
            )

        if final_payload is None:
            final_payload = {
                "intent": "unknown",
                "language": "en",
                "response": "I am here to help.",
                "follow_up_needed": False,
                "follow_up_query": None,
                "tool_call": None,
            }

        intent = str(final_payload.get("intent", "unknown")
                     ).strip().lower() or "unknown"

        language = str(final_payload.get("language", "en")
                       ).strip().lower() or "en"
        follow_up_needed = bool(final_payload.get("follow_up_needed", False))
        follow_up_query = final_payload.get("follow_up_query")
        if follow_up_query is not None:
            follow_up_query = str(follow_up_query).strip() or None

        response_text = str(final_payload.get("response") or "").strip()
        if not response_text and follow_up_query:
            response_text = follow_up_query
        if not response_text:
            response_text = "I am here to help."

        references = DataReferences(
            database_function=db_function,
            external_source=self._normalize_external_source(external_sources),
        )

        response = ChatResponse(
            session_uuid=session_uuid,
            language=language,
            response=response_text,
            follow_up_needed=follow_up_needed,
            follow_up_query=follow_up_query,
            intent=intent,
            data_references=references,
        )

        self.history_repo.add_chat_record(
            ani=request.ani,
            session_uuid=session_uuid,
            input_message=request.input_message,
            response_message=response.response,
            language=response.language,
            intent=response.intent,
            data_references=response.data_references.model_dump(),
        )

        if self.transcript_store is not None:
            self.transcript_store.append_turn(
                ani=request.ani,
                session_uuid=session_uuid,
                turn={
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "ani": request.ani,
                    "session_uuid": session_uuid,
                    "input_message": request.input_message,
                    "response": response.model_dump(),
                    "llm_final_payload": final_payload,
                    "tool_trace": tool_trace,
                    "data_references": response.data_references.model_dump(),
                },
            )

        LOGGER.info(
            "chat_turn:end ani=%s session=%s intent=%s language=%s follow_up_needed=%s",
            request.ani,
            session_uuid,
            response.intent,
            response.language,
            response.follow_up_needed,
        )
        return response
