"""
Layra AI Brain — Gemini-Powered Intelligence
=====================================================
The core intelligence layer using Google Gemini with function calling.
Understands user intent, routes to appropriate skill modules,
and generates natural conversational responses.
"""

import json
import logging
from typing import Callable
from google import genai
from google.genai import types

logger = logging.getLogger("layra.brain")


# ============================================
# Tool/Function Definitions for Gemini
# ============================================

LAYRA_TOOLS = [
    # --- System Control ---
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="open_application",
            description="Open a macOS application by name. Examples: Safari, Chrome, Finder, Terminal, Notes, Calendar, Music, Spotify, VS Code, WhatsApp, Telegram, Slack",
            parameters=types.Schema(
                type="OBJECT",
                properties={"app_name": types.Schema(type="STRING", description="Name of the application to open")},
                required=["app_name"]
            )
        ),
        types.FunctionDeclaration(
            name="close_application",
            description="Close/quit a running macOS application",
            parameters=types.Schema(
                type="OBJECT",
                properties={"app_name": types.Schema(type="STRING", description="Name of the application to close")},
                required=["app_name"]
            )
        ),
        types.FunctionDeclaration(
            name="set_volume",
            description="Set the system volume level (0-100) or mute/unmute",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "level": types.Schema(type="INTEGER", description="Volume level 0-100. Use -1 to mute, -2 to unmute"),
                },
                required=["level"]
            )
        ),
        types.FunctionDeclaration(
            name="set_brightness",
            description="Set the screen brightness level (0.0 to 1.0)",
            parameters=types.Schema(
                type="OBJECT",
                properties={"level": types.Schema(type="NUMBER", description="Brightness level from 0.0 (dark) to 1.0 (full)")},
                required=["level"]
            )
        ),
        types.FunctionDeclaration(
            name="toggle_wifi",
            description="Turn Wi-Fi on or off",
            parameters=types.Schema(
                type="OBJECT",
                properties={"enable": types.Schema(type="BOOLEAN", description="True to enable, False to disable")},
                required=["enable"]
            )
        ),
        types.FunctionDeclaration(
            name="toggle_bluetooth",
            description="Turn Bluetooth on or off",
            parameters=types.Schema(
                type="OBJECT",
                properties={"enable": types.Schema(type="BOOLEAN", description="True to enable, False to disable")},
                required=["enable"]
            )
        ),
        types.FunctionDeclaration(
            name="toggle_dark_mode",
            description="Switch between dark mode and light mode on macOS",
            parameters=types.Schema(
                type="OBJECT",
                properties={"enable": types.Schema(type="BOOLEAN", description="True for dark mode, False for light mode")},
                required=["enable"]
            )
        ),
        types.FunctionDeclaration(
            name="lock_screen",
            description="Lock the Mac screen",
            parameters=types.Schema(type="OBJECT", properties={})
        ),
        types.FunctionDeclaration(
            name="sleep_mac",
            description="Put the Mac to sleep",
            parameters=types.Schema(type="OBJECT", properties={})
        ),
        types.FunctionDeclaration(
            name="take_screenshot",
            description="Take a screenshot of the entire screen or a window",
            parameters=types.Schema(
                type="OBJECT",
                properties={"filename": types.Schema(type="STRING", description="Optional filename for screenshot")},
            )
        ),
        types.FunctionDeclaration(
            name="get_system_info",
            description="Get system information: battery level, storage, RAM usage, CPU usage",
            parameters=types.Schema(type="OBJECT", properties={})
        ),
        types.FunctionDeclaration(
            name="empty_trash",
            description="Empty the macOS Trash/Bin",
            parameters=types.Schema(type="OBJECT", properties={})
        ),
        types.FunctionDeclaration(
            name="show_notification",
            description="Show a macOS notification with title and message",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "title": types.Schema(type="STRING", description="Notification title"),
                    "message": types.Schema(type="STRING", description="Notification body text"),
                },
                required=["title", "message"]
            )
        ),
        types.FunctionDeclaration(
            name="control_music",
            description="Control music playback. Actions: play (resume), pause, next (skip), previous, play_song (search and play a specific song by name), play_liked (play user's Liked Songs playlist), play_playlist (play a named playlist). Examples: 'play my liked songs' → action=play_liked. 'play chill playlist' → action=play_playlist, playlist_name=chill. 'play Shape of You' → action=play_song, song_name=Shape of You.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "action": types.Schema(type="STRING", description="Action: play, pause, next, previous, play_song, play_liked, play_playlist"),
                    "song_name": types.Schema(type="STRING", description="Song name to search and play (only for play_song action)"),
                    "playlist_name": types.Schema(type="STRING", description="Playlist name to search and play (only for play_playlist action)"),
                },
                required=["action"]
            )
        ),
        types.FunctionDeclaration(
            name="run_shell_command",
            description="Run a shell/terminal command on macOS and return the output. Use for system operations, file management, etc.",
            parameters=types.Schema(
                type="OBJECT",
                properties={"command": types.Schema(type="STRING", description="The shell command to execute")},
                required=["command"]
            )
        ),
    ]),

    # --- Browser ---
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="open_url",
            description="Open a URL in the default web browser",
            parameters=types.Schema(
                type="OBJECT",
                properties={"url": types.Schema(type="STRING", description="Full URL to open")},
                required=["url"]
            )
        ),
        types.FunctionDeclaration(
            name="search_web",
            description="Search the web using Google/DuckDuckGo and return results",
            parameters=types.Schema(
                type="OBJECT",
                properties={"query": types.Schema(type="STRING", description="Search query text")},
                required=["query"]
            )
        ),
        types.FunctionDeclaration(
            name="search_youtube",
            description="Search YouTube for videos and optionally play one",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "query": types.Schema(type="STRING", description="YouTube search query"),
                    "play_first": types.Schema(type="BOOLEAN", description="If true, play the first result directly"),
                },
                required=["query"]
            )
        ),
    ]),

    # --- Research ---
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="research_topic",
            description="Research a topic thoroughly by searching the web, gathering information from multiple sources, and providing a comprehensive summary",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "topic": types.Schema(type="STRING", description="The topic to research"),
                    "depth": types.Schema(type="STRING", description="Research depth: quick (1-2 sources) or deep (5+ sources)"),
                },
                required=["topic"]
            )
        ),
        types.FunctionDeclaration(
            name="get_weather",
            description="Get current weather information for a city",
            parameters=types.Schema(
                type="OBJECT",
                properties={"city": types.Schema(type="STRING", description="City name")},
                required=["city"]
            )
        ),
        types.FunctionDeclaration(
            name="get_news",
            description="Get latest news headlines, optionally filtered by topic",
            parameters=types.Schema(
                type="OBJECT",
                properties={"topic": types.Schema(type="STRING", description="News topic filter (optional)")},
            )
        ),
    ]),

    # --- Email ---
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="check_emails",
            description="Check and read unread emails from Gmail, providing a summary",
            parameters=types.Schema(
                type="OBJECT",
                properties={"count": types.Schema(type="INTEGER", description="Number of emails to check (default 5)")},
            )
        ),
        types.FunctionDeclaration(
            name="send_email",
            description="Compose and send an email",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "to": types.Schema(type="STRING", description="Recipient email address"),
                    "subject": types.Schema(type="STRING", description="Email subject line"),
                    "body": types.Schema(type="STRING", description="Email body text"),
                },
                required=["to", "subject", "body"]
            )
        ),
        types.FunctionDeclaration(
            name="search_emails",
            description="Search emails by keyword, sender, or subject",
            parameters=types.Schema(
                type="OBJECT",
                properties={"query": types.Schema(type="STRING", description="Search query for emails")},
                required=["query"]
            )
        ),
    ]),

    # --- Social Media ---
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="open_social_media",
            description="Open a social media platform in the browser (Instagram, Twitter/X, LinkedIn, WhatsApp Web, Facebook, Reddit)",
            parameters=types.Schema(
                type="OBJECT",
                properties={"platform": types.Schema(type="STRING", description="Platform name: instagram, twitter, linkedin, whatsapp, facebook, reddit")},
                required=["platform"]
            )
        ),
    ]),

    # --- Project Management ---
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="create_file",
            description="Create a new file with specified content",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "file_path": types.Schema(type="STRING", description="Full path for the new file"),
                    "content": types.Schema(type="STRING", description="File content to write"),
                },
                required=["file_path", "content"]
            )
        ),
        types.FunctionDeclaration(
            name="read_file",
            description="Read and return the contents of a file",
            parameters=types.Schema(
                type="OBJECT",
                properties={"file_path": types.Schema(type="STRING", description="Full path to the file to read")},
                required=["file_path"]
            )
        ),
        types.FunctionDeclaration(
            name="git_operation",
            description="Perform git operations: status, add, commit, push, pull, log",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "operation": types.Schema(type="STRING", description="Git operation: status, add, commit, push, pull, log, diff"),
                    "args": types.Schema(type="STRING", description="Additional arguments (e.g., commit message, file path)"),
                },
                required=["operation"]
            )
        ),
    ]),

    # --- Utilities ---
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="set_timer",
            description="Set a timer/alarm for a specified duration",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "minutes": types.Schema(type="NUMBER", description="Timer duration in minutes"),
                    "label": types.Schema(type="STRING", description="Timer label/description"),
                },
                required=["minutes"]
            )
        ),
        types.FunctionDeclaration(
            name="take_note",
            description="Save a note or reminder for later",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "title": types.Schema(type="STRING", description="Note title"),
                    "content": types.Schema(type="STRING", description="Note content"),
                },
                required=["content"]
            )
        ),
        types.FunctionDeclaration(
            name="get_date_time",
            description="Get the current date and time",
            parameters=types.Schema(type="OBJECT", properties={})
        ),
        types.FunctionDeclaration(
            name="calculate",
            description="Perform mathematical calculations",
            parameters=types.Schema(
                type="OBJECT",
                properties={"expression": types.Schema(type="STRING", description="Mathematical expression to evaluate")},
                required=["expression"]
            )
        ),
        types.FunctionDeclaration(
            name="remember_user_fact",
            description="Remember a preference, habit, or personal fact about the user for future interactions (e.g. key='favorite_singer', value='Arijit Singh')",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "key": types.Schema(type="STRING", description="Short identifier for the fact/preference (e.g., favorite_singer, speech_volume, bedtime, working_style)"),
                    "value": types.Schema(type="STRING", description="Details of the fact or habit to remember"),
                },
                required=["key", "value"]
            )
        ),
        types.FunctionDeclaration(
            name="get_user_facts",
            description="Retrieve all remembered facts, habits, and preferences about the user",
            parameters=types.Schema(type="OBJECT", properties={})
        ),
    ]),
]


