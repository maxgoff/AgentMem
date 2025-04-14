# Case Study: Building a Chatbot Assistant with AgentMem

This case study demonstrates how to build a chatbot assistant that leverages AgentMem's memory systems to create a more helpful, personalized experience for users.

## Overview

Our chatbot assistant will:

1. Remember user preferences and information using semantic memory
2. Recall conversation history using episodic memory
3. Apply appropriate response patterns using procedural memory
4. Adapt to user needs over time based on interaction history

## Implementation

### Step 1: Setting Up the Project

First, let's set up our project structure:

```bash
mkdir chatbot_assistant
cd chatbot_assistant
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install "agentmem[vector]" numpy
```

### Step 2: Creating the Assistant Class

Let's create a file called `assistant.py` with our main assistant class:

```python
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from agentmem.semantic import SemanticMemory
from agentmem.episodic import EpisodicMemory
from agentmem.procedural import ProceduralMemory


class ChatbotAssistant:
    def __init__(self, name: str = "Assistant", persistence_dir: Optional[str] = None):
        """Initialize the chatbot assistant with memory systems."""
        self.name = name
        self.current_user_id = None
        self.conversation_id = str(uuid.uuid4())
        
        # Initialize memory systems
        self.user_memory = SemanticMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.conversation_memory = EpisodicMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.response_patterns = ProceduralMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        # Load existing memory if persistence is enabled
        if persistence_dir:
            self.user_memory.load_all()
            self.conversation_memory.load_all()
            self.response_patterns.load_all()
            
        # Initialize with default response patterns if none exist
        if len(self.response_patterns.query("")) == 0:
            self._initialize_response_patterns()
            
        print(f"{self.name} initialized with conversation ID: {self.conversation_id}")
        
    def _initialize_response_patterns(self):
        """Initialize default response patterns."""
        # Greeting pattern
        self.response_patterns.create(
            content="How to respond to greetings",
            task="Respond to greeting",
            steps=[
                "Check if the user is known",
                "If known, include their name in the greeting",
                "Include a friendly opening",
                "Ask how the user is doing"
            ],
            domains=["conversation", "greeting"],
            metadata={
                "templates": [
                    "Hello{user}! How can I help you today?",
                    "Hi{user}! It's good to see you. How are you doing?",
                    "Greetings{user}! How may I assist you today?"
                ]
            }
        )
        
        # Help request pattern
        self.response_patterns.create(
            content="How to respond to help requests",
            task="Respond to help request",
            steps=[
                "Acknowledge the help request",
                "Provide information about capabilities",
                "Give examples of what you can do",
                "Ask for more specific information if needed"
            ],
            domains=["conversation", "help"],
            metadata={
                "templates": [
                    "I'd be happy to help! I can remember our conversations, learn your preferences, and provide information on topics I know about. What would you like to know?",
                    "Sure, I can assist with that. Could you tell me more specifically what you need help with?"
                ]
            }
        )
        
        # Farewell pattern
        self.response_patterns.create(
            content="How to respond to goodbyes",
            task="Respond to farewell",
            steps=[
                "Acknowledge the farewell",
                "Express positive sentiment about the conversation",
                "Offer future assistance",
                "Say goodbye"
            ],
            domains=["conversation", "farewell"],
            metadata={
                "templates": [
                    "Goodbye{user}! It was nice talking with you. Feel free to return if you have more questions!",
                    "See you later{user}! Have a great day!",
                    "Farewell{user}! I'll be here if you need any more help."
                ]
            }
        )
        
    def identify_user(self, user_id: str, user_name: Optional[str] = None) -> str:
        """
        Identify the current user of the chatbot.
        
        Args:
            user_id: Unique identifier for the user
            user_name: Optional name for new users
            
        Returns:
            Greeting message for the user
        """
        self.current_user_id = user_id
        
        # Search for existing user profile
        user_profiles = self.user_memory.query(
            user_id,
            category="user_profile"
        )
        
        if user_profiles:
            # Existing user
            profile = user_profiles[0]
            name = profile.get("metadata", {}).get("name", "there")
            
            # Record this interaction in episodic memory
            self.conversation_memory.create(
                content=f"User {name} (ID: {user_id}) started a new conversation",
                timestamp=datetime.now(),
                context={
                    "event_type": "session_start",
                    "user_id": user_id,
                    "conversation_id": self.conversation_id
                },
                importance=5
            )
            
            return f"Welcome back, {name}! How can I help you today?"
        elif user_name:
            # New user with a name
            self.user_memory.create(
                content=f"User profile for {user_name}",
                category="user_profile",
                tags=["user", "profile"],
                metadata={
                    "user_id": user_id,
                    "name": user_name,
                    "first_seen": datetime.now().isoformat(),
                    "interactions_count": 0
                }
            )
            
            # Record this in episodic memory
            self.conversation_memory.create(
                content=f"New user {user_name} (ID: {user_id}) started a conversation",
                timestamp=datetime.now(),
                context={
                    "event_type": "new_user",
                    "user_id": user_id,
                    "conversation_id": self.conversation_id
                },
                importance=8
            )
            
            return f"Hello, {user_name}! It's nice to meet you. How can I help you today?"
        else:
            # Unknown user without a name
            return "Hello! I don't think we've met before. What's your name?"
    
    def remember_message(self, message: str, from_user: bool = True, 
                        importance: int = 5) -> uuid.UUID:
        """
        Record a message in the conversation history.
        
        Args:
            message: The message to remember
            from_user: Whether the message is from the user (True) or assistant (False)
            importance: How important this message is (1-10)
            
        Returns:
            ID of the created memory
        """
        if not self.current_user_id and from_user:
            # If no user is identified yet, assume this is a name
            return self.identify_user(str(uuid.uuid4()), message)
        
        # Create context data for the message
        context = {
            "user_id": self.current_user_id,
            "conversation_id": self.conversation_id,
            "from_user": from_user,
            "from_assistant": not from_user,
            "timestamp": datetime.now().isoformat()
        }
        
        # Adjust importance based on content
        if from_user:
            # User messages with questions are more important
            if "?" in message:
                importance = min(importance + 2, 10)
            # Messages with personal information are more important
            if any(phrase in message.lower() for phrase in ["my name is", "i am", "i like", "i don't like"]):
                importance = min(importance + 3, 10)
                self._extract_user_information(message)
        
        # Record the message
        memory_id = self.conversation_memory.create(
            content=message,
            timestamp=datetime.now(),
            context=context,
            importance=importance
        )
        
        # Update interaction count for the user
        if from_user and self.current_user_id:
            user_profiles = self.user_memory.query(
                self.current_user_id,
                category="user_profile"
            )
            
            if user_profiles:
                profile = user_profiles[0]
                profile_id = profile["id"]
                
                # Get current count
                count = profile.get("metadata", {}).get("interactions_count", 0)
                
                # Update the count
                self.user_memory.update(
                    profile_id,
                    metadata={
                        "interactions_count": count + 1,
                        "last_interaction": datetime.now().isoformat()
                    }
                )
        
        return memory_id
    
    def _extract_user_information(self, message: str) -> None:
        """
        Extract user information from a message and update the user profile.
        
        Args:
            message: Message to extract information from
        """
        if not self.current_user_id:
            return
        
        message_lower = message.lower()
        
        # Extract name
        name_indicators = ["my name is", "i am called", "i'm called", "call me"]
        for indicator in name_indicators:
            if indicator in message_lower:
                name_info = message_lower.split(indicator, 1)[1].strip().split()[0]
                name_info = name_info.capitalize()
                
                # Store this information
                self.user_memory.create(
                    content=f"User's name is {name_info}",
                    category="user_fact",
                    tags=["personal", "name"],
                    metadata={
                        "user_id": self.current_user_id,
                        "attribute": "name",
                        "value": name_info
                    }
                )
                
                # Update user profile
                self._update_user_profile({"name": name_info})
                return
        
        # Extract likes
        if "i like" in message_lower:
            like_info = message_lower.split("i like", 1)[1].strip()
            
            # Store this preference
            self.user_memory.create(
                content=f"User likes {like_info}",
                category="user_preference",
                tags=["preference", "like"],
                metadata={
                    "user_id": self.current_user_id,
                    "attribute": "likes",
                    "value": like_info
                }
            )
            return
        
        # Extract dislikes
        if "i don't like" in message_lower or "i do not like" in message_lower:
            split_phrase = "i don't like" if "i don't like" in message_lower else "i do not like"
            dislike_info = message_lower.split(split_phrase, 1)[1].strip()
            
            # Store this preference
            self.user_memory.create(
                content=f"User dislikes {dislike_info}",
                category="user_preference",
                tags=["preference", "dislike"],
                metadata={
                    "user_id": self.current_user_id,
                    "attribute": "dislikes",
                    "value": dislike_info
                }
            )
            return
    
    def _update_user_profile(self, attributes: Dict[str, Any]) -> None:
        """
        Update user profile with new attributes.
        
        Args:
            attributes: Dictionary of attributes to update
        """
        if not self.current_user_id:
            return
        
        user_profiles = self.user_memory.query(
            self.current_user_id,
            category="user_profile"
        )
        
        if user_profiles:
            profile = user_profiles[0]
            profile_id = profile["id"]
            
            # Update the profile
            metadata = profile.get("metadata", {}).copy()
            metadata.update(attributes)
            metadata["last_updated"] = datetime.now().isoformat()
            
            self.user_memory.update(
                profile_id,
                metadata=metadata
            )
    
    def get_recent_conversation(self, message_count: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent messages in the current conversation.
        
        Args:
            message_count: Number of messages to retrieve
            
        Returns:
            List of recent messages
        """
        # Query messages from the current conversation
        messages = self.conversation_memory.query(
            "",
            context_keys=["conversation_id"]
        )
        
        # Filter to current conversation
        current_messages = [
            msg for msg in messages 
            if msg.get("context", {}).get("conversation_id") == self.conversation_id
        ]
        
        # Sort by timestamp (older messages first)
        current_messages.sort(key=lambda x: x.get("timestamp"))
        
        # Return the most recent messages
        return current_messages[-message_count:]
    
    def get_user_preferences(self) -> Dict[str, List[str]]:
        """
        Get the current user's preferences.
        
        Returns:
            Dictionary with likes and dislikes
        """
        if not self.current_user_id:
            return {"likes": [], "dislikes": []}
        
        preferences = {
            "likes": [],
            "dislikes": []
        }
        
        # Get likes
        likes = self.user_memory.query(
            "",
            category="user_preference",
            tags=["like"]
        )
        
        likes = [
            l.get("metadata", {}).get("value") 
            for l in likes 
            if l.get("metadata", {}).get("user_id") == self.current_user_id
        ]
        preferences["likes"] = [l for l in likes if l]
        
        # Get dislikes
        dislikes = self.user_memory.query(
            "",
            category="user_preference",
            tags=["dislike"]
        )
        
        dislikes = [
            d.get("metadata", {}).get("value") 
            for d in dislikes 
            if d.get("metadata", {}).get("user_id") == self.current_user_id
        ]
        preferences["dislikes"] = [d for d in dislikes if d]
        
        return preferences
    
    def generate_response(self, message: str) -> str:
        """
        Generate a response to a user message.
        
        Args:
            message: The user's message
            
        Returns:
            The assistant's response
        """
        # Remember the user message
        self.remember_message(message, from_user=True)
        
        # Analyze intent
        intent = self._analyze_intent(message)
        
        # Get relevant response pattern
        pattern = self._get_response_pattern(intent, message)
        
        # Get user information for personalization
        user_info = self._get_user_info()
        
        # Get recent conversation for context
        recent_messages = self.get_recent_conversation(5)
        
        # Generate response using the pattern and context
        response = self._apply_response_pattern(pattern, message, user_info, recent_messages)
        
        # Remember the response
        self.remember_message(response, from_user=False)
        
        return response
    
    def _analyze_intent(self, message: str) -> str:
        """
        Analyze the intent of a user message.
        
        Args:
            message: The user's message
            
        Returns:
            The identified intent
        """
        message_lower = message.lower()
        
        # Basic intent recognition
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "greeting"
        
        if any(word in message_lower for word in ["bye", "goodbye", "see you", "farewell"]):
            return "farewell"
        
        if any(phrase in message_lower for phrase in ["help me", "how can you help", "what can you do"]):
            return "help_request"
        
        if "?" in message:
            return "question"
        
        # Default intent
        return "general_statement"
    
    def _get_response_pattern(self, intent: str, message: str) -> Dict[str, Any]:
        """
        Get a response pattern for the given intent.
        
        Args:
            intent: The message intent
            message: The user's message
            
        Returns:
            A response pattern
        """
        # Direct intent mapping
        intent_map = {
            "greeting": "Respond to greeting",
            "farewell": "Respond to farewell",
            "help_request": "Respond to help request"
        }
        
        if intent in intent_map:
            # Look for a specific pattern for this intent
            patterns = self.response_patterns.query(
                intent_map[intent],
                domain="conversation"
            )
            
            if patterns:
                return patterns[0]
        
        # Try to find a relevant pattern using vector search
        patterns = self.response_patterns.query(
            message,
            use_vector=True,
            n_results=1
        )
        
        if patterns:
            return patterns[0]
        
        # Default pattern if no specific one is found
        return {
            "task": "General response",
            "steps": [
                "Acknowledge the user's message",
                "Respond in a helpful manner",
                "Ask a relevant follow-up question"
            ],
            "metadata": {
                "templates": [
                    "I understand. Can you tell me more about that?",
                    "I see. How can I help you with that?",
                    "Got it. Is there anything specific you'd like to know?"
                ]
            }
        }
    
    def _get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the current user.
        
        Returns:
            Dictionary with user information
        """
        if not self.current_user_id:
            return {"name": None}
        
        user_info = {"name": None}
        
        # Get user profile
        profiles = self.user_memory.query(
            self.current_user_id,
            category="user_profile"
        )
        
        if profiles:
            profile = profiles[0]
            metadata = profile.get("metadata", {})
            user_info["name"] = metadata.get("name")
            user_info["interactions_count"] = metadata.get("interactions_count", 0)
        
        # Get preferences
        preferences = self.get_user_preferences()
        user_info["likes"] = preferences["likes"]
        user_info["dislikes"] = preferences["dislikes"]
        
        return user_info
    
    def _apply_response_pattern(self, pattern: Dict[str, Any], message: str, 
                              user_info: Dict[str, Any], 
                              recent_messages: List[Dict[str, Any]]) -> str:
        """
        Apply a response pattern to generate a response.
        
        Args:
            pattern: The response pattern to apply
            message: The user's message
            user_info: Information about the user
            recent_messages: Recent conversation messages
            
        Returns:
            Generated response
        """
        import random
        
        # Get templates from the pattern
        templates = pattern.get("metadata", {}).get("templates", [
            "I understand. How can I help you with that?",
            "I see. What else would you like to know?"
        ])
        
        # Choose a template
        template = random.choice(templates)
        
        # Personalize with user name if available
        if user_info.get("name"):
            template = template.replace("{user}", f" {user_info['name']}")
        else:
            template = template.replace("{user}", "")
        
        # Additional personalization based on preferences
        if user_info.get("likes") and random.random() < 0.3:  # 30% chance
            like = random.choice(user_info["likes"])
            # Only add this if it's relevant to the current message
            if like in message.lower():
                template += f" I remember you mentioned you like {like}."
        
        # Add context awareness based on conversation history
        user_messages = [
            msg for msg in recent_messages 
            if msg.get("context", {}).get("from_user", False)
            and msg.get("content") != message  # Don't reference the current message
        ]
        
        if user_messages and random.random() < 0.3:  # 30% chance
            # Reference a previous message
            prev_message = user_messages[-1]["content"]
            # Only add if the previous message is relevant and not too long
            if len(prev_message) < 50 and prev_message not in message:
                template += f" Earlier you mentioned '{prev_message}'. "
        
        return template
    
    def save(self) -> None:
        """Save all memory systems to disk."""
        self.user_memory.save_all()
        self.conversation_memory.save_all()
        self.response_patterns.save_all()
        print("Assistant memory saved to disk.")
```

### Step 3: Creating the Command-Line Interface

Next, let's create a simple CLI for interacting with our assistant (`cli.py`):

```python
import os
import argparse
from assistant import ChatbotAssistant

def main():
    parser = argparse.ArgumentParser(description='Chatbot Assistant with Memory')
    parser.add_argument('--name', type=str, default='MemoryBot',
                        help='Name of the assistant')
    parser.add_argument('--memory-dir', type=str, default='./assistant_memory',
                        help='Directory for persistent memory storage')
    parser.add_argument('--no-memory', action='store_true',
                        help='Disable persistent memory')
    
    args = parser.parse_args()
    
    # Create memory directory if it doesn't exist
    if not args.no_memory:
        os.makedirs(args.memory_dir, exist_ok=True)
    
    # Initialize the assistant
    assistant = ChatbotAssistant(
        name=args.name,
        persistence_dir=None if args.no_memory else args.memory_dir
    )
    
    print(f"\n{args.name} is ready to chat. Type 'exit' to end the conversation.")
    
    # Start chat loop
    user_input = input("You: ")
    
    # Initial message is treated as the user's name for a new session
    response = assistant.identify_user(str(hash(user_input)), user_input)
    print(f"\n{args.name}: {response}")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print(f"\n{args.name}: Goodbye! It was nice talking with you.")
            break
        
        response = assistant.generate_response(user_input)
        print(f"\n{args.name}: {response}")
    
    # Save assistant memory
    if not args.no_memory:
        assistant.save()

if __name__ == "__main__":
    main()
```

### Step 4: Testing the Assistant

Now, let's run our assistant and see how it works:

```bash
python cli.py --name MemBot --memory-dir ./membot_data
```

Sample interaction:

```
MemBot is ready to chat. Type 'exit' to end the conversation.
You: Alice

MemBot: Hello, Alice! It's nice to meet you. How can I help you today?

You: I like chocolate ice cream

MemBot: I understand. How can I help you with that?

You: What can you help me with?

MemBot: I'd be happy to help! I can remember our conversations, learn your preferences, and provide information on topics I know about. What would you like to know?

You: Can you remember what I like?

MemBot: I see. What else would you like to know? Earlier you mentioned 'I like chocolate ice cream'.

You: Tell me something about myself

MemBot: I understand. I remember you mentioned you like chocolate ice cream.

You: bye

MemBot: Goodbye! It was nice talking with you.
```

### Step 5: Improving the Assistant

Let's extend our assistant by adding the ability to learn new responses from interactions. Add these methods to the `ChatbotAssistant` class:

```python
def learn_response_pattern(self, trigger: str, response_template: str) -> uuid.UUID:
    """
    Learn a new response pattern from examples.
    
    Args:
        trigger: The trigger phrase or intent
        response_template: Template for responses
        
    Returns:
        ID of the created pattern
    """
    pattern_id = self.response_patterns.create(
        content=f"How to respond to: {trigger}",
        task=f"Respond to {trigger}",
        steps=[
            "Recognize the trigger phrase or intent",
            "Apply the response template",
            "Personalize the response for the user",
            "Ensure the response is contextually appropriate"
        ],
        domains=["conversation", "learned"],
        metadata={
            "templates": [response_template],
            "learned_at": datetime.now().isoformat(),
            "trigger": trigger
        }
    )
    
    return pattern_id

def process_teaching_intent(self, message: str) -> Optional[str]:
    """
    Process a teaching intent from the user.
    
    Args:
        message: The user's message
        
    Returns:
        Confirmation message if teaching was successful, None otherwise
    """
    message_lower = message.lower()
    
    # Check for teaching patterns
    teaching_patterns = [
        "when i say", "if i say", "when i ask", 
        "you should respond", "you should say"
    ]
    
    if not any(pattern in message_lower for pattern in teaching_patterns):
        return None
    
    # Try to extract trigger and response
    if "when i say" in message_lower and "you should say" in message_lower:
        parts = message_lower.split("you should say")
        if len(parts) != 2:
            return "I'm not sure I understand how to respond to that. Could you try rephrasing?"
        
        response_part = parts[1].strip()
        trigger_part = parts[0].replace("when i say", "").strip()
        
        if trigger_part and response_part:
            self.learn_response_pattern(trigger_part, response_part)
            return f"Thank you! I've learned that when you say '{trigger_part}', I should respond with '{response_part}'."
    
    # Try other teaching patterns
    if "when i say" in message_lower and "respond with" in message_lower:
        parts = message_lower.split("respond with")
        if len(parts) != 2:
            return "I'm not sure I understand how to respond to that. Could you try rephrasing?"
        
        response_part = parts[1].strip()
        trigger_part = parts[0].replace("when i say", "").strip()
        
        if trigger_part and response_part:
            self.learn_response_pattern(trigger_part, response_part)
            return f"Got it! When you say '{trigger_part}', I'll respond with '{response_part}'."
    
    return "I'd like to learn how to respond, but I didn't quite understand the format. Try something like 'When I say hello, you should say hi there!'"
```

