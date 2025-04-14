# Building a Chatbot with Memory

This tutorial will guide you through creating a chatbot that uses AgentMem to remember past interactions and provide more intelligent responses.

## Overview

A memory-enabled chatbot can provide more personalized and contextually relevant responses by:

1. Remembering user preferences and details (semantic memory)
2. Recalling conversation history (episodic memory)
3. Following response patterns and templates (procedural memory)

In this tutorial, we'll build a simple command-line chatbot that demonstrates these capabilities.

## Prerequisites

- AgentMem installed (`pip install agentmem`)
- Basic understanding of Python
- Familiarity with basic AgentMem concepts

## Step 1: Setting Up the Chatbot

First, let's create a basic chatbot class that integrates all three memory types:

```python
import uuid
from datetime import datetime
from agentmem.semantic import SemanticMemory
from agentmem.episodic import EpisodicMemory
from agentmem.procedural import ProceduralMemory

class MemoryChatbot:
    def __init__(self, name="MemBot", persistence_dir=None):
        """Initialize the chatbot with memory systems."""
        self.name = name
        self.user_id = None
        
        # Initialize memory systems
        self.semantic_memory = SemanticMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.episodic_memory = EpisodicMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.procedural_memory = ProceduralMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        # Initialize conversation tracking
        self.conversation_id = str(uuid.uuid4())
        print(f"{self.name} initialized with conversation ID: {self.conversation_id}")
```

## Step 2: Adding User Identification

Let's add methods to identify and remember users:

```python
def identify_user(self, user_id, user_name=None):
    """Identify the current user."""
    self.user_id = user_id
    
    # Check if we know this user
    known_users = self.semantic_memory.query(
        user_id, 
        category="user_profile"
    )
    
    if known_users:
        user_profile = known_users[0]
        print(f"Welcome back, {user_profile['metadata'].get('name', user_id)}!")
        return True
    elif user_name:
        # Create new user profile
        self.semantic_memory.create(
            content=f"User profile for {user_name}",
            category="user_profile",
            tags=["user", "profile"],
            metadata={
                "user_id": user_id,
                "name": user_name,
                "first_seen": datetime.now().isoformat()
            }
        )
        print(f"Nice to meet you, {user_name}!")
        return True
    else:
        print(f"Hello! I don't think we've met before. What's your name?")
        return False
```

## Step 3: Recording Conversations

Now, let's add methods to record and recall conversations:

```python
def remember_message(self, message, from_user=True, importance=5):
    """Record a message in episodic memory."""
    timestamp = datetime.now()
    
    # Determine importance based on content
    if from_user:
        # Simple heuristic: longer messages or messages with question marks are more important
        if len(message) > 100 or "?" in message:
            importance = min(importance + 2, 10)
    
    # Create the memory entry
    memory_id = self.episodic_memory.create(
        content=message,
        timestamp=timestamp,
        context={
            "conversation_id": self.conversation_id,
            "user_id": self.user_id if from_user else None,
            "from_user": from_user,
            "from_bot": not from_user
        },
        importance=importance
    )
    
    return memory_id

def get_recent_conversation(self, limit=5):
    """Retrieve recent conversation history."""
    # Query for messages in the current conversation
    messages = self.episodic_memory.query(
        "",  # Empty query matches all
        context_keys=["conversation_id"]
    )
    
    # Filter for current conversation
    current_conversation = [
        msg for msg in messages 
        if msg["context"]["conversation_id"] == self.conversation_id
    ]
    
    # Sort by timestamp (older messages first)
    current_conversation.sort(key=lambda x: x["timestamp"])
    
    # Return most recent messages
    return current_conversation[-limit:]
```

## Step 4: Learning Facts About Users

Let's add methods to remember information about users:

```python
def learn_user_fact(self, fact, from_user=True):
    """Store facts about the user."""
    if not self.user_id:
        return None
    
    # Create the memory entry
    fact_id = self.semantic_memory.create(
        content=fact,
        category="user_facts",
        tags=["user", self.user_id],
        metadata={
            "user_id": self.user_id,
            "from_user": from_user
        }
    )
    
    return fact_id

def get_user_facts(self):
    """Retrieve facts about the current user."""
    if not self.user_id:
        return []
    
    # Query for facts about this user
    facts = self.semantic_memory.query(
        "",  # Empty query matches all
        tags=[self.user_id]
    )
    
    return facts
```

## Step 5: Adding Response Patterns

Now, let's add procedural memory for different response patterns:

```python
def add_response_pattern(self, trigger, response_template, steps=None):
    """Add a response pattern to procedural memory."""
    if steps is None:
        steps = [
            "Identify the intent in the user message",
            f"If the intent matches '{trigger}', use this response",
            f"Format the response using the template: '{response_template}'",
            "Personalize the response with user-specific information if available"
        ]
    
    pattern_id = self.procedural_memory.create(
        content=f"Response pattern for {trigger}",
        task=f"Respond to {trigger}",
        steps=steps,
        domains=["conversation", "response_patterns"],
        prerequisites=[],
        metadata={
            "trigger": trigger,
            "template": response_template
        }
    )
    
    return pattern_id

def find_response_pattern(self, message):
    """Find a suitable response pattern for the message."""
    # Use vector search to find the most relevant response pattern
    patterns = self.procedural_memory.query(
        message, 
        domain="response_patterns",
        use_vector=True
    )
    
    if patterns:
        return patterns[0]
    
    return None
```

## Step 6: Generating Responses

Now, let's implement the core response generation logic:

```python
def generate_response(self, message):
    """Generate a response to the user's message."""
    # First, remember this message
    self.remember_message(message, from_user=True)
    
    # Extract potential facts about the user
    if "my name is" in message.lower() or "i am called" in message.lower():
        name_info = message.lower().replace("my name is", "").replace("i am called", "").strip()
        if name_info:
            self.learn_user_fact(f"User's name is {name_info}")
    
    elif "i like" in message.lower():
        like_info = message.lower().replace("i like", "").strip()
        if like_info:
            self.learn_user_fact(f"User likes {like_info}")
    
    elif "i don't like" in message.lower() or "i do not like" in message.lower():
        dislike_info = message.lower().replace("i don't like", "").replace("i do not like", "").strip()
        if dislike_info:
            self.learn_user_fact(f"User doesn't like {dislike_info}")
    
    # Look for relevant response patterns
    pattern = self.find_response_pattern(message)
    
    if pattern:
        # Use the pattern to generate a response
        template = pattern["metadata"].get("template", "I understand about {topic}.")
        
        # Extract potential topic from message
        topic = message.strip().strip("?!.")
        if len(topic) > 30:
            topic = topic[:30] + "..."
        
        # Format the template
        response = template.format(topic=topic, user=self.user_id)
    else:
        # Get recent conversation for context
        recent = self.get_recent_conversation(3)
        
        # Get user facts for personalization
        facts = self.get_user_facts()
        
        # Simple fallback response strategy
        if "?" in message:
            response = "That's an interesting question. Let me think about it."
        elif len(message) < 10:
            response = "Could you tell me more about that?"
        elif "thank" in message.lower():
            response = "You're welcome! Is there anything else I can help with?"
        elif any(word in message.lower() for word in ["hello", "hi", "hey"]):
            response = f"Hello! How can I help you today?"
        else:
            response = "I see. Please tell me more about your thoughts on this."
    
    # Remember bot's response
    self.remember_message(response, from_user=False)
    
    return response
```

## Step 7: Creating the Chatbot Interface

Finally, let's create a simple command-line interface for our chatbot:

```python
def chat_loop(self):
    """Run the main chat loop."""
    print(f"\n{self.name}: Hello! I'm {self.name}. What's your name?")
    
    user_identified = False
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"\n{self.name}: Goodbye! It was nice talking to you.")
            break
        
        if not user_identified:
            # First message is expected to be the user's name
            user_identified = self.identify_user(str(uuid.uuid4()), user_input)
            continue
        
        response = self.generate_response(user_input)
        print(f"\n{self.name}: {response}")
```

## Step 8: Initializing with Pre-defined Response Patterns

Let's initialize our chatbot with some pre-defined response patterns:

```python
def initialize_patterns(self):
    """Add initial response patterns."""
    # Greeting patterns
    self.add_response_pattern(
        "greeting", 
        "Hello there! How can I help you today?"
    )
    
    self.add_response_pattern(
        "farewell", 
        "Goodbye! It was nice talking to you."
    )
    
    # Question patterns
    self.add_response_pattern(
        "what is your name", 
        f"My name is {self.name}. I'm a chatbot with memory capabilities."
    )
    
    self.add_response_pattern(
        "how are you", 
        "I'm functioning well, thank you! How are you doing today?"
    )
    
    # Topic patterns
    self.add_response_pattern(
        "weather", 
        "I don't have real-time weather data, but I hope the weather is pleasant wherever you are!"
    )
    
    self.add_response_pattern(
        "tell me about yourself", 
        f"I'm {self.name}, a memory-enabled chatbot built with AgentMem. I can remember our conversations and learn about you."
    )
    
    print(f"Initialized {self.procedural_memory.query('', domain='response_patterns').__len__()} response patterns")
```

## Step 9: Putting It All Together

Now, let's create our complete chatbot application:

```python
# memory_chatbot.py
import uuid
from datetime import datetime
from agentmem.semantic import SemanticMemory
from agentmem.episodic import EpisodicMemory
from agentmem.procedural import ProceduralMemory
from agentmem import configure_logging, LogLevel

# Configure logging
configure_logging(LogLevel.INFO)

class MemoryChatbot:
    def __init__(self, name="MemBot", persistence_dir=None):
        """Initialize the chatbot with memory systems."""
        self.name = name
        self.user_id = None
        
        # Initialize memory systems
        self.semantic_memory = SemanticMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.episodic_memory = EpisodicMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.procedural_memory = ProceduralMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        # Initialize conversation tracking
        self.conversation_id = str(uuid.uuid4())
        print(f"{self.name} initialized with conversation ID: {self.conversation_id}")
        
        # Add initial response patterns
        self.initialize_patterns()
    
    def identify_user(self, user_id, user_name=None):
        """Identify the current user."""
        self.user_id = user_id
        
        # Check if we know this user
        known_users = self.semantic_memory.query(
            user_id, 
            category="user_profile"
        )
        
        if known_users:
            user_profile = known_users[0]
            print(f"Welcome back, {user_profile['metadata'].get('name', user_id)}!")
            return True
        elif user_name:
            # Create new user profile
            self.semantic_memory.create(
                content=f"User profile for {user_name}",
                category="user_profile",
                tags=["user", "profile"],
                metadata={
                    "user_id": user_id,
                    "name": user_name,
                    "first_seen": datetime.now().isoformat()
                }
            )
            print(f"Nice to meet you, {user_name}!")
            return True
        else:
            print(f"Hello! I don't think we've met before. What's your name?")
            return False
    
    def remember_message(self, message, from_user=True, importance=5):
        """Record a message in episodic memory."""
        timestamp = datetime.now()
        
        # Determine importance based on content
        if from_user:
            # Simple heuristic: longer messages or messages with question marks are more important
            if len(message) > 100 or "?" in message:
                importance = min(importance + 2, 10)
        
        # Create the memory entry
        memory_id = self.episodic_memory.create(
            content=message,
            timestamp=timestamp,
            context={
                "conversation_id": self.conversation_id,
                "user_id": self.user_id if from_user else None,
                "from_user": from_user,
                "from_bot": not from_user
            },
            importance=importance
        )
        
        return memory_id

    def get_recent_conversation(self, limit=5):
        """Retrieve recent conversation history."""
        # Query for messages in the current conversation
        messages = self.episodic_memory.query(
            "",  # Empty query matches all
            context_keys=["conversation_id"]
        )
        
        # Filter for current conversation
        current_conversation = [
            msg for msg in messages 
            if msg["context"]["conversation_id"] == self.conversation_id
        ]
        
        # Sort by timestamp (older messages first)
        current_conversation.sort(key=lambda x: x["timestamp"])
        
        # Return most recent messages
        return current_conversation[-limit:]
    
    def learn_user_fact(self, fact, from_user=True):
        """Store facts about the user."""
        if not self.user_id:
            return None
        
        # Create the memory entry
        fact_id = self.semantic_memory.create(
            content=fact,
            category="user_facts",
            tags=["user", self.user_id],
            metadata={
                "user_id": self.user_id,
                "from_user": from_user
            }
        )
        
        return fact_id

    def get_user_facts(self):
        """Retrieve facts about the current user."""
        if not self.user_id:
            return []
        
        # Query for facts about this user
        facts = self.semantic_memory.query(
            "",  # Empty query matches all
            tags=[self.user_id]
        )
        
        return facts
    
    def add_response_pattern(self, trigger, response_template, steps=None):
        """Add a response pattern to procedural memory."""
        if steps is None:
            steps = [
                "Identify the intent in the user message",
                f"If the intent matches '{trigger}', use this response",
                f"Format the response using the template: '{response_template}'",
                "Personalize the response with user-specific information if available"
            ]
        
        pattern_id = self.procedural_memory.create(
            content=f"Response pattern for {trigger}",
            task=f"Respond to {trigger}",
            steps=steps,
            domains=["conversation", "response_patterns"],
            prerequisites=[],
            metadata={
                "trigger": trigger,
                "template": response_template
            }
        )
        
        return pattern_id

    def find_response_pattern(self, message):
        """Find a suitable response pattern for the message."""
        # Use vector search to find the most relevant response pattern
        patterns = self.procedural_memory.query(
            message, 
            domain="response_patterns",
            use_vector=True
        )
        
        if patterns:
            return patterns[0]
        
        return None
    
    def generate_response(self, message):
        """Generate a response to the user's message."""
        # First, remember this message
        self.remember_message(message, from_user=True)
        
        # Extract potential facts about the user
        if "my name is" in message.lower() or "i am called" in message.lower():
            name_info = message.lower().replace("my name is", "").replace("i am called", "").strip()
            if name_info:
                self.learn_user_fact(f"User's name is {name_info}")
        
        elif "i like" in message.lower():
            like_info = message.lower().replace("i like", "").strip()
            if like_info:
                self.learn_user_fact(f"User likes {like_info}")
        
        elif "i don't like" in message.lower() or "i do not like" in message.lower():
            dislike_info = message.lower().replace("i don't like", "").replace("i do not like", "").strip()
            if dislike_info:
                self.learn_user_fact(f"User doesn't like {dislike_info}")
        
        # Look for relevant response patterns
        pattern = self.find_response_pattern(message)
        
        if pattern:
            # Use the pattern to generate a response
            template = pattern["metadata"].get("template", "I understand about {topic}.")
            
            # Extract potential topic from message
            topic = message.strip().strip("?!.")
            if len(topic) > 30:
                topic = topic[:30] + "..."
            
            # Format the template
            response = template.format(topic=topic, user=self.user_id)
        else:
            # Get recent conversation for context
            recent = self.get_recent_conversation(3)
            
            # Get user facts for personalization
            facts = self.get_user_facts()
            
            # Simple fallback response strategy
            if "?" in message:
                response = "That's an interesting question. Let me think about it."
            elif len(message) < 10:
                response = "Could you tell me more about that?"
            elif "thank" in message.lower():
                response = "You're welcome! Is there anything else I can help with?"
            elif any(word in message.lower() for word in ["hello", "hi", "hey"]):
                response = f"Hello! How can I help you today?"
            else:
                response = "I see. Please tell me more about your thoughts on this."
        
        # Remember bot's response
        self.remember_message(response, from_user=False)
        
        return response
    
    def initialize_patterns(self):
        """Add initial response patterns."""
        # Greeting patterns
        self.add_response_pattern(
            "greeting", 
            "Hello there! How can I help you today?"
        )
        
        self.add_response_pattern(
            "farewell", 
            "Goodbye! It was nice talking to you."
        )
        
        # Question patterns
        self.add_response_pattern(
            "what is your name", 
            f"My name is {self.name}. I'm a chatbot with memory capabilities."
        )
        
        self.add_response_pattern(
            "how are you", 
            "I'm functioning well, thank you! How are you doing today?"
        )
        
        # Topic patterns
        self.add_response_pattern(
            "weather", 
            "I don't have real-time weather data, but I hope the weather is pleasant wherever you are!"
        )
        
        self.add_response_pattern(
            "tell me about yourself", 
            f"I'm {self.name}, a memory-enabled chatbot built with AgentMem. I can remember our conversations and learn about you."
        )
        
        print(f"Initialized {self.procedural_memory.query('', domain='response_patterns').__len__()} response patterns")
    
    def chat_loop(self):
        """Run the main chat loop."""
        print(f"\n{self.name}: Hello! I'm {self.name}. What's your name?")
        
        user_identified = False
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print(f"\n{self.name}: Goodbye! It was nice talking to you.")
                break
            
            if not user_identified:
                # First message is expected to be the user's name
                user_identified = self.identify_user(str(uuid.uuid4()), user_input)
                continue
            
            response = self.generate_response(user_input)
            print(f"\n{self.name}: {response}")

# Run the chatbot if executed directly
if __name__ == "__main__":
    # Create a chatbot with persistence
    import os
    
    # Create the persistence directory if it doesn't exist
    os.makedirs("./chatbot_memory", exist_ok=True)
    
    # Initialize the chatbot
    chatbot = MemoryChatbot(
        name="MemoryBot",
        persistence_dir="./chatbot_memory"
    )
    
    # Start the chat loop
    try:
        chatbot.chat_loop()
    except KeyboardInterrupt:
        print("\nExiting chatbot...")
```