class GeminiBrain:
    """
    The AI brain of Layra powered by Google Gemini.
    Handles intent recognition, function calling, and response generation.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash",
                 personality: str = "", skill_handlers: dict = None, memory=None):
        """
        Args:
            api_key: Google Gemini API key
            model_name: Gemini model to use
            personality: System prompt / personality description
            skill_handlers: Dict mapping function names to callable handlers
            memory: Reference to Layra Memory instance for continuous learning
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.personality = personality
        self.skill_handlers = skill_handlers or {}
        self.conversation_history = []
        self.max_history = 20
        self.memory = memory

        if self.memory:
            self.register_handler("remember_user_fact", self.memory.remember_fact)
            self.register_handler("get_user_facts", self.memory.get_all_facts)

    def register_handler(self, function_name: str, handler: Callable):
        """Register a handler function for a tool."""
        self.skill_handlers[function_name] = handler

    def register_handlers(self, handlers: dict):
        """Register multiple handlers at once."""
        self.skill_handlers.update(handlers)

    def _trim_history(self):
        """Keep conversation history within limits."""
        if len(self.conversation_history) > self.max_history * 2:
            # Keep the first system message and last N exchanges
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]

    def process(self, user_input: str) -> str:
        """
        Process user input through Gemini with function calling.
        
        Args:
            user_input: The user's voice command/text
            
        Returns:
            Layra's response text
        """
        logger.info(f"🧠 Processing: '{user_input}'")

    def _sanitize_history(self):
        """Sanitize conversation history so no empty or invalid parts/contents exist."""
        clean_history = []
        for content in self.conversation_history:
            if not hasattr(content, 'parts') or not content.parts:
                continue
            valid_parts = []
            for p in content.parts:
                if getattr(p, 'text', None):
                    valid_parts.append(p)
                elif getattr(p, 'function_call', None):
                    valid_parts.append(p)
                elif getattr(p, 'function_response', None):
                    valid_parts.append(p)
            if valid_parts:
                content.parts = valid_parts
                clean_history.append(content)
        self.conversation_history = clean_history

    def process(self, user_input: str) -> str:
        """
        Process a user input string through Gemini.
        Returns:
            Layra's response text
        """
        logger.info(f"🧠 Processing: '{user_input}'")

        # Add user message to history
        self.conversation_history.append(
            types.Content(role="user", parts=[types.Part(text=user_input)])
        )
        self._trim_history()
        self._sanitize_history()

        # Build dynamic system instruction with learned memory
        system_instruction = self.personality
        if self.memory:
            mem_context = self.memory.get_memory_context()
            if mem_context:
                system_instruction += (
                    "\n\n=== LEARNED USER HABITS & PREFERENCES ===\n"
                    f"{mem_context}\n"
                    "\nINSTRUCTIONS ON LEARNING & ADAPTATION:\n"
                    "1. Use this learned context to personalize your responses, remember user habits, and adapt to the user's workflow.\n"
                    "2. If the user tells you a new fact, preference, habit, or instruction (e.g. 'I speak quietly', 'my favorite singer is Arijit', 'I prefer Spotify'), ALWAYS call the `remember_user_fact` tool to save it permanently.\n"
                    "3. Continuously improve and adapt your behavior based on user feedback.\n"
                )

        fallback_models = [self.model_name, "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-latest"]
        fallback_models = list(dict.fromkeys(fallback_models))

        last_exception = None
        for model in fallback_models:
            try:
                # Call Gemini with tools
                response = self.client.models.generate_content(
                    model=model,
                    contents=self.conversation_history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=LAYRA_TOOLS,
                        temperature=0.7,
                        max_output_tokens=2048,
                    )
                )

                # Process the response — handle function calls
                res = self._handle_response(response)
                return res if res else "Done, Sir."

            except Exception as e:
                last_exception = e
                logger.warning(f"Gemini API model '{model}' failed: {e}. Retrying with fallback model...")

        logger.error(f"Gemini API error across all fallback models: {last_exception}")
        # Remove un-replied user message from history so future calls don't get corrupted
        if self.conversation_history and self.conversation_history[-1].role == "user":
            self.conversation_history.pop()

        error_msg = f"Sorry Sir, I encountered an error: {str(last_exception)[:100]}"
        return error_msg

    def _handle_response(self, response) -> str:
        """Handle Gemini response, executing any function calls."""
        if not response or not response.candidates:
            return "I didn't get a response. Could you try again, Sir?"

        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            return "I'm operational, Sir. How can I help you?"

        parts = candidate.content.parts
        
        # Check for function calls
        function_calls = [p for p in parts if getattr(p, 'function_call', None)]
        text_parts = [p for p in parts if getattr(p, 'text', None)]

        if function_calls:
            # Execute all function calls
            results = []
            for fc_part in function_calls:
                fc = fc_part.function_call
                func_name = fc.name
                func_args = dict(fc.args) if fc.args else {}

                logger.info(f"⚡ Calling function: {func_name}({func_args})")

                # Execute the handler
                if func_name in self.skill_handlers:
                    try:
                        result = self.skill_handlers[func_name](**func_args)
                        results.append((func_name, result))
                        logger.info(f"✅ {func_name} returned: {str(result)[:200]}")
                    except Exception as e:
                        error_result = f"Error executing {func_name}: {str(e)}"
                        results.append((func_name, error_result))
                        logger.error(error_result)
                else:
                    results.append((func_name, f"Function {func_name} not implemented yet"))
                    logger.warning(f"⚠️ No handler for function: {func_name}")

            # Add model's function call to history
            self.conversation_history.append(candidate.content)

            # Send function results back to Gemini for final response
            function_response_parts = []
            for func_name, result in results:
                function_response_parts.append(
                    types.Part(function_response=types.FunctionResponse(
                        name=func_name,
                        response={"result": str(result) if result is not None else "Success"}
                    ))
                )

            self.conversation_history.append(
                types.Content(role="user", parts=function_response_parts)
            )

            # Get final natural language response
            try:
                self._sanitize_history()
                final_response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=self.conversation_history,
                    config=types.GenerateContentConfig(
                        system_instruction=self.personality,
                        temperature=0.7,
                        max_output_tokens=1024,
                    )
                )

                final_text = None
                if final_response and final_response.candidates and final_response.candidates[0].content and final_response.candidates[0].content.parts:
                    valid_text_parts = [p.text for p in final_response.candidates[0].content.parts if getattr(p, 'text', None)]
                    if valid_text_parts:
                        final_text = " ".join(valid_text_parts).strip()

                if final_text:
                    self.conversation_history.append(
                        types.Content(role="model", parts=[types.Part(text=final_text)])
                    )
                    return final_text
                else:
                    # Use the function results as fallback response
                    result_text = "; ".join([f"{result}" for _, result in results if result])
                    fallback = f"Done, Sir. {result_text}" if result_text else "Done, Sir."
                    self.conversation_history.append(
                        types.Content(role="model", parts=[types.Part(text=fallback)])
                    )
                    return fallback

            except Exception as e:
                logger.error(f"Final response error: {e}")
                result_text = "; ".join([f"{result}" for _, result in results if result])
                fallback = f"Task completed, Sir. {result_text}" if result_text else "Task completed, Sir."
                return fallback

        elif text_parts:
            # Pure text response (no function call needed)
            text = " ".join([p.text for p in text_parts if p.text]).strip()
            if not text:
                text = "Yes Sir, I am here."
            self.conversation_history.append(
                types.Content(role="model", parts=[types.Part(text=text)])
            )
            return text

        else:
            return "I'm here to help, Sir. What would you like to do?"


    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("🗑️ Conversation history cleared")

    def get_history_summary(self) -> str:
        """Get a summary of conversation history."""
        count = len(self.conversation_history)
        return f"{count} messages in history"