Now modify the `generate_response` method to check for teaching intents first:

```python
def generate_response(self, message: str) -> str:
    """
    Generate a response to a user message.
    
    Args:
        message: The user's message
        
    Returns:
        The assistant's response
    """
    # Remember the user message
    self.remember_message(message, from_user=True)
    
    # Check for teaching intent
    teaching_response = self.process_teaching_intent(message)
    if teaching_response:
        # Remember the response
        self.remember_message(teaching_response, from_user=False)
        return teaching_response
    
    # Rest of the method remains the same...
```

### Step 6: Adding Conversation Analytics

Let's add some analytics capabilities to track conversation patterns:

```python
def get_conversation_analytics(self) -> Dict[str, Any]:
    """
    Generate analytics about conversations with the current user.
    
    Returns:
        Dictionary with conversation analytics
    """
    if not self.current_user_id:
        return {"error": "No user identified"}
    
    analytics = {
        "total_interactions": 0,
        "average_message_length": 0,
        "common_topics": [],
        "sentiment_analysis": {},
        "conversation_patterns": {}
    }
    
    # Get all user messages
    user_messages = self.conversation_memory.query(
        "",
        context_keys=["user_id", "from_user"]
    )
    
    user_messages = [
        msg for msg in user_messages 
        if msg.get("context", {}).get("user_id") == self.current_user_id
        and msg.get("context", {}).get("from_user", False)
    ]
    
    if not user_messages:
        return {"error": "No messages found for this user"}
    
    # Calculate total interactions
    analytics["total_interactions"] = len(user_messages)
    
    # Calculate average message length
    total_length = sum(len(msg.get("content", "")) for msg in user_messages)
    analytics["average_message_length"] = total_length / len(user_messages)
    
    # Extract basic topics (very simple approach)
    all_content = " ".join([msg.get("content", "") for msg in user_messages]).lower()
    
    # Simple word frequency analysis
    common_words = {}
    stop_words = {"a", "an", "the", "and", "or", "but", "is", "are", "was", "were", 
                 "this", "that", "i", "you", "he", "she", "it", "we", "they", "my",
                 "your", "his", "her", "its", "our", "their", "to", "for", "of", "in"}
    
    for word in all_content.split():
        word = word.strip(".,!?\"'()[]{}:;")
        if word and word not in stop_words and len(word) > 3:
            common_words[word] = common_words.get(word, 0) + 1
    
    # Get most common words as "topics"
    analytics["common_topics"] = sorted(
        [(word, count) for word, count in common_words.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Very basic sentiment analysis
    positive_words = {"good", "great", "excellent", "amazing", "wonderful", "like", "love", 
                     "enjoy", "happy", "glad", "positive", "fantastic", "awesome"}
    negative_words = {"bad", "awful", "terrible", "horrible", "dislike", "hate", "sad", 
                     "unhappy", "negative", "disappointed", "frustrating", "annoying"}
    
    positive_count = sum(all_content.count(word) for word in positive_words)
    negative_count = sum(all_content.count(word) for word in negative_words)
    total_count = positive_count + negative_count
    
    if total_count > 0:
        analytics["sentiment_analysis"] = {
            "positive": positive_count / total_count,
            "negative": negative_count / total_count,
            "overall": "positive" if positive_count > negative_count else "negative"
        }
    else:
        analytics["sentiment_analysis"] = {
            "positive": 0,
            "negative": 0,
            "overall": "neutral"
        }
    
    # Simple conversation patterns
    question_count = sum(1 for msg in user_messages if "?" in msg.get("content", ""))
    statement_count = len(user_messages) - question_count
    
    analytics["conversation_patterns"] = {
        "questions": question_count,
        "statements": statement_count,
        "question_ratio": question_count / len(user_messages)
    }
    
    return analytics
```