## Step 10: Testing the Chatbot

Save the code above in a file named `memory_chatbot.py`, and run it:

```bash
python memory_chatbot.py
```

You should see output similar to:

```
MemoryBot initialized with conversation ID: d8f9a7b6-c5e4-4d3e-b2a1-0c9f8e7d6b5a
Initialized 6 response patterns

MemoryBot: Hello! I'm MemoryBot. What's your name?
You: Alice
Nice to meet you, Alice!

You: What's your name?

MemoryBot: My name is MemoryBot. I'm a chatbot with memory capabilities.

You: I like chocolate

MemoryBot: I see. Please tell me more about your thoughts on this.

You: What do I like?

MemoryBot: That's an interesting question. Let me think about it.

You: Tell me about yourself

MemoryBot: I'm MemoryBot, a memory-enabled chatbot built with AgentMem. I can remember our conversations and learn about you.

You: How are you today?

MemoryBot: I'm functioning well, thank you! How are you doing today?

You: bye

MemoryBot: Goodbye! It was nice talking to you.
```

## Step 11: Enhancing the Chatbot

Now that we have a basic memory-enabled chatbot, we can enhance it in several ways:

### Adding More Personalization

```python
def personalize_response(self, response):
    """Personalize a response based on user facts."""
    # Get user facts
    facts = self.get_user_facts()
    
    if not facts:
        return response
    
    # Extract user preferences
    likes = []
    dislikes = []
    name = None
    
    for fact in facts:
        content = fact["content"].lower()
        if "user's name is" in content:
            name = content.replace("user's name is", "").strip()
        elif "user likes" in content:
            likes.append(content.replace("user likes", "").strip())
        elif "user doesn't like" in content:
            dislikes.append(content.replace("user doesn't like", "").strip())
    
    # Personalize the response
    personalized = response
    
    # Add name if available
    if name and "you" in response.lower():
        personalized = personalized.replace("you", name, 1)
    
    # Add a reference to a like if relevant
    if likes and any(like in response.lower() for like in likes):
        for like in likes:
            if like in response.lower():
                personalized += f" I remember you mentioned you like {like}."
                break
    
    return personalized
```

