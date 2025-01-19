from dotenv import load_dotenv
import os
from wardbuddy.learning_interface import LearningInterface

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("OPENROUTER_API_KEY"):
    raise ValueError("Please set OPENROUTER_API_KEY in your .env file")

# Create and launch interface
interface = LearningInterface()
demo = interface.create_interface()
demo.launch(server_name='0.0.0.0', server_port=7860, share=True)