To use this in our CLI, add a command to show analytics:

```python
def main():
    # ... existing code ...
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print(f"\n{args.name}: Goodbye! It was nice talking with you.")
            break
        
        if user_input.lower() == 'analytics':
            # Display conversation analytics
            analytics = assistant.get_conversation_analytics()
            print("\n=== Conversation Analytics ===")
            for key, value in analytics.items():
                if key == "common_topics":
                    print(f"Common topics: {', '.join([t[0] for t in value[:5]])}")
                elif key == "sentiment_analysis":
                    print(f"Sentiment: {value.get('overall', 'neutral')}")
                    print(f"  - Positive: {value.get('positive', 0):.2f}")
                    print(f"  - Negative: {value.get('negative', 0):.2f}")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value}")
            continue
        
        response = assistant.generate_response(user_input)
        print(f"\n{args.name}: {response}")
    
    # ... rest of the code ...
```

## Key Features

Our chatbot assistant demonstrates several key AgentMem features:

1. **Multi-type Memory Integration**:
   - Semantic memory for user profiles and preferences
   - Episodic memory for conversation history
   - Procedural memory for response patterns

2. **Persistence**:
   - Memory survives across multiple sessions
   - Builds knowledge about users over time

3. **Learning and Adaptation**:
   - Learns user preferences automatically
   - Can be taught new response patterns
   - Adapts responses based on conversation history

