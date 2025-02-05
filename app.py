from dotenv import load_dotenv
import os
from wardbuddy.learning_interface import LearningInterface

# Load environment variables
load_dotenv()

# Check required environment variables
required_vars = ["OPENROUTER_API_KEY", "API_URL"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Create interface
interface = LearningInterface(
    model="anthropic/claude-3.5-sonnet",
    api_url=os.getenv("API_URL")
)

# Create app
demo = interface.create_interface()

# Launch with appropriate settings
if os.getenv("SPACE_ID"):  # Running on HF Spaces
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False
    )
else:  # Local development
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )