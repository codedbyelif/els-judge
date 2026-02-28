import sys
import os
import requests
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, TextArea, Input, Button, Static, Markdown, LoadingIndicator
from textual.reactive import reactive

class ResultView(Static):
    """A widget to display the analysis results."""
    
    results_text = reactive("")
    
    def render(self) -> str:
        return self.results_text

class AICodeJudgeApp(App):
    """A Textual TUI for the LLM Consensus Engine."""
    
    CSS = """
    Screen {
        background: #0c0c12;
    }
    
    Header {
        background: #d6336c;
        color: white;
        text-style: bold;
    }
    
    Footer {
        background: #131320;
        color: #f06595;
    }
    
    #main_container {
        padding: 1;
        width: 100%;
        height: 100%;
        layout: horizontal;
    }
    
    #left_pane {
        width: 40%;
        height: 100%;
        border-right: solid #d6336c;
        padding-right: 1;
    }
    
    #right_pane {
        width: 60%;
        height: 100%;
        padding-left: 1;
    }

    .label {
        color: #f06595;
        text-style: bold;
        margin-bottom: 0;
        margin-top: 1;
    }
    
    TextArea {
        height: 1fr;
        border: solid #d6336c;
        background: #1a1a2e;
        color: #eeeeee;
    }

    TextArea:focus {
        border: double #f06595;
    }
    
    Input {
        border: solid #d6336c;
        background: #1a1a2e;
        color: #eeeeee;
    }
    
    Input:focus {
        border: double #f06595;
    }
    
    Button {
        width: 100%;
        margin-top: 1;
        background: #d6336c;
        color: white;
        text-style: bold;
    }
    
    Button:hover {
        background: #a61e4d;
    }
    
    #branding_footer {
        color: #f06595;
        text-style: italic;
        text-align: center;
        margin-top: 1;
    }
    
    #results_container {
        height: 100%;
        overflow-y: scroll;
        border: solid #d6336c;
        background: #131320;
        padding: 1;
    }
    
    LoadingIndicator {
        color: #f06595;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+r", "analyze", "Analyze Code")
    ]
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        
        with Container(id="main_container"):
            # Left Pane: Inputs
            with Vertical(id="left_pane"):
                yield Static("Your Code:", classes="label")
                yield TextArea(id="code_input", language="python", show_line_numbers=True)
                
                yield Static("What should be improved?", classes="label")
                yield Input(id="prompt_input", placeholder="e.g. Add type hints and error handling")
                
                yield Button("Analyze with 3 AI Models", id="submit_btn", variant="primary")
                yield Static("♥ Built by codedbyelif ♥", id="branding_footer")
                
            # Right Pane: Results
            with Vertical(id="right_pane"):
                yield Static("Analysis Report:", classes="label")
                with Container(id="results_container"):
                    yield Markdown("## Welcome to LLM Consensus Engine\n\n1. Paste your code on the left.\n2. Enter your instructions.\n3. Press **Analyze** to submit.", id="markdown_result")
                    yield LoadingIndicator(id="loading", classes="hidden")
                
        yield Footer()

    def on_mount(self) -> None:
        self.title = "LLM Consensus Engine"
        self.query_one("#loading").display = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit_btn":
            await self.action_analyze()

    async def action_analyze(self) -> None:
        code_input = self.query_one("#code_input", TextArea).text
        prompt_input = self.query_one("#prompt_input", Input).value
        
        if not code_input.strip() or not prompt_input.strip():
            self.query_one("#markdown_result", Markdown).update("### ❌ Error\nPlease provide both code and a prompt.")
            return

        # Show loading
        btn = self.query_one("#submit_btn", Button)
        btn.disabled = True
        btn.label = "Analyzing..."
        
        md_view = self.query_one("#markdown_result", Markdown)
        loading = self.query_one("#loading", LoadingIndicator)
        
        md_view.display = False
        loading.display = True
        
        self.run_worker(self.fetch_analysis(code_input, prompt_input), exclusive=True)

    async def fetch_analysis(self, code: str, prompt: str) -> None:
        api_url = "http://localhost:8000/api/submit-code"
        try:
            # We run the blocking request in the worker thread
            import urllib.request
            import inspect
            import json
            
            data = json.dumps({"code": code, "prompt": prompt}).encode('utf-8')
            req = urllib.request.Request(api_url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode())
                
            md_report = result.get("markdown_report", "No report generated.")
            
            self.call_from_thread(self.update_success, md_report)
            
        except Exception as e:
            self.call_from_thread(self.update_error, str(e))

    def update_success(self, markdown_text: str) -> None:
        self.query_one("#loading").display = False
        md_view = self.query_one("#markdown_result", Markdown)
        md_view.update(markdown_text)
        md_view.display = True
        
        btn = self.query_one("#submit_btn", Button)
        btn.disabled = False
        btn.label = "Analyze with 3 AI Models"

    def update_error(self, error_msg: str) -> None:
        self.query_one("#loading").display = False
        md_view = self.query_one("#markdown_result", Markdown)
        md_view.update(f"### ❌ API Error\nCould not connect to the backend. Ensure FastAPI is running on port 8000.\n\nDetails: `{error_msg}`")
        md_view.display = True
        
        btn = self.query_one("#submit_btn", Button)
        btn.disabled = False
        btn.label = "Analyze with 3 AI Models"

if __name__ == "__main__":
    app = AICodeJudgeApp()
    app.run()