4. **Analytics**:
   - Tracks conversation patterns
   - Performs simple sentiment analysis
   - Identifies common topics

## Benefits of Using AgentMem

1. **Improved User Experience**:
   - Personalized responses based on user preferences
   - Contextual awareness of conversation history
   - Adaptive learning from interactions

2. **Developer Productivity**:
   - Memory handled automatically by AgentMem
   - Reusable components for different memory types
   - Built-in persistence eliminates need for database setup

3. **Performance**:
   - Thread-safe operations for multi-user environments
   - Efficient memory access patterns
   - Vector search for semantic understanding

## Further Enhancements

This case study can be extended in several ways:

1. **NLP Integration**:
   - Add a more sophisticated NLP system for intent recognition
   - Improve topic extraction with entity recognition
   - Enhance sentiment analysis with ML models

2. **Multi-user Support**:
   - Add proper user authentication
   - Scale for concurrent conversations
   - Implement privacy controls

3. **Knowledge Integration**:
   - Connect to external knowledge bases
   - Add web search capabilities
   - Implement fact validation

4. **UI Integration**:
   - Create a web interface
   - Add mobile client
   - Enable voice interaction

## Conclusion

This case study demonstrates how AgentMem can be used to create a chatbot assistant with memory capabilities. By leveraging different memory types, the assistant can provide personalized, contextually relevant responses that improve over time.

The integration of semantic, episodic, and procedural memory creates a more human-like interaction experience, allowing the assistant to remember user preferences, recall conversation history, and apply appropriate response patterns.

With AgentMem's built-in persistence and vector search capabilities, the assistant can maintain knowledge across sessions and understand the semantic meaning behind user queries, making it more helpful and engaging.