import json
from typing import List



DEFAULT_STYLES =  ["Fooocus V2","Fooocus Enhance","Fooocus Sharp"]

class PromptExtractor:
    def __init__(self):
        with open("utils/fooocus/style_mapping.json","r") as f:
            self.style_mapping = json.load(f)

    def style_extractor(self, user_message: str) -> List[str]:
        styles = DEFAULT_STYLES
        user_style = None
        if "--style" in user_message:
            style_start = user_message.find("--style") + len("--style")
            
            # Skip any whitespace immediately after '--style'
            while style_start < len(user_message) and user_message[style_start].isspace():
                style_start += 1
            
            # Initialize user_style as an empty string
            user_style = ""
            
            # Capture up to two words
            word_count = 0
            current_index = style_start
            
            while word_count < 2 and current_index < len(user_message):
                # Find the next space or end of the string
                next_space = user_message.find(" ", current_index)
                
                if next_space == -1:
                    # If no space is found, take the rest of the string
                    user_style += user_message[current_index:].strip()
                    break
                else:
                    # Add the current word to user_style
                    user_style += user_message[current_index:next_space].strip() + " "
                    word_count += 1
                    current_index = next_space + 1
            
            # Strip any trailing whitespace from user_style
            user_style = user_style.strip()
            
            print(f"user_style: '{user_style}'")
            if user_style in self.style_mapping:
                styles = self.style_mapping[user_style]
            elif user_style in [item for sublist in self.style_mapping.values() for item in sublist]:
                for key, value in self.style_mapping.items():
                    if user_style in value:
                        styles = value
        
        print(f"Used style: {styles}")
        return styles
    
def prompt_cleaner(user_message: str) -> str:
    """
    Removes '-- <text>' from the user message.

    Args:
    user_message (str): The user's input message.

    Returns:
    str: The cleaned user message.
    """
    # Split the user message into parts separated by '--'
    parts = user_message.split('--', 1)
    
    # Return the first part, stripped of leading/trailing whitespace
    return parts[0].strip()
