# Implementing a Knowledge Base with AgentMem

This tutorial will guide you through building a flexible knowledge base system using AgentMem, focusing primarily on semantic memory with support from episodic and procedural memories.

## Overview

A knowledge base is a structured repository of information that can be queried for facts, relationships, and procedures. By implementing a knowledge base with AgentMem, you can create systems that:

1. Store and retrieve factual information (semantic memory)
2. Track how knowledge was acquired and changes over time (episodic memory)
3. Store procedures for knowledge application (procedural memory)

## Prerequisites

- AgentMem installed (`pip install agentmem[vector]`)
- Basic understanding of Python
- Familiarity with basic AgentMem concepts

## Step 1: Setting Up the Knowledge Base Structure

First, let's create a basic knowledge base class that integrates all three memory types:

```python
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from agentmem.semantic import SemanticMemory
from agentmem.episodic import EpisodicMemory
from agentmem.procedural import ProceduralMemory
from agentmem import configure_logging, LogLevel

# Configure logging
configure_logging(LogLevel.INFO)

class KnowledgeBase:
    def __init__(self, name="AgentMem KB", persistence_dir=None):
        """Initialize the knowledge base with memory systems."""
        self.name = name
        
        # Initialize memory systems
        self.facts = SemanticMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.history = EpisodicMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.procedures = ProceduralMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        # Initialize tracking information
        self.kb_id = str(uuid.uuid4())
        print(f"Knowledge Base '{name}' initialized with ID: {self.kb_id}")
```

## Step 2: Adding Core Knowledge Operations

Now, let's implement the core knowledge base operations:

```python
def add_fact(self, fact: str, category: str = "general", 
             tags: List[str] = None, source: str = None,
             confidence: float = 1.0) -> str:
    """
    Add a fact to the knowledge base.
    
    Args:
        fact: The factual statement to store
        category: Category for organization
        tags: List of tags for classification
        source: Source of the information
        confidence: Confidence level (0.0 to 1.0)
        
    Returns:
        ID of the created fact
    """
    if tags is None:
        tags = []
    
    # Create the fact in semantic memory
    fact_id = self.facts.create(
        content=fact,
        category=category,
        tags=tags,
        metadata={
            "source": source,
            "confidence": confidence,
            "added_at": datetime.now().isoformat()
        }
    )
    
    # Record the addition in episodic memory
    self.history.create(
        content=f"Added fact: {fact}",
        timestamp=datetime.now(),
        context={
            "operation": "add_fact",
            "fact_id": str(fact_id),
            "category": category,
            "source": source
        },
        importance=7 if confidence > 0.8 else 5
    )
    
    return str(fact_id)

def get_fact(self, fact_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific fact by ID.
    
    Args:
        fact_id: ID of the fact to retrieve
        
    Returns:
        The fact with all metadata
    """
    try:
        # Record the retrieval in history
        self.history.create(
            content=f"Retrieved fact with ID: {fact_id}",
            timestamp=datetime.now(),
            context={
                "operation": "get_fact",
                "fact_id": fact_id
            },
            importance=3
        )
        
        # Return the fact
        return self.facts.read(uuid.UUID(fact_id))
    except KeyError:
        print(f"Fact with ID {fact_id} not found")
        return None
```

## Step 3: Implementing Knowledge Queries

Let's add methods to search and retrieve facts:

```python
def query_facts(self, query: str, category: str = None, 
                tags: List[str] = None, min_confidence: float = 0.0,
                use_vector: bool = True, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Query facts in the knowledge base.
    
    Args:
        query: Search query
        category: Filter by category
        tags: Filter by tags
        min_confidence: Minimum confidence level
        use_vector: Whether to use vector search
        limit: Maximum number of results
        
    Returns:
        List of matching facts
    """
    # Prepare query parameters
    params = {
        "use_vector": use_vector,
        "n_results": limit
    }
    
    if category:
        params["category"] = category
        
    if tags:
        params["tags"] = tags
    
    # Execute the query
    results = self.facts.query(query, **params)
    
    # Filter by confidence
    if min_confidence > 0:
        results = [
            r for r in results 
            if r.get("metadata", {}).get("confidence", 0) >= min_confidence
        ]
    
    # Limit results
    results = results[:limit]
    
    # Record the query in history
    self.history.create(
        content=f"Queried facts: '{query}'",
        timestamp=datetime.now(),
        context={
            "operation": "query_facts",
            "query": query,
            "category": category,
            "tags": tags,
            "results_count": len(results)
        },
        importance=4
    )
    
    return results

def ask(self, question: str) -> List[Dict[str, Any]]:
    """
    Ask a question to the knowledge base.
    
    Args:
        question: The question to ask
        
    Returns:
        List of relevant facts that might answer the question
    """
    # Always use vector search for questions
    results = self.query_facts(question, use_vector=True, limit=5)
    
    # Record the question in history
    self.history.create(
        content=f"Asked question: '{question}'",
        timestamp=datetime.now(),
        context={
            "operation": "ask",
            "question": question,
            "results_count": len(results)
        },
        importance=6
    )
    
    return results
```

## Step 4: Managing Knowledge Structure

Now, let's add methods to organize and structure the knowledge:

```python
def create_category(self, name: str, description: str) -> None:
    """
    Create a category for organizing facts.
    
    Args:
        name: Category name
        description: Category description
    """
    # Categories are implemented as semantic memories with a special flag
    self.facts.create(
        content=description,
        category="system",
        tags=["category", "structure"],
        metadata={
            "type": "category",
            "name": name,
            "created_at": datetime.now().isoformat()
        }
    )
    
    print(f"Created category: {name}")

def create_tag(self, name: str, description: str) -> None:
    """
    Create a tag for classifying facts.
    
    Args:
        name: Tag name
        description: Tag description
    """
    # Tags are implemented as semantic memories with a special flag
    self.facts.create(
        content=description,
        category="system",
        tags=["tag", "structure"],
        metadata={
            "type": "tag",
            "name": name,
            "created_at": datetime.now().isoformat()
        }
    )
    
    print(f"Created tag: {name}")

def get_categories(self) -> List[str]:
    """
    Get all categories in the knowledge base.
    
    Returns:
        List of category names
    """
    category_facts = self.facts.query("", category="system", tags=["category"])
    return [f["metadata"]["name"] for f in category_facts if "name" in f.get("metadata", {})]

def get_tags(self) -> List[str]:
    """
    Get all tags in the knowledge base.
    
    Returns:
        List of tag names
    """
    tag_facts = self.facts.query("", category="system", tags=["tag"])
    return [f["metadata"]["name"] for f in tag_facts if "name" in f.get("metadata", {})]
```

## Step 5: Adding Relationships Between Facts

Let's implement relationships between facts:

```python
def add_relationship(self, subject_id: str, predicate: str, object_id: str, 
                    confidence: float = 1.0, source: str = None) -> str:
    """
    Add a relationship between two facts.
    
    Args:
        subject_id: ID of the subject fact
        predicate: Relationship type (e.g., "is_a", "part_of")
        object_id: ID of the object fact
        confidence: Confidence level
        source: Source of the relationship
        
    Returns:
        ID of the relationship
    """
    # Verify that both facts exist
    try:
        subject = self.facts.read(uuid.UUID(subject_id))
        object_fact = self.facts.read(uuid.UUID(object_id))
    except KeyError:
        print("One or both facts do not exist")
        return None
    
    # Create the relationship as a fact
    relationship_id = self.facts.create(
        content=f"{subject_id} {predicate} {object_id}",
        category="relationship",
        tags=["relationship", predicate],
        metadata={
            "type": "relationship",
            "subject_id": subject_id,
            "predicate": predicate,
            "object_id": object_id,
            "confidence": confidence,
            "source": source,
            "added_at": datetime.now().isoformat()
        }
    )
    
    # Record the relationship creation
    self.history.create(
        content=f"Added relationship: {subject['content']} {predicate} {object_fact['content']}",
        timestamp=datetime.now(),
        context={
            "operation": "add_relationship",
            "relationship_id": str(relationship_id),
            "subject_id": subject_id,
            "predicate": predicate,
            "object_id": object_id
        },
        importance=6
    )
    
    return str(relationship_id)

def get_relationships(self, fact_id: str, predicate: str = None) -> List[Dict[str, Any]]:
    """
    Get relationships involving a fact.
    
    Args:
        fact_id: ID of the fact
        predicate: Optional filter by relationship type
        
    Returns:
        List of relationships
    """
    # Query relationships
    query_params = {
        "category": "relationship",
        "tags": ["relationship"]
    }
    
    if predicate:
        query_params["tags"].append(predicate)
    
    all_relationships = self.facts.query(fact_id, **query_params)
    
    # Filter for relationships involving the specified fact
    relationships = [
        r for r in all_relationships 
        if r.get("metadata", {}).get("subject_id") == fact_id or 
           r.get("metadata", {}).get("object_id") == fact_id
    ]
    
    return relationships
```

## Step 6: Implementing Inference Procedures

Now, let's add procedures for reasoning about the knowledge:

```python
def add_inference_rule(self, name: str, description: str, 
                      conditions: List[str], actions: List[str],
                      domain: str = "general") -> str:
    """
    Add an inference rule to the knowledge base.
    
    Args:
        name: Rule name
        description: Rule description
        conditions: List of conditions for rule application
        actions: List of actions to take when conditions are met
        domain: Domain where the rule applies
        
    Returns:
        ID of the created rule
    """
    rule_id = self.procedures.create(
        content=description,
        task=name,
        steps=actions,
        prerequisites=conditions,
        domains=[domain, "inference"],
        metadata={
            "type": "inference_rule",
            "created_at": datetime.now().isoformat()
        }
    )
    
    # Record the rule creation
    self.history.create(
        content=f"Added inference rule: {name}",
        timestamp=datetime.now(),
        context={
            "operation": "add_inference_rule",
            "rule_id": str(rule_id),
            "rule_name": name,
            "domain": domain
        },
        importance=7
    )
    
    return str(rule_id)

def apply_inference(self, fact_ids: List[str], domain: str = "general") -> List[Dict[str, Any]]:
    """
    Apply inference rules to facts.
    
    Args:
        fact_ids: IDs of facts to reason about
        domain: Domain of rules to apply
        
    Returns:
        List of inferred facts
    """
    # Get facts
    facts = []
    for fact_id in fact_ids:
        try:
            fact = self.facts.read(uuid.UUID(fact_id))
            facts.append(fact)
        except KeyError:
            print(f"Fact with ID {fact_id} not found")
    
    if not facts:
        return []
    
    # Get applicable inference rules
    rules = self.procedures.query("", domain=domain)
    rules = [r for r in rules if r.get("metadata", {}).get("type") == "inference_rule"]
    
    # Apply rules (simple implementation)
    inferred_facts = []
    
    for rule in rules:
        # Check prerequisites (very simple check, would be more complex in practice)
        if all(any(prereq.lower() in fact["content"].lower() for fact in facts) 
               for prereq in rule["prerequisites"]):
            
            # Apply the rule
            for step in rule["steps"]:
                if step.startswith("INFER:"):
                    inference = step[6:].strip()
                    
                    # Create the inferred fact
                    inferred_fact_id = self.add_fact(
                        inference,
                        category="inferred",
                        tags=["inferred", domain],
                        source=f"Inference rule: {rule['task']}",
                        confidence=0.7  # Lower confidence for inferred facts
                    )
                    
                    inferred_fact = self.get_fact(inferred_fact_id)
                    inferred_facts.append(inferred_fact)
    
    # Record the inference operation
    self.history.create(
        content=f"Applied inference rules in domain: {domain}",
        timestamp=datetime.now(),
        context={
            "operation": "apply_inference",
            "fact_ids": fact_ids,
            "domain": domain,
            "inferred_facts_count": len(inferred_facts)
        },
        importance=5
    )
    
    return inferred_facts
```

## Step 7: Tracking Knowledge Provenance

Let's add methods to track the provenance (origin and history) of knowledge:

```python
def get_fact_history(self, fact_id: str) -> List[Dict[str, Any]]:
    """
    Get the history of a fact.
    
    Args:
        fact_id: ID of the fact
        
    Returns:
        List of events related to the fact
    """
    # Query historical events related to this fact
    events = self.history.query(
        fact_id,
        context_keys=["fact_id", "operation"]
    )
    
    # Sort events by timestamp
    events.sort(key=lambda e: e["timestamp"])
    
    return events

def get_knowledge_source_stats(self) -> Dict[str, int]:
    """
    Get statistics on knowledge sources.
    
    Returns:
        Dictionary mapping sources to fact counts
    """
    # Get all facts
    all_facts = self.facts.query("")
    
    # Count facts by source
    source_counts = {}
    for fact in all_facts:
        source = fact.get("metadata", {}).get("source")
        if source:
            source_counts[source] = source_counts.get(source, 0) + 1
    
    return source_counts
```

## Step 8: Implementing Knowledge Base Persistence

Let's add methods to save and load the entire knowledge base:

```python
def save(self) -> None:
    """Save the knowledge base to disk."""
    print(f"Saving knowledge base '{self.name}'...")
    
    # Save all memory systems
    self.facts.save_all()
    self.history.save_all()
    self.procedures.save_all()
    
    print(f"Knowledge base saved successfully")

def load(self) -> None:
    """Load the knowledge base from disk."""
    print(f"Loading knowledge base '{self.name}'...")
    
    # Load all memory systems
    self.facts.load_all()
    self.history.load_all()
    self.procedures.load_all()
    
    # Get statistics
    fact_count = len(self.facts.query(""))
    category_count = len(self.get_categories())
    tag_count = len(self.get_tags())
    
    print(f"Knowledge base loaded successfully with {fact_count} facts, "
          f"{category_count} categories, and {tag_count} tags")

def get_statistics(self) -> Dict[str, Any]:
    """
    Get statistics about the knowledge base.
    
    Returns:
        Dictionary of statistics
    """
    stats = {
        "name": self.name,
        "id": self.kb_id,
        "facts_count": len(self.facts.query("")),
        "categories_count": len(self.get_categories()),
        "tags_count": len(self.get_tags()),
        "relationships_count": len(self.facts.query("", category="relationship")),
        "inference_rules_count": len(self.procedures.query("", domain="inference")),
        "operations_count": len(self.history.query("")),
        "creation_time": self.history.query("", limit=1)[0]["timestamp"] if self.history.query("", limit=1) else "Unknown"
    }
    
    return stats
```

## Step 9: Putting It All Together

Now, let's create our complete knowledge base application:

```python
# knowledge_base.py
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from agentmem.semantic import SemanticMemory
from agentmem.episodic import EpisodicMemory
from agentmem.procedural import ProceduralMemory
from agentmem import configure_logging, LogLevel

# Configure logging
configure_logging(LogLevel.INFO)

class KnowledgeBase:
    def __init__(self, name="AgentMem KB", persistence_dir=None):
        """Initialize the knowledge base with memory systems."""
        self.name = name
        
        # Initialize memory systems
        self.facts = SemanticMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.history = EpisodicMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.procedures = ProceduralMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        # Initialize tracking information
        self.kb_id = str(uuid.uuid4())
        print(f"Knowledge Base '{name}' initialized with ID: {self.kb_id}")

    def add_fact(self, fact: str, category: str = "general", 
                 tags: List[str] = None, source: str = None,
                 confidence: float = 1.0) -> str:
        """
        Add a fact to the knowledge base.
        
        Args:
            fact: The factual statement to store
            category: Category for organization
            tags: List of tags for classification
            source: Source of the information
            confidence: Confidence level (0.0 to 1.0)
            
        Returns:
            ID of the created fact
        """
        if tags is None:
            tags = []
        
        # Create the fact in semantic memory
        fact_id = self.facts.create(
            content=fact,
            category=category,
            tags=tags,
            metadata={
                "source": source,
                "confidence": confidence,
                "added_at": datetime.now().isoformat()
            }
        )
        
        # Record the addition in episodic memory
        self.history.create(
            content=f"Added fact: {fact}",
            timestamp=datetime.now(),
            context={
                "operation": "add_fact",
                "fact_id": str(fact_id),
                "category": category,
                "source": source
            },
            importance=7 if confidence > 0.8 else 5
        )
        
        return str(fact_id)

    def get_fact(self, fact_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific fact by ID.
        
        Args:
            fact_id: ID of the fact to retrieve
            
        Returns:
            The fact with all metadata
        """
        try:
            # Record the retrieval in history
            self.history.create(
                content=f"Retrieved fact with ID: {fact_id}",
                timestamp=datetime.now(),
                context={
                    "operation": "get_fact",
                    "fact_id": fact_id
                },
                importance=3
            )
            
            # Return the fact
            return self.facts.read(uuid.UUID(fact_id))
        except KeyError:
            print(f"Fact with ID {fact_id} not found")
            return None

    def query_facts(self, query: str, category: str = None, 
                    tags: List[str] = None, min_confidence: float = 0.0,
                    use_vector: bool = True, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query facts in the knowledge base.
        
        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            min_confidence: Minimum confidence level
            use_vector: Whether to use vector search
            limit: Maximum number of results
            
        Returns:
            List of matching facts
        """
        # Prepare query parameters
        params = {
            "use_vector": use_vector,
            "n_results": limit
        }
        
        if category:
            params["category"] = category
            
        if tags:
            params["tags"] = tags
        
        # Execute the query
        results = self.facts.query(query, **params)
        
        # Filter by confidence
        if min_confidence > 0:
            results = [
                r for r in results 
                if r.get("metadata", {}).get("confidence", 0) >= min_confidence
            ]
        
        # Limit results
        results = results[:limit]
        
        # Record the query in history
        self.history.create(
            content=f"Queried facts: '{query}'",
            timestamp=datetime.now(),
            context={
                "operation": "query_facts",
                "query": query,
                "category": category,
                "tags": tags,
                "results_count": len(results)
            },
            importance=4
        )
        
        return results

    def ask(self, question: str) -> List[Dict[str, Any]]:
        """
        Ask a question to the knowledge base.
        
        Args:
            question: The question to ask
            
        Returns:
            List of relevant facts that might answer the question
        """
        # Always use vector search for questions
        results = self.query_facts(question, use_vector=True, limit=5)
        
        # Record the question in history
        self.history.create(
            content=f"Asked question: '{question}'",
            timestamp=datetime.now(),
            context={
                "operation": "ask",
                "question": question,
                "results_count": len(results)
            },
            importance=6
        )
        
        return results

    def create_category(self, name: str, description: str) -> None:
        """
        Create a category for organizing facts.
        
        Args:
            name: Category name
            description: Category description
        """
        # Categories are implemented as semantic memories with a special flag
        self.facts.create(
            content=description,
            category="system",
            tags=["category", "structure"],
            metadata={
                "type": "category",
                "name": name,
                "created_at": datetime.now().isoformat()
            }
        )
        
        print(f"Created category: {name}")

    def create_tag(self, name: str, description: str) -> None:
        """
        Create a tag for classifying facts.
        
        Args:
            name: Tag name
            description: Tag description
        """
        # Tags are implemented as semantic memories with a special flag
        self.facts.create(
            content=description,
            category="system",
            tags=["tag", "structure"],
            metadata={
                "type": "tag",
                "name": name,
                "created_at": datetime.now().isoformat()
            }
        )
        
        print(f"Created tag: {name}")

    def get_categories(self) -> List[str]:
        """
        Get all categories in the knowledge base.
        
        Returns:
            List of category names
        """
        category_facts = self.facts.query("", category="system", tags=["category"])
        return [f["metadata"]["name"] for f in category_facts if "name" in f.get("metadata", {})]

    def get_tags(self) -> List[str]:
        """
        Get all tags in the knowledge base.
        
        Returns:
            List of tag names
        """
        tag_facts = self.facts.query("", category="system", tags=["tag"])
        return [f["metadata"]["name"] for f in tag_facts if "name" in f.get("metadata", {})]

    def add_relationship(self, subject_id: str, predicate: str, object_id: str, 
                        confidence: float = 1.0, source: str = None) -> str:
        """
        Add a relationship between two facts.
        
        Args:
            subject_id: ID of the subject fact
            predicate: Relationship type (e.g., "is_a", "part_of")
            object_id: ID of the object fact
            confidence: Confidence level
            source: Source of the relationship
            
        Returns:
            ID of the relationship
        """
        # Verify that both facts exist
        try:
            subject = self.facts.read(uuid.UUID(subject_id))
            object_fact = self.facts.read(uuid.UUID(object_id))
        except KeyError:
            print("One or both facts do not exist")
            return None
        
        # Create the relationship as a fact
        relationship_id = self.facts.create(
            content=f"{subject_id} {predicate} {object_id}",
            category="relationship",
            tags=["relationship", predicate],
            metadata={
                "type": "relationship",
                "subject_id": subject_id,
                "predicate": predicate,
                "object_id": object_id,
                "confidence": confidence,
                "source": source,
                "added_at": datetime.now().isoformat()
            }
        )
        
        # Record the relationship creation
        self.history.create(
            content=f"Added relationship: {subject['content']} {predicate} {object_fact['content']}",
            timestamp=datetime.now(),
            context={
                "operation": "add_relationship",
                "relationship_id": str(relationship_id),
                "subject_id": subject_id,
                "predicate": predicate,
                "object_id": object_id
            },
            importance=6
        )
        
        return str(relationship_id)

    def get_relationships(self, fact_id: str, predicate: str = None) -> List[Dict[str, Any]]:
        """
        Get relationships involving a fact.
        
        Args:
            fact_id: ID of the fact
            predicate: Optional filter by relationship type
            
        Returns:
            List of relationships
        """
        # Query relationships
        query_params = {
            "category": "relationship",
            "tags": ["relationship"]
        }
        
        if predicate:
            query_params["tags"].append(predicate)
        
        all_relationships = self.facts.query(fact_id, **query_params)
        
        # Filter for relationships involving the specified fact
        relationships = [
            r for r in all_relationships 
            if r.get("metadata", {}).get("subject_id") == fact_id or 
               r.get("metadata", {}).get("object_id") == fact_id
        ]
        
        return relationships

    def add_inference_rule(self, name: str, description: str, 
                          conditions: List[str], actions: List[str],
                          domain: str = "general") -> str:
        """
        Add an inference rule to the knowledge base.
        
        Args:
            name: Rule name
            description: Rule description
            conditions: List of conditions for rule application
            actions: List of actions to take when conditions are met
            domain: Domain where the rule applies
            
        Returns:
            ID of the created rule
        """
        rule_id = self.procedures.create(
            content=description,
            task=name,
            steps=actions,
            prerequisites=conditions,
            domains=[domain, "inference"],
            metadata={
                "type": "inference_rule",
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Record the rule creation
        self.history.create(
            content=f"Added inference rule: {name}",
            timestamp=datetime.now(),
            context={
                "operation": "add_inference_rule",
                "rule_id": str(rule_id),
                "rule_name": name,
                "domain": domain
            },
            importance=7
        )
        
        return str(rule_id)

    def apply_inference(self, fact_ids: List[str], domain: str = "general") -> List[Dict[str, Any]]:
        """
        Apply inference rules to facts.
        
        Args:
            fact_ids: IDs of facts to reason about
            domain: Domain of rules to apply
            
        Returns:
            List of inferred facts
        """
        # Get facts
        facts = []
        for fact_id in fact_ids:
            try:
                fact = self.facts.read(uuid.UUID(fact_id))
                facts.append(fact)
            except KeyError:
                print(f"Fact with ID {fact_id} not found")
        
        if not facts:
            return []
        
        # Get applicable inference rules
        rules = self.procedures.query("", domain=domain)
        rules = [r for r in rules if r.get("metadata", {}).get("type") == "inference_rule"]
        
        # Apply rules (simple implementation)
        inferred_facts = []
        
        for rule in rules:
            # Check prerequisites (very simple check, would be more complex in practice)
            if all(any(prereq.lower() in fact["content"].lower() for fact in facts) 
                   for prereq in rule["prerequisites"]):
                
                # Apply the rule
                for step in rule["steps"]:
                    if step.startswith("INFER:"):
                        inference = step[6:].strip()
                        
                        # Create the inferred fact
                        inferred_fact_id = self.add_fact(
                            inference,
                            category="inferred",
                            tags=["inferred", domain],
                            source=f"Inference rule: {rule['task']}",
                            confidence=0.7  # Lower confidence for inferred facts
                        )
                        
                        inferred_fact = self.get_fact(inferred_fact_id)
                        inferred_facts.append(inferred_fact)
        
        # Record the inference operation
        self.history.create(
            content=f"Applied inference rules in domain: {domain}",
            timestamp=datetime.now(),
            context={
                "operation": "apply_inference",
                "fact_ids": fact_ids,
                "domain": domain,
                "inferred_facts_count": len(inferred_facts)
            },
            importance=5
        )
        
        return inferred_facts

    def get_fact_history(self, fact_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of a fact.
        
        Args:
            fact_id: ID of the fact
            
        Returns:
            List of events related to the fact
        """
        # Query historical events related to this fact
        events = self.history.query(
            fact_id,
            context_keys=["fact_id", "operation"]
        )
        
        # Sort events by timestamp
        events.sort(key=lambda e: e["timestamp"])
        
        return events

    def get_knowledge_source_stats(self) -> Dict[str, int]:
        """
        Get statistics on knowledge sources.
        
        Returns:
            Dictionary mapping sources to fact counts
        """
        # Get all facts
        all_facts = self.facts.query("")
        
        # Count facts by source
        source_counts = {}
        for fact in all_facts:
            source = fact.get("metadata", {}).get("source")
            if source:
                source_counts[source] = source_counts.get(source, 0) + 1
        
        return source_counts

    def save(self) -> None:
        """Save the knowledge base to disk."""
        print(f"Saving knowledge base '{self.name}'...")
        
        # Save all memory systems
        self.facts.save_all()
        self.history.save_all()
        self.procedures.save_all()
        
        print(f"Knowledge base saved successfully")

    def load(self) -> None:
        """Load the knowledge base from disk."""
        print(f"Loading knowledge base '{self.name}'...")
        
        # Load all memory systems
        self.facts.load_all()
        self.history.load_all()
        self.procedures.load_all()
        
        # Get statistics
        fact_count = len(self.facts.query(""))
        category_count = len(self.get_categories())
        tag_count = len(self.get_tags())
        
        print(f"Knowledge base loaded successfully with {fact_count} facts, "
              f"{category_count} categories, and {tag_count} tags")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary of statistics
        """
        stats = {
            "name": self.name,
            "id": self.kb_id,
            "facts_count": len(self.facts.query("")),
            "categories_count": len(self.get_categories()),
            "tags_count": len(self.get_tags()),
            "relationships_count": len(self.facts.query("", category="relationship")),
            "inference_rules_count": len(self.procedures.query("", domain="inference")),
            "operations_count": len(self.history.query("")),
            "creation_time": self.history.query("", limit=1)[0]["timestamp"] if self.history.query("", limit=1) else "Unknown"
        }
        
        return stats

# Example usage
if __name__ == "__main__":
    import os
    
    # Create the persistence directory if it doesn't exist
    os.makedirs("./knowledge_base", exist_ok=True)
    
    # Initialize the knowledge base
    kb = KnowledgeBase(
        name="Biology KB",
        persistence_dir="./knowledge_base"
    )
    
    # Create some categories and tags
    kb.create_category("animal", "Facts about animals")
    kb.create_category("plant", "Facts about plants")
    kb.create_tag("mammal", "Warm-blooded vertebrate animals")
    kb.create_tag("tree", "Woody perennial plants")
    
    # Add some facts
    dog_id = kb.add_fact(
        "Dogs are domesticated mammals of the family Canidae.",
        category="animal",
        tags=["mammal"],
        source="Encyclopedia",
        confidence=0.95
    )
    
    wolf_id = kb.add_fact(
        "Wolves are wild carnivorous mammals of the family Canidae.",
        category="animal",
        tags=["mammal"],
        source="Encyclopedia",
        confidence=0.95
    )
    
    oak_id = kb.add_fact(
        "Oak trees are flowering plants of the genus Quercus.",
        category="plant",
        tags=["tree"],
        source="Botany Textbook",
        confidence=0.90
    )
    
    # Add relationships
    kb.add_relationship(
        dog_id, "evolved_from", wolf_id,
        confidence=0.85,
        source="Scientific Research"
    )
    
    # Add an inference rule
    kb.add_inference_rule(
        "Mammal classification",
        "Infer that mammals are animals",
        conditions=["mammal"],
        actions=[
            "INFER: All mammals are animals with hair or fur that feed their young with milk"
        ],
        domain="biology"
    )
    
    # Apply inference
    inferred = kb.apply_inference([dog_id, wolf_id], domain="biology")
    
    # Query the knowledge base
    print("\nQuery for 'dog':")
    dog_results = kb.query_facts("dog")
    for result in dog_results:
        print(f"- {result['content']} (Confidence: {result['metadata'].get('confidence', 'N/A')})")
    
    # Ask a question
    print("\nAsking 'What is the relationship between dogs and wolves?'")
    answer = kb.ask("What is the relationship between dogs and wolves?")
    for result in answer:
        print(f"- {result['content']} (Confidence: {result['metadata'].get('confidence', 'N/A')})")
    
    # Get facts by relationship
    print("\nRelationships for dog:")
    dog_relationships = kb.get_relationships(dog_id)
    for rel in dog_relationships:
        print(f"- {rel['content']}")
    
    # Get statistics
    stats = kb.get_statistics()
    print("\nKnowledge Base Statistics:")
    for key, value in stats.items():
        print(f"- {key}: {value}")
    
    # Save the knowledge base
    kb.save()
```

## Step 10: Advanced Knowledge Base Features

Let's explore some advanced features we can add to our knowledge base:

### Handling Contradictory Information

```python
def handle_contradiction(self, fact1_id: str, fact2_id: str, resolution: str = None) -> str:
    """
    Handle contradictory facts in the knowledge base.
    
    Args:
        fact1_id: ID of first contradictory fact
        fact2_id: ID of second contradictory fact
        resolution: Optional resolution statement
        
    Returns:
        ID of the contradiction record
    """
    try:
        fact1 = self.facts.read(uuid.UUID(fact1_id))
        fact2 = self.facts.read(uuid.UUID(fact2_id))
    except KeyError:
        print("One or both facts do not exist")
        return None
    
    # Create a contradiction record
    contradiction_id = self.facts.create(
        content=f"Contradiction between two facts: \n1. {fact1['content']}\n2. {fact2['content']}",
        category="contradiction",
        tags=["contradiction", "issue"],
        metadata={
            "type": "contradiction",
            "fact1_id": fact1_id,
            "fact2_id": fact2_id,
            "resolution": resolution,
            "status": "resolved" if resolution else "unresolved",
            "created_at": datetime.now().isoformat()
        }
    )
    
    # If there's a resolution, update the confidence of both facts
    if resolution:
        # Lower confidence in contradicted facts
        for fact_id in [fact1_id, fact2_id]:
            fact = self.facts.read(uuid.UUID(fact_id))
            old_confidence = fact.get("metadata", {}).get("confidence", 1.0)
            
            self.facts.update(
                uuid.UUID(fact_id),
                metadata={
                    "confidence": old_confidence * 0.7,  # Reduce confidence
                    "contradicted": True,
                    "contradiction_id": str(contradiction_id)
                }
            )
        
        # Add the resolution as a new fact
        resolution_id = self.add_fact(
            resolution,
            category="resolution",
            tags=["resolution", "contradiction"],
            source="Contradiction resolution",
            confidence=0.8
        )
        
        # Update the contradiction record
        self.facts.update(
            contradiction_id,
            metadata={
                "resolution_id": resolution_id,
                "status": "resolved"
            }
        )
    
    return str(contradiction_id)
```

### Implementing Knowledge Import/Export

```python
def export_knowledge(self, filepath: str, format_type: str = "json") -> None:
    """
    Export knowledge base to a file.
    
    Args:
        filepath: Path to export file
        format_type: Format type (json, csv, etc.)
    """
    import json
    
    if format_type.lower() != "json":
        print(f"Format {format_type} not supported. Using JSON.")
    
    # Get all facts
    all_facts = self.facts.query("")
    
    # Prepare export data
    export_data = {
        "metadata": {
            "name": self.name,
            "id": self.kb_id,
            "export_time": datetime.now().isoformat(),
            "fact_count": len(all_facts)
        },
        "facts": all_facts,
        "categories": [
            {
                "name": name,
                "description": next((f["content"] for f in self.facts.query(name, category="system", tags=["category"]) if f), "")
            } for name in self.get_categories()
        ],
        "tags": [
            {
                "name": name,
                "description": next((f["content"] for f in self.facts.query(name, category="system", tags=["tag"]) if f), "")
            } for name in self.get_tags()
        ]
    }
    
    # Write to file
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"Exported {len(all_facts)} facts to {filepath}")

def import_knowledge(self, filepath: str, format_type: str = "json") -> int:
    """
    Import knowledge from a file.
    
    Args:
        filepath: Path to import file
        format_type: Format type (json, csv, etc.)
        
    Returns:
        Number of facts imported
    """
    import json
    
    if format_type.lower() != "json":
        print(f"Format {format_type} not supported. Using JSON.")
    
    try:
        with open(filepath, 'r') as f:
            import_data = json.load(f)
        
        # Import categories and tags first
        for category in import_data.get("categories", []):
            if category.get("name") and category.get("description"):
                self.create_category(category["name"], category["description"])
        
        for tag in import_data.get("tags", []):
            if tag.get("name") and tag.get("description"):
                self.create_tag(tag["name"], tag["description"])
        
        # Import facts
        imported_count = 0
        id_mapping = {}  # Maps old IDs to new IDs
        
        for fact in import_data.get("facts", []):
            if "content" in fact:
                category = fact.get("category", "general")
                tags = fact.get("tags", [])
                metadata = fact.get("metadata", {})
                
                new_id = self.add_fact(
                    fact["content"],
                    category=category,
                    tags=tags,
                    source=metadata.get("source", "Imported"),
                    confidence=metadata.get("confidence", 0.7)
                )
                
                # Store ID mapping
                if "id" in fact:
                    id_mapping[fact["id"]] = new_id
                
                imported_count += 1
        
        print(f"Imported {imported_count} facts from {filepath}")
        return imported_count
        
    except Exception as e:
        print(f"Error importing knowledge: {str(e)}")
        return 0
```

## Step 11: Creating a Knowledge Explorer

Let's create a simple command-line interface for exploring the knowledge base:

```python
def run_explorer(self):
    """Run an interactive explorer for the knowledge base."""
    print(f"\nKnowledge Base Explorer: {self.name}")
    print("Type 'help' for available commands.")
    
    while True:
        command = input("\nKB> ").strip()
        
        if command.lower() in ["exit", "quit", "q"]:
            print("Exiting explorer...")
            break
        
        elif command.lower() in ["help", "h", "?"]:
            print("\nAvailable commands:")
            print("  add <fact>                  - Add a new fact")
            print("  add-category <name> <desc>  - Add a new category")
            print("  add-tag <name> <desc>       - Add a new tag")
            print("  ask <question>              - Ask a question")
            print("  categories                  - List all categories")
            print("  facts [category] [limit]    - List facts, optionally filtered by category")
            print("  get <fact-id>               - Get a specific fact by ID")
            print("  help                        - Show this help message")
            print("  query <search-term>         - Search for facts")
            print("  relate <id1> <rel> <id2>    - Add a relationship between facts")
            print("  save                        - Save the knowledge base")
            print("  stats                       - Show knowledge base statistics")
            print("  tags                        - List all tags")
            print("  exit                        - Exit the explorer")
        
        elif command.lower().startswith("add "):
            fact = command[4:].strip()
            category = input("Category [general]: ").strip() or "general"
            tags_input = input("Tags (comma-separated): ").strip()
            tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
            source = input("Source: ").strip()
            confidence = float(input("Confidence [0.0-1.0]: ").strip() or "1.0")
            
            fact_id = self.add_fact(
                fact,
                category=category,
                tags=tags,
                source=source,
                confidence=confidence
            )
            
            print(f"Added fact with ID: {fact_id}")
        
        elif command.lower().startswith("add-category "):
            parts = command[13:].strip().split(" ", 1)
            if len(parts) >= 2:
                name, description = parts
                self.create_category(name, description)
            else:
                print("Usage: add-category <name> <description>")
        
        elif command.lower().startswith("add-tag "):
            parts = command[8:].strip().split(" ", 1)
            if len(parts) >= 2:
                name, description = parts
                self.create_tag(name, description)
            else:
                print("Usage: add-tag <name> <description>")
        
        elif command.lower().startswith("ask "):
            question = command[4:].strip()
            results = self.ask(question)
            
            print(f"\nTop answers to: '{question}'")
            for i, result in enumerate(results, 1):
                score = result.get("similarity_score", "N/A")
                print(f"{i}. {result['content']} (Relevance: {score:.2f if isinstance(score, float) else score})")
                print(f"   Category: {result.get('category', 'N/A')}")
                print(f"   Confidence: {result.get('metadata', {}).get('confidence', 'N/A')}")
                if i < len(results):
                    print()
        
        elif command.lower() == "categories":
            categories = self.get_categories()
            print("\nCategories:")
            for category in categories:
                print(f"- {category}")
        
        elif command.lower().startswith("facts"):
            parts = command.split()
            category = parts[1] if len(parts) > 1 else None
            limit = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 10
            
            params = {"limit": limit}
            if category:
                params["category"] = category
            
            facts = self.query_facts("", **params)
            
            print(f"\nFacts" + (f" in category '{category}'" if category else "") + f" (showing {len(facts)} of {len(self.facts.query(''))})")
            for i, fact in enumerate(facts, 1):
                print(f"{i}. [{fact['id']}] {fact['content']}")
                print(f"   Category: {fact.get('category', 'N/A')}")
                print(f"   Tags: {', '.join(fact.get('tags', []))}")
                if i < len(facts):
                    print()
        
        elif command.lower().startswith("get "):
            fact_id = command[4:].strip()
            fact = self.get_fact(fact_id)
            
            if fact:
                print(f"\nFact ID: {fact['id']}")
                print(f"Content: {fact['content']}")
                print(f"Category: {fact.get('category', 'N/A')}")
                print(f"Tags: {', '.join(fact.get('tags', []))}")
                print(f"Created: {fact.get('created_at', 'N/A')}")
                print(f"Updated: {fact.get('updated_at', 'N/A')}")
                print(f"Source: {fact.get('metadata', {}).get('source', 'N/A')}")
                print(f"Confidence: {fact.get('metadata', {}).get('confidence', 'N/A')}")
                
                # Show relationships
                relationships = self.get_relationships(fact_id)
                if relationships:
                    print("\nRelationships:")
                    for rel in relationships:
                        print(f"- {rel['content']}")
        
        elif command.lower().startswith("query "):
            search_term = command[6:].strip()
            use_vector = "y" in input("Use vector search? [y/n]: ").lower()
            
            results = self.query_facts(search_term, use_vector=use_vector)
            
            print(f"\nResults for query: '{search_term}'")
            for i, result in enumerate(results, 1):
                score = result.get("similarity_score", "N/A")
                print(f"{i}. [{result['id']}] {result['content']}")
                print(f"   Category: {result.get('category', 'N/A')}")
                print(f"   Score: {score:.2f if isinstance(score, float) else score}")
                if i < len(results):
                    print()
        
        elif command.lower().startswith("relate "):
            parts = command[7:].strip().split()
            if len(parts) >= 3:
                subject_id, predicate, object_id = parts[0], parts[1], parts[2]
                source = input("Source: ").strip()
                confidence = float(input("Confidence [0.0-1.0]: ").strip() or "1.0")
                
                rel_id = self.add_relationship(
                    subject_id,
                    predicate,
                    object_id,
                    confidence=confidence,
                    source=source
                )
                
                if rel_id:
                    print(f"Added relationship with ID: {rel_id}")
            else:
                print("Usage: relate <subject-id> <predicate> <object-id>")
        
        elif command.lower() == "save":
            self.save()
        
        elif command.lower() == "stats":
            stats = self.get_statistics()
            
            print("\nKnowledge Base Statistics:")
            for key, value in stats.items():
                print(f"- {key}: {value}")
            
            # Get source statistics
            source_stats = self.get_knowledge_source_stats()
            if source_stats:
                print("\nSources:")
                for source, count in source_stats.items():
                    print(f"- {source}: {count} facts")
        
        elif command.lower() == "tags":
            tags = self.get_tags()
            print("\nTags:")
            for tag in tags:
                print(f"- {tag}")
        
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' for available commands.")
```

## Step 12: Testing the Knowledge Base

To test our knowledge base, save the complete code in a file named `knowledge_base.py` and run it:

```bash
python knowledge_base.py
```

This will demonstrate the basic knowledge base functionality. To use the explorer:

```python
# At the end of your knowledge_base.py file, add:
if __name__ == "__main__":
    # ... existing example code ...
    
    # Run the explorer
    print("\nStarting knowledge base explorer...\n")
    kb.run_explorer()
```

## Step 13: Advanced Knowledge Organization Techniques

Here are some advanced techniques for organizing knowledge in your knowledge base:

### Hierarchical Categories

```python
def add_hierarchical_category(self, path: str, description: str) -> None:
    """
    Add a hierarchical category.
    
    Args:
        path: Path in the form "parent/child/grandchild"
        description: Category description
    """
    components = path.split("/")
    current_path = ""
    
    for i, component in enumerate(components):
        current_path = current_path + "/" + component if current_path else component
        existing = self.facts.query(
            current_path, 
            category="system",
            tags=["hierarchical_category"]
        )
        
        if not existing:
            # Create this level
            self.facts.create(
                content=description if i == len(components) - 1 else f"Category path: {current_path}",
                category="system",
                tags=["hierarchical_category", "structure"],
                metadata={
                    "type": "hierarchical_category",
                    "path": current_path,
                    "name": component,
                    "level": i,
                    "parent": "/".join(components[:i]) if i > 0 else None,
                    "created_at": datetime.now().isoformat()
                }
            )
            
            print(f"Created category path: {current_path}")
```

### Knowledge Graph Visualization

```python
def export_knowledge_graph(self, filepath: str) -> None:
    """
    Export knowledge graph for visualization.
    
    Args:
        filepath: Path to export file (GraphML format)
    """
    # Get all facts and relationships
    facts = self.facts.query("")
    relationships = self.facts.query("", category="relationship")
    
    # Generate GraphML format
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    root = ET.Element("graphml")
    root.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
    
    # Define node attributes
    node_key = ET.SubElement(root, "key")
    node_key.set("id", "label")
    node_key.set("for", "node")
    node_key.set("attr.name", "label")
    node_key.set("attr.type", "string")
    
    node_category = ET.SubElement(root, "key")
    node_category.set("id", "category")
    node_category.set("for", "node")
    node_category.set("attr.name", "category")
    node_category.set("attr.type", "string")
    
    # Define edge attributes
    edge_key = ET.SubElement(root, "key")
    edge_key.set("id", "label")
    edge_key.set("for", "edge")
    edge_key.set("attr.name", "label")
    edge_key.set("attr.type", "string")
    
    edge_weight = ET.SubElement(root, "key")
    edge_weight.set("id", "weight")
    edge_weight.set("for", "edge")
    edge_weight.set("attr.name", "weight")
    edge_weight.set("attr.type", "double")
    
    # Create graph
    graph = ET.SubElement(root, "graph")
    graph.set("id", "G")
    graph.set("edgedefault", "directed")
    
    # Add fact nodes
    for fact in facts:
        if fact.get("category") != "relationship":  # Skip relationship nodes
            node = ET.SubElement(graph, "node")
            node.set("id", str(fact["id"]))
            
            label = ET.SubElement(node, "data")
            label.set("key", "label")
            
            # Truncate content if too long
            content = fact["content"]
            if len(content) > 50:
                content = content[:47] + "..."
            label.text = content
            
            category = ET.SubElement(node, "data")
            category.set("key", "category")
            category.text = fact.get("category", "general")
    
    # Add relationship edges
    for rel in relationships:
        metadata = rel.get("metadata", {})
        if "subject_id" in metadata and "object_id" in metadata:
            edge = ET.SubElement(graph, "edge")
            edge.set("id", str(rel["id"]))
            edge.set("source", metadata["subject_id"])
            edge.set("target", metadata["object_id"])
            
            label = ET.SubElement(edge, "data")
            label.set("key", "label")
            label.text = metadata.get("predicate", "related_to")
            
            weight = ET.SubElement(edge, "data")
            weight.set("key", "weight")
            weight.text = str(metadata.get("confidence", 1.0))
    
    # Write to file with pretty formatting
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    with open(filepath, "w") as f:
        f.write(xmlstr)
    
    print(f"Exported knowledge graph to {filepath}")
    print(f"The graph contains {len(facts) - len(relationships)} fact nodes and {len(relationships)} relationship edges")
    print("You can visualize this file using tools like Gephi, Cytoscape, or yEd.")
```

## Conclusion

In this tutorial, we've built a comprehensive knowledge base system using AgentMem that:

1. Stores factual knowledge using semantic memory
2. Tracks knowledge creation and usage with episodic memory
3. Applies inference rules using procedural memory
4. Maintains relationships between facts
5. Tracks provenance and confidence levels
6. Handles contradictions and uncertainties
7. Provides powerful search capabilities
8. Supports persistence and import/export

This knowledge base can serve as a foundation for AI applications that require structured knowledge storage and retrieval. By leveraging AgentMem's memory systems, we've created a system that not only stores information but also maintains its context, history, and relationships.

For more advanced applications, you might consider extending this knowledge base with:

1. Integration with large language models for natural language understanding
2. More sophisticated inference engines
3. Support for additional knowledge formats (RDF, OWL, etc.)
4. Visualization tools for exploring the knowledge graph
5. Automatic knowledge extraction from text
6. Collaborative knowledge editing features

AgentMem provides the flexible memory infrastructure needed to implement these advanced features, making it an excellent foundation for knowledge-based AI systems.