### Adding Memory Recall Commands

```python
def process_recall_command(self, message):
    """Process commands to recall information."""
    if message.lower().startswith("what do you know about me"):
        facts = self.get_user_facts()
        if facts:
            fact_texts = [f"- {fact['content']}" for fact in facts]
            return "Here's what I know about you:\n" + "\n".join(fact_texts)
        else:
            return "I don't have any specific information about you yet. Feel free to tell me more about yourself!"
    
    elif message.lower().startswith("what did i say about"):
        topic = message.lower().replace("what did i say about", "").strip()
        if topic:
            # Search episodic memory for user messages mentioning the topic
            related_messages = self.episodic_memory.query(
                topic,
                use_vector=True
            )
            
            # Filter for messages from the user
            user_messages = [
                msg for msg in related_messages 
                if msg["context"].get("from_user", False)
            ]
            
            if user_messages:
                message_texts = [f"- {msg['content']}" for msg in user_messages[:3]]
                return f"You've mentioned {topic} before. Here are some things you said:\n" + "\n".join(message_texts)
            else:
                return f"I don't recall you mentioning anything about {topic}."
        
    return None
```

### Adding Learning Capabilities

```python
def learn_response_pattern(self, trigger, response):
    """Learn a new response pattern from interaction."""
    # Check if this is a teaching instruction
    if trigger.lower().startswith("when i say") and "you say" in trigger.lower():
        try:
            # Extract the trigger and response
            parts = trigger.lower().split("you say")
            user_trigger = parts[0].replace("when i say", "").strip()
            user_response = response.strip()
            
            if user_trigger and user_response:
                self.add_response_pattern(user_trigger, user_response)
                return f"I've learned that when you say '{user_trigger}', I should respond with '{user_response}'."
        except Exception as e:
            return f"I couldn't learn that pattern: {str(e)}"
    
    return None
```

## Step 12: Future Improvements

Here are some ideas for further enhancing your memory-enabled chatbot:

1. **Sentiment Analysis**: Track user sentiment over time to adjust responses accordingly.

2. **Context-Aware Responses**: Use more of the conversation history to generate contextually appropriate responses.

3. **Topic Tracking**: Maintain a model of the current conversation topic to provide more coherent discussions.

4. **Personalization Over Time**: Gradually build a more detailed user model based on interactions.

5. **Multi-User Support**: Expand the chatbot to handle multiple users with separate memory spaces.

6. **Integration with External Knowledge**: Connect the chatbot to external APIs or knowledge bases.

## Conclusion

In this tutorial, we've built a memory-enabled chatbot using AgentMem that can:

- Remember user information using semantic memory
- Track conversation history using episodic memory
- Apply response patterns using procedural memory
- Learn from interactions and improve over time

The combination of these memory systems creates a more personalized and intelligent chatbot experience. By leveraging AgentMem's persistence capabilities, the chatbot can maintain its knowledge across sessions, creating a more consistent user experience.

For more advanced applications, you might consider integrating this memory-enabled chatbot with:

- Natural language understanding models for better intent recognition
- Knowledge graphs for more structured information storage
- Machine learning for response generation and personalization

AgentMem provides the foundational memory systems that make these advanced capabilities possible.