"""Gradio interface"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_learning_interface.ipynb.

# %% auto 0
__all__ = ['logger', 'LearningInterface', 'launch_learning_interface', 'write_css']

# %% ../nbs/02_learning_interface.ipynb 4
from typing import Dict, List, Optional, Tuple, Any
import gradio as gr
import logging
from pathlib import Path
import asyncio
from .clinical_tutor import ClinicalTutor
from .utils import format_response
from .learning_context import setup_logger


logger = setup_logger(__name__)

# %% ../nbs/02_learning_interface.ipynb 7
class LearningInterface:
    """
    Gradio interface for clinical learning interactions.
    
    The interface provides:
    - Case presentation input and feedback
    - Learning preference configuration
    - Session history management
    - Progress tracking visualization
    
    Examples:
        >>> interface = LearningInterface()
        >>> demo = interface.create_interface()
        >>> demo.launch()
    """
    
    def __init__(
        self,
        context_path: Optional[Path] = None,
        theme: str = "default"
    ):
        """
        Initialize learning interface.
        
        Args:
            context_path: Optional path for context persistence
            theme: Gradio theme name
        """
        self.tutor = ClinicalTutor(context_path)
        self.theme = theme
        self.context_path = context_path
        logger.info("Learning interface initialized")
    
    async def process_input(
        self, 
        message: str, 
        history: List[Dict[str, str]],  # Changed to Dict for messages format
        clinical_reasoning: float = 1.0,
        medical_knowledge: float = 1.0,
        presentation_skills: float = 1.0,
        differential_building: float = 1.0
    ) -> Tuple[List[Dict[str, str]], str]:  # Updated return type
        """Process user input and generate context-aware response"""
        try:
            if not message.strip():
                return history, "Please provide your case or question."
            
            # Update feedback preferences
            feedback_focus = {
                "clinical_reasoning": clinical_reasoning,
                "medical_knowledge": medical_knowledge,
                "presentation_skills": presentation_skills,
                "differential_building": differential_building
            }
            self.tutor.update_feedback_preferences(feedback_focus)
            
            # Process the interaction
            response = await self.tutor.process_interaction(message)
            
            # Format response for display using format_response utility
            formatted_response = format_response(response)
            
            # Initialize history if None
            if history is None:
                history = []
            
            # Use message format
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": formatted_response})
            
            return history, ""
            
        except Exception as e:
            logger.error(f"Error in interface: {str(e)}")
            if history is None:
                history = []
            return history, "An error occurred. Please try again."
    
    def update_preferences(
        self,
        clinical_reasoning: float,
        medical_knowledge: float,
        presentation_skills: float,
        differential_building: float
    ) -> Dict[str, float]:
        """
        Update feedback preferences.
        
        Args:
            clinical_reasoning: Focus weight for clinical reasoning
            medical_knowledge: Focus weight for medical knowledge
            presentation_skills: Focus weight for presentation skills
            differential_building: Focus weight for differential diagnosis
            
        Returns:
            dict: Updated preferences
        """
        preferences = {
            "clinical_reasoning": clinical_reasoning,
            "medical_knowledge": medical_knowledge,
            "presentation_skills": presentation_skills,
            "differential_building": differential_building
        }
        
        self.tutor.update_feedback_preferences(preferences)
        return preferences
    
    def create_interface(self) -> gr.Blocks:
        """Create and configure the Gradio interface"""
        with gr.Blocks(
            title="Clinical Learning Assistant",
            theme=self.theme
        ) as interface:
            gr.Markdown("# Clinical Learning Assistant")
            gr.Markdown("## Enhance your clinical reasoning through adaptive feedback")
            
            with gr.Tab("Case Discussion"):
                with gr.Row():
                    # Left column - Chat interface
                    with gr.Column(scale=2):
                        chatbot = gr.Chatbot(
                            height=400,
                            type='messages',
                            label="Learning Session"
                        )
                        
                        msg = gr.Textbox(
                            label="Present your case or ask a question",
                            placeholder=(
                                "Present your case as you would to your supervisor:\n"
                                "- Start with the chief complaint\n"
                                "- Include relevant history and findings\n"
                                "- Share your assessment and plan"
                            ),
                            lines=5
                        )
                        
                        with gr.Row():
                            clear = gr.Button("Clear Session")
                            retry = gr.Button("Retry Last")
                    
                    # Right column - Learning focus controls
                    with gr.Column(scale=1):
                        gr.Markdown("### Learning Focus Areas")
                        gr.Markdown(
                            "Adjust these sliders to emphasize different aspects "
                            "of feedback for your case presentations."
                        )
                        
                        clinical_reasoning = gr.Slider(
                            minimum=0.5,
                            maximum=2.0,
                            value=1.0,
                            step=0.1,
                            label="Clinical Reasoning",
                            info="Emphasis on diagnostic process and medical decision-making"
                        )
                        medical_knowledge = gr.Slider(
                            minimum=0.5,
                            maximum=2.0,
                            value=1.0,
                            step=0.1,
                            label="Medical Knowledge",
                            info="Focus on relevant medical concepts and evidence"
                        )
                        presentation_skills = gr.Slider(
                            minimum=0.5,
                            maximum=2.0,
                            value=1.0,
                            step=0.1,
                            label="Presentation Skills",
                            info="Structure, clarity, and communication effectiveness"
                        )
                        differential_building = gr.Slider(
                            minimum=0.5,
                            maximum=2.0,
                            value=1.0,
                            step=0.1,
                            label="Differential Building",
                            info="Development of comprehensive differentials"
                        )
            
            # Initialize empty history
            state = gr.State([])
            
            # Event handlers
            msg.submit(
                self.process_input,
                inputs=[
                    msg, 
                    state,  # Use state instead of chatbot for history
                    clinical_reasoning,
                    medical_knowledge,
                    presentation_skills,
                    differential_building
                ],
                outputs=[chatbot, msg]
            )
            
            clear.click(
                lambda: ([], ""), 
                outputs=[chatbot, msg]
            )
            
            retry.click(
                lambda history: (history[:-1], history[-1]["content"]) if history else (history, ""),
                inputs=[state],
                outputs=[chatbot, msg]
            )
            
        return interface

# %% ../nbs/02_learning_interface.ipynb 9
async def launch_learning_interface(
    port: Optional[int] = None,
    context_path: Optional[Path] = None,
    share: bool = False,
    theme: str = "default"
) -> None:
    """
    Launch the learning interface application.
    
    Args:
        port: Optional port number
        context_path: Optional path for context persistence
        share: Whether to create a public link
        theme: Gradio theme name
    """
    try:
        interface = LearningInterface(context_path, theme)
        app = interface.create_interface()
        app.launch(
            server_port=port,
            share=share
        )
        logger.info(f"Interface launched on port: {port}")
    except Exception as e:
        logger.error(f"Error launching interface: {str(e)}")
        raise


# %% ../nbs/02_learning_interface.ipynb 11
def write_css():
    """Create custom CSS file for the interface"""
    css = """
    .gr-button {
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .gr-button:hover {
        background-color: #2c5282;
        color: white;
    }
    
    .message {
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    .user-message {
        background-color: #e2e8f0;
    }
    
    .assistant-message {
        background-color: #ebf8ff;
    }
    """
    
    with open("styles.css", "w") as f:
        f.write(css)

