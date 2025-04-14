"""
Advanced example demonstrating an intelligent agent using all three memory types.

This example shows a conversational assistant that uses:
1. Semantic Memory for storing facts about the world
2. Episodic Memory for remembering past interactions
3. Procedural Memory for knowledge about performing tasks

It demonstrates:
- Integration of all memory types
- Persistence across sessions
- Vector-based semantic search
- Building context-aware AI agent systems
"""

import os
import random
import shutil
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

from agentmem import EpisodicMemory, ProceduralMemory, SemanticMemory


class AssistantAgent:
    """
    An intelligent assistant agent powered by multiple memory systems.
    
    This agent demonstrates the use of all three memory types working together:
    - Semantic memory for factual knowledge
    - Episodic memory for conversation history
    - Procedural memory for task-oriented knowledge
    
    The agent can:
    1. Answer factual questions using semantic memory
    2. Remember past conversations using episodic memory 
    3. Provide step-by-step instructions using procedural memory
    4. Learn new information and save it to memory
    """
    
    def __init__(
        self,
        name: str = "Assistant",
        persistence_dir: Optional[str] = None,
        use_vector_search: bool = True,
        vector_db_dir: Optional[str] = None
    ):
        """
        Initialize the assistant agent with memory systems.
        
        Args:
            name: Name of the assistant
            persistence_dir: Directory for persistent storage (None for in-memory only)
            use_vector_search: Whether to use vector-based search 
            vector_db_dir: Directory for vector database (defaults to persistence_dir)
        """
        self.name = name
        self.persistence_dir = persistence_dir
        self.vector_db_dir = vector_db_dir or persistence_dir
        
        # Create memory paths if needed
        if persistence_dir and not os.path.exists(persistence_dir):
            os.makedirs(persistence_dir, exist_ok=True)
            
        if self.vector_db_dir and not os.path.exists(self.vector_db_dir):
            os.makedirs(self.vector_db_dir, exist_ok=True)
        
        # Initialize memory systems
        self.semantic_memory = SemanticMemory(
            persistence=persistence_dir,
            vector_search=use_vector_search,
            vector_db_path=self.vector_db_dir
        )
        
        self.episodic_memory = EpisodicMemory(
            persistence=persistence_dir,
            vector_search=use_vector_search,
            vector_db_path=self.vector_db_dir
        )
        
        self.procedural_memory = ProceduralMemory(
            persistence=persistence_dir,
            vector_search=use_vector_search,
            vector_db_path=self.vector_db_dir
        )
        
        # Internal state
        self.session_id = str(random.randint(1000, 9999))
        self.current_user = None
        self.current_context = {"session_id": self.session_id}
        
        # Initialize with some default knowledge if memories are empty
        self._initialize_knowledge()
    
    def _initialize_knowledge(self):
        """Initialize the agent with some default knowledge if memories are empty."""
        # Check if semantic memory is empty
        if not list(self.semantic_memory._storage.keys()):
            print(f"Initializing {self.name} with default knowledge...")
            
            # Add some basic facts to semantic memory
            self.semantic_memory.create(
                content="Python is a high-level programming language created by Guido van Rossum",
                category="technology",
                tags=["programming", "languages", "python"]
            )
            
            self.semantic_memory.create(
                content="Machine learning is a subset of AI that uses data to train algorithms",
                category="technology",
                tags=["AI", "machine learning", "data science"]
            )
            
            self.semantic_memory.create(
                content="The Earth is the third planet from the Sun",
                category="science",
                tags=["astronomy", "planets", "solar system"]
            )
            
            # Add some procedures to procedural memory
            self.procedural_memory.create(
                content="How to create a Python virtual environment",
                task="Create a virtual environment",
                steps=[
                    "Open a terminal or command prompt",
                    "Navigate to your project directory",
                    "Run 'python -m venv venv' to create a virtual environment",
                    "Activate the environment with 'source venv/bin/activate' (Linux/Mac) or 'venv\\Scripts\\activate' (Windows)",
                    "Install packages with pip as needed"
                ],
                domains=["programming", "python", "setup"]
            )
            
            self.procedural_memory.create(
                content="How to push changes to GitHub",
                task="Push changes to GitHub",
                steps=[
                    "Add files to staging with 'git add .'",
                    "Commit changes with 'git commit -m \"Your message\"'",
                    "Push to remote with 'git push origin main'",
                    "Verify changes on the GitHub website"
                ],
                domains=["programming", "git", "github"]
            )
    
    def remember_interaction(
        self,
        user_id: str,
        message: str,
        importance: int = 5,
        topic: Optional[str] = None
    ) -> UUID:
        """
        Store a user interaction in episodic memory.
        
        Args:
            user_id: Identifier for the user
            message: Content of the user's message
            importance: Subjective importance of this interaction (1-10)
            topic: Optional topic categorization
            
        Returns:
            UUID: Memory ID of the stored interaction
        """
        # Update current user and context
        self.current_user = user_id
        if topic:
            self.current_context["topic"] = topic
        
        # Store in episodic memory
        interaction_id = self.episodic_memory.create(
            content=f"User {user_id}: {message}",
            timestamp=datetime.now(),
            importance=importance,
            context={
                "user_id": user_id,
                "session_id": self.session_id,
                "topic": topic or "general"
            }
        )
        
        return interaction_id
    
    def learn_fact(
        self,
        fact: str,
        category: str = "general",
        tags: Optional[List[str]] = None
    ) -> UUID:
        """
        Learn a new fact and store it in semantic memory.
        
        Args:
            fact: The factual content to store
            category: Category for the fact
            tags: Optional tags for classification
            
        Returns:
            UUID: Memory ID of the stored fact
        """
        tags = tags or []
        fact_id = self.semantic_memory.create(
            content=fact,
            category=category,
            tags=tags
        )
        
        # Remember that we learned this fact
        self.episodic_memory.create(
            content=f"I learned: {fact}",
            timestamp=datetime.now(),
            importance=6,
            context={
                "action": "learning",
                "memory_type": "semantic",
                "memory_id": str(fact_id),
                "session_id": self.session_id
            }
        )
        
        return fact_id
    
    def learn_procedure(
        self,
        task: str,
        steps: List[str],
        domains: Optional[List[str]] = None,
        prerequisites: Optional[List[str]] = None
    ) -> UUID:
        """
        Learn a new procedure and store it in procedural memory.
        
        Args:
            task: Description of the task
            steps: Sequence of steps to perform the task
            domains: Optional list of applicable domains
            prerequisites: Optional list of prerequisites
            
        Returns:
            UUID: Memory ID of the stored procedure
        """
        domains = domains or ["general"]
        prerequisites = prerequisites or []
        
        procedure_id = self.procedural_memory.create(
            content=f"How to {task}",
            task=task,
            steps=steps,
            domains=domains,
            prerequisites=prerequisites
        )
        
        # Remember that we learned this procedure
        self.episodic_memory.create(
            content=f"I learned a procedure: {task}",
            timestamp=datetime.now(),
            importance=7,
            context={
                "action": "learning",
                "memory_type": "procedural",
                "memory_id": str(procedure_id),
                "session_id": self.session_id
            }
        )
        
        return procedure_id
    
    def recall_user_history(
        self,
        user_id: str,
        days: int = 30,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Recall past interactions with a specific user.
        
        Args:
            user_id: Identifier for the user
            days: Number of days back to search
            max_results: Maximum results to return
            
        Returns:
            List[Dict]: Relevant past interactions
        """
        start_time = datetime.now() - timedelta(days=days)
        
        past_interactions = self.episodic_memory.query(
            "",  # Empty query matches all content
            start_time=start_time,
            end_time=datetime.now(),
            context_keys=["user_id"]
        )
        
        # Filter for specific user
        user_interactions = [
            memory for memory in past_interactions
            if memory["context"]["user_id"] == user_id
        ]
        
        # Sort by most recent first and limit results
        return user_interactions[:max_results]
    
    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        use_vector: bool = True
    ) -> List[Dict]:
        """
        Search for facts in semantic memory.
        
        Args:
            query: Search query
            category: Optional category filter
            use_vector: Whether to use vector search
            
        Returns:
            List[Dict]: Matching facts
        """
        facts = self.semantic_memory.query(
            query,
            category=category,
            use_vector=use_vector
        )
        
        return facts
    
    def get_procedure(
        self,
        task_query: str,
        domain: Optional[str] = None,
        use_vector: bool = True
    ) -> Optional[Dict]:
        """
        Find a procedure for performing a specific task.
        
        Args:
            task_query: Description of the desired task
            domain: Optional domain filter
            use_vector: Whether to use vector search
            
        Returns:
            Optional[Dict]: Best matching procedure or None
        """
        procedures = self.procedural_memory.query(
            task_query,
            domain=domain,
            use_vector=use_vector
        )
        
        if not procedures:
            return None
            
        # If using vector search, procedures should already be sorted by relevance
        return procedures[0]
    
    def process_message(
        self,
        user_id: str,
        message: str
    ) -> str:
        """
        Process a user message and generate a response.
        
        This method demonstrates the full workflow of:
        1. Storing the user message in episodic memory
        2. Using all three memory types to generate a response
        3. Identifying the intent type (factual, procedural, or contextual)
        
        Args:
            user_id: Identifier for the user
            message: The user's input message
            
        Returns:
            str: The agent's response
        """
        # Store the interaction in episodic memory
        self.remember_interaction(user_id, message)
        
        # Basic intent classification (in a real system, use a proper NLU component)
        message_lower = message.lower()
        
        # Check for learning intent
        if "remember that" in message_lower or "learn this fact" in message_lower:
            # Extract the fact (simplified extraction)
            fact = message.split("that", 1)[1].strip() if "that" in message else message
            fact_id = self.learn_fact(fact)
            return f"I've learned this new fact: '{fact}'"
            
        # Check for procedural knowledge request
        if "how to" in message_lower or "how do I" in message_lower or "steps to" in message_lower:
            procedure = self.get_procedure(message)
            
            if procedure:
                steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(procedure["steps"])])
                return f"Here's how to {procedure['task']}:\n\n{steps_text}"
            else:
                return "I don't know how to do that yet. Would you like to teach me?"
        
        # Check for recall of past interactions
        if "what did we talk about" in message_lower or "previous conversation" in message_lower:
            past = self.recall_user_history(user_id)
            
            if past:
                past_summary = "\n".join([f"- {interaction['content']}" for interaction in past[:3]])
                return f"Here's what we discussed recently:\n{past_summary}"
            else:
                return "We haven't had any significant conversations recently that I can recall."
        
        # Default to knowledge search
        facts = self.search_knowledge(message)
        
        if facts:
            fact = facts[0]
            return f"I know that {fact['content']}"
        else:
            return "I don't have specific information about that. Would you like me to learn about it?"


def run_demo():
    """Run a demonstration of the assistant agent with persistence."""
    # Create temporary directories for the demo
    temp_dir = tempfile.mkdtemp()
    persistence_dir = os.path.join(temp_dir, "assistant_memory")
    vector_dir = os.path.join(temp_dir, "assistant_vectors")
    
    try:
        print("=== AgentMem Assistant Demo ===")
        print(f"Using temporary persistence directory: {persistence_dir}")
        
        # Create the assistant with persistence
        assistant = AssistantAgent(
            name="MemAgent",
            persistence_dir=persistence_dir,
            use_vector_search=True,
            vector_db_dir=vector_dir
        )
        
        print(f"\n{assistant.name} is initialized and ready to chat.")
        print("Type 'exit' to end the conversation.\n")
        
        # Simulate a conversation
        user_id = f"user{random.randint(100, 999)}"
        
        while True:
            user_input = input(f"You: ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print(f"\n{assistant.name}: Goodbye! I'll remember our conversation.")
                break
                
            response = assistant.process_message(user_id, user_input)
            print(f"\n{assistant.name}: {response}\n")
        
        # Demonstrate persistence by creating a new assistant instance
        print("\n=== Demonstrating Memory Persistence ===")
        print("Creating a new assistant instance that will load the same memories...\n")
        
        assistant2 = AssistantAgent(
            name="MemAgent",
            persistence_dir=persistence_dir,
            use_vector_search=True,
            vector_db_dir=vector_dir
        )
        
        # Recall the conversation history to demonstrate persistence
        history = assistant2.recall_user_history(user_id)
        
        print(f"The new assistant instance remembers {len(history)} interactions from your conversation:")
        for i, memory in enumerate(history, 1):
            content = memory["content"]
            timestamp = memory["timestamp"].strftime("%H:%M:%S")
            print(f"{i}. [{timestamp}] {content}")
            
    finally:
        # Clean up
        print("\nCleaning up temporary directories...")
        shutil.rmtree(temp_dir)
        print("Demo completed.")


if __name__ == "__main__":
    run_demo()