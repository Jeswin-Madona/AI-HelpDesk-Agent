import os
import warnings
warnings.filterwarnings("ignore")
from typing import Dict, Any, List
from rag.retriever import RAGRetriever
from tools import check_internet_connection, check_disk_space, check_system_health

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    import google.generativeai as legacy_genai

class HelpdeskAgent:
    def __init__(self, retriever: RAGRetriever = None):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        raw_chat_model = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
        self.chat_model_name = raw_chat_model.replace("models/", "")
        self.retriever = retriever or RAGRetriever()

        self.client = None
        if self.api_key and HAS_GENAI:
            self.client = genai.Client(api_key=self.api_key)
        elif self.api_key and not HAS_GENAI:
            legacy_genai.configure(api_key=self.api_key)

    def is_technical_query(self, query: str) -> bool:
        """
        Determines if the question is a technical support issue vs off-topic trivia.
        """
        text = query.lower()

        # Non-technical / general trivia keywords
        off_topic_indicators = [
            "who is the prime minister", "who is the president", "capital of",
            "write a poem", "write a story", "recipe for", "who won", "tell me a joke"
        ]
        for indicator in off_topic_indicators:
            if indicator in text:
                return False

        # Technical keywords
        tech_indicators = [
            "wifi", "wi-fi", "internet", "network", "router", "dns", "ping", "ethernet", "website",
            "laptop", "computer", "pc", "mac", "windows", "cpu", "ram", "memory", "disk", "storage",
            "slow", "freeze", "freezing", "crash", "crashing", "overheat", "fan", "boot",
            "printer", "print", "spooler", "ink", "software", "app", "install", "error", "dll", "update"
        ]
        
        if any(term in text for term in tech_indicators):
            return True

        # Short general greetings or vague questions
        if len(text.split()) <= 4:
            if any(word in text for word in ["hi", "hello", "help", "hey"]):
                return True

        return True

    def process(self, user_query: str) -> Dict[str, Any]:
        """
        Executes the Agent reasoning workflow:
        Query -> Intent Check -> RAG Retrieval -> Tool Decision & Execution -> LLM Synthesis
        """
        trimmed_query = user_query.strip()
        result = {
            "query": trimmed_query,
            "is_technical": True,
            "rag_chunks": [],
            "tool_executed": None,
            "tool_output": None,
            "response": "",
            "logs": []
        }

        if not trimmed_query:
            result["response"] = "Please enter a technical problem to diagnose."
            result["is_technical"] = False
            return result

        result["logs"].append("[AGENT] Understanding the problem...")

        # Step 1: Boundary / Scope Check
        if not self.is_technical_query(trimmed_query):
            result["is_technical"] = False
            result["logs"].append("[AGENT] Non-technical query detected. Politely redirecting.")
            result["response"] = (
                "I'm an AI Helpdesk Agent designed for technical troubleshooting.\n\n"
                "Please describe a technical issue such as:\n"
                "  - WiFi or network connectivity problems\n"
                "  - Computer performance or slow speed\n"
                "  - Software crashes and installation errors\n"
                "  - Printer connection or spooler errors\n"
                "  - Low disk storage space alerts"
            )
            return result

        # Step 2: RAG Knowledge Retrieval
        result["logs"].append("[RAG] Searching technical knowledge base...")
        retrieved_chunks = self.retriever.retrieve(trimmed_query, top_k=3)
        result["rag_chunks"] = retrieved_chunks

        if retrieved_chunks:
            chunk_topics = [f"'{c['topic']}' ({c['category']})" for c in retrieved_chunks]
            result["logs"].append(f"[RAG] Retrieved {len(retrieved_chunks)} relevant knowledge chunk(s): {', '.join(chunk_topics)}")
        else:
            result["logs"].append("[RAG] No high-confidence knowledge chunks retrieved.")

        # Step 3: Tool Selection & Execution
        tool_output = None
        tool_name = None
        query_lower = trimmed_query.lower()

        # Tool Routing Logic
        if any(kw in query_lower for kw in ["wifi", "internet", "network", "dns", "ping", "website", "online", "ethernet"]):
            tool_name = "Internet Diagnostic Tool"
            result["logs"].append(f"[TOOL] Running {tool_name}...")
            tool_output = check_internet_connection()
            result["logs"].append("[OK] Tool execution completed successfully")

        elif any(kw in query_lower for kw in ["storage", "disk", "space", "drive full", "low memory", "low disk"]):
            tool_name = "Disk Diagnostic Tool"
            result["logs"].append(f"[TOOL] Running {tool_name}...")
            tool_output = check_disk_space()
            result["logs"].append("[OK] Tool execution completed successfully")

        elif any(kw in query_lower for kw in ["slow", "performance", "cpu", "ram", "freeze", "freezing", "lag", "overheat", "fan", "resource"]):
            tool_name = "System Health Tool"
            result["logs"].append(f"[TOOL] Running {tool_name}...")
            tool_output = check_system_health()
            result["logs"].append("[OK] Tool execution completed successfully")

        result["tool_executed"] = tool_name
        result["tool_output"] = tool_output

        # Step 4: Handle cases with zero knowledge match
        if not retrieved_chunks and not tool_output:
            result["response"] = (
                "I couldn't find enough relevant information in my technical knowledge base to confidently diagnose this issue.\n\n"
                "Please provide more details about:\n"
                "  • Device model\n"
                "  • Operating system\n"
                "  • Exact error messages or codes"
            )
            return result

        # Step 5: Grounded Response Synthesis (Gemini LLM or Fallback)
        result["logs"].append("[AGENT] Analyzing knowledge + diagnostic results...")

        if self.api_key:
            response_text = self._synthesize_with_gemini(trimmed_query, retrieved_chunks, tool_output)
        else:
            response_text = self._synthesize_offline_fallback(trimmed_query, retrieved_chunks, tool_output)

        result["response"] = response_text
        return result

    def _synthesize_with_gemini(self, query: str, chunks: List[Dict[str, Any]], tool_output: Dict[str, Any]) -> str:
        """
        Uses Gemini API to synthesize grounded response.
        """
        context_blocks = []
        for i, c in enumerate(chunks, 1):
            context_blocks.append(f"Source {i} [{c['category']} - {c['topic']}]:\n{c['content']}")

        knowledge_context = "\n\n---\n\n".join(context_blocks) if context_blocks else "No direct matching knowledge articles."
        tool_context = f"Diagnostic Tool ({tool_output.get('tool_name')}):\nStatus: {tool_output.get('status')}\nDetails: {tool_output.get('details')}" if tool_output else "No diagnostic tool was required for this query."

        system_prompt = f"""You are an expert AI Technical Support Engineer.
Diagnose the user's issue and provide clear, beginner-friendly troubleshooting steps based on the retrieved Knowledge Base and real Diagnostic Tool results.

STRICT INSTRUCTIONS:
1. Base your recommendations on the retrieved knowledge and diagnostic tool data.
2. Structure your output clearly using this EXACT format:

==================================================
DIAGNOSIS
==================================================

Issue:
<1-2 sentence diagnosis>

Possible Causes:
- <Cause 1>
- <Cause 2>

Diagnostic Result:
<Status and summary from diagnostic tool, or "N/A">

Recommended Troubleshooting Steps:

1. <Step 1>
2. <Step 2>
3. <Step 3>
4. <Step 4>

Confidence:
High

Knowledge Used:
• <Topic 1>
• <Topic 2>

--- RETRIEVED KNOWLEDGE BASE ---
{knowledge_context}

--- DIAGNOSTIC TOOL OUTPUT ---
{tool_context}
"""

        try:
            full_prompt = f"{system_prompt}\n\nUSER QUESTION: {query}"
            if HAS_GENAI and self.client:
                res = self.client.models.generate_content(
                    model=self.chat_model_name,
                    contents=full_prompt
                )
                return res.text.strip()
            else:
                model = legacy_genai.GenerativeModel(self.chat_model_name)
                response = model.generate_content(full_prompt)
                return response.text.strip()
        except Exception as e:
            print(f"[Agent Warning] Gemini API call error: {e}. Using deterministic synthesis.")
            return self._synthesize_offline_fallback(query, chunks, tool_output)

    def _synthesize_offline_fallback(self, query: str, chunks: List[Dict[str, Any]], tool_output: Dict[str, Any]) -> str:
        """
        Deterministic fallback response generator when Gemini API key is missing or API errors out.
        """
        primary_chunk = chunks[0] if chunks else {"topic": "General Diagnostics", "category": "Technical", "content": "Follow standard system reboot procedures."}
        
        diag_tool_text = "N/A"
        if tool_output:
            diag_tool_text = f"{tool_output.get('tool_name')}: {tool_output.get('status')} - {tool_output.get('details')}"

        sources_text = "\n".join([f"- {c['topic']} ({c['category']})" for c in chunks]) if chunks else "- General System Troubleshooting Guide"

        return f"""==================================================
DIAGNOSIS
==================================================

Issue:
Potential issue related to {primary_chunk['topic']} ({primary_chunk['category']}).

Possible Causes:
- Hardware configuration or service fault
- Software setting or connectivity interruption

Diagnostic Result:
{diag_tool_text}

Recommended Troubleshooting Steps:

{primary_chunk['content']}

Confidence:
High

Knowledge Used:
{sources_text}"""
