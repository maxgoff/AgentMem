# Creating a Learning Agent with AgentMem

This tutorial will guide you through building an AI agent that can learn from its experiences using AgentMem's memory systems.

## Overview

A learning agent improves its performance through experience. By leveraging AgentMem, we can create agents that:

1. Remember past experiences and use them to improve (episodic memory)
2. Build and update a knowledge base of facts (semantic memory)
3. Learn and refine action patterns based on results (procedural memory)

In this tutorial, we'll build a simple learning agent that solves problems and improves its approach over time.

## Prerequisites

- AgentMem installed (`pip install agentmem[vector]`)
- Basic understanding of Python
- Familiarity with basic AgentMem concepts

## Step 1: Setting Up the Learning Agent Structure

First, let's create a basic learning agent class that integrates all three memory types:

```python
import uuid
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from agentmem.semantic import SemanticMemory
from agentmem.episodic import EpisodicMemory
from agentmem.procedural import ProceduralMemory
from agentmem import configure_logging, LogLevel

# Configure logging
configure_logging(LogLevel.INFO)

class LearningAgent:
    def __init__(self, name="AgentMem Learner", persistence_dir=None):
        """Initialize the learning agent with memory systems."""
        self.name = name
        
        # Initialize memory systems
        self.knowledge = SemanticMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.experiences = EpisodicMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.skills = ProceduralMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        # Initialize agent state
        self.agent_id = str(uuid.uuid4())
        self.current_task = None
        self.learning_rate = 0.1  # How quickly the agent adapts
        self.exploration_rate = 0.2  # Probability of trying something new
        
        print(f"Learning Agent '{name}' initialized with ID: {self.agent_id}")
```

## Step 2: Implementing Learning from Experience

Let's add methods for recording and learning from experiences:

```python
def record_experience(self, task: str, action: str, outcome: str, 
                     success: bool, context: Dict[str, Any] = None) -> str:
    """
    Record an experience in episodic memory.
    
    Args:
        task: The task that was attempted
        action: The action that was taken
        outcome: The outcome that was observed
        success: Whether the action was successful
        context: Additional contextual information
        
    Returns:
        ID of the recorded experience
    """
    if context is None:
        context = {}
    
    # Determine importance based on outcome
    importance = 7 if success else 8  # Failures are slightly more important to remember
    
    # Calculate a performance score
    performance_score = 1.0 if success else 0.0
    
    # Add task information to context
    context.update({
        "task": task,
        "success": success,
        "performance_score": performance_score,
        "timestamp": datetime.now().isoformat()
    })
    
    # Record the experience
    experience_id = self.experiences.create(
        content=f"Task: {task}\nAction: {action}\nOutcome: {outcome}\nSuccess: {success}",
        timestamp=datetime.now(),
        context=context,
        importance=importance
    )
    
    # Learn from this experience
    self._learn_from_experience(task, action, outcome, success, context)
    
    return str(experience_id)

def _learn_from_experience(self, task: str, action: str, outcome: str, 
                          success: bool, context: Dict[str, Any]) -> None:
    """
    Internal method to learn from an experience.
    
    This updates both semantic knowledge and procedural skills.
    """
    # 1. Update knowledge based on outcome
    if success:
        # If successful, record what worked
        self.knowledge.create(
            content=f"The action '{action}' was effective for task '{task}'.",
            category="task_knowledge",
            tags=[task, "successful_approach"],
            metadata={
                "task": task,
                "action": action,
                "success_count": 1,
                "confidence": 0.5 + (0.5 * self.learning_rate)  # Start with moderate confidence
            }
        )
    else:
        # If unsuccessful, record what didn't work
        self.knowledge.create(
            content=f"The action '{action}' was ineffective for task '{task}'.",
            category="task_knowledge",
            tags=[task, "unsuccessful_approach"],
            metadata={
                "task": task,
                "action": action,
                "failure_count": 1,
                "confidence": 0.5 * self.learning_rate  # Start with low confidence
            }
        )
    
    # 2. Update or create a skill for this task
    existing_skills = self.skills.query(task, domain="tasks")
    
    if existing_skills:
        # Update existing skill
        skill = existing_skills[0]
        skill_id = skill["id"]
        
        # Get existing steps and success rate
        steps = skill.get("steps", [])
        success_rate = skill.get("metadata", {}).get("success_rate", 0.5)
        attempts = skill.get("metadata", {}).get("attempts", 0)
        
        # Update success rate with new experience
        new_success_rate = ((success_rate * attempts) + (1.0 if success else 0.0)) / (attempts + 1)
        
        # Modify steps based on outcome
        if success and action not in steps:
            # Add successful action if not already present
            steps.append(action)
        elif not success and action in steps and len(steps) > 1:
            # Remove unsuccessful action if it was previously included
            steps.remove(action)
        
        # Update the skill
        self.skills.update(
            skill_id,
            steps=steps,
            metadata={
                "success_rate": new_success_rate,
                "attempts": attempts + 1,
                "last_updated": datetime.now().isoformat()
            }
        )
    else:
        # Create new skill
        self.skills.create(
            content=f"How to perform task: {task}",
            task=task,
            steps=[action] if success else [],
            prerequisites=[],
            domains=["tasks", task.lower().replace(" ", "_")],
            metadata={
                "success_rate": 1.0 if success else 0.0,
                "attempts": 1,
                "created_at": datetime.now().isoformat()
            }
        )
```

## Step 3: Creating a Decision-Making Process

Now, let's implement methods for the agent to choose actions based on its experiences:

```python
def choose_action(self, task: str, available_actions: List[str], 
                 context: Dict[str, Any] = None) -> str:
    """
    Choose an action for a given task based on past experiences.
    
    Args:
        task: The task to perform
        available_actions: List of available actions to choose from
        context: Additional context for the decision
        
    Returns:
        The chosen action
    """
    if not available_actions:
        return None
    
    if context is None:
        context = {}
    
    self.current_task = task
    
    # Check if we should explore (try something new)
    if random.random() < self.exploration_rate:
        chosen_action = random.choice(available_actions)
        print(f"Exploring: Trying {chosen_action}")
        return chosen_action
    
    # Look for skills related to this task
    skills = self.skills.query(task, domain="tasks")
    
    if skills and skills[0].get("steps"):
        # Use existing skill if available
        skill = skills[0]
        steps = skill.get("steps", [])
        success_rate = skill.get("metadata", {}).get("success_rate", 0.0)
        
        # Find the best known action that's in available_actions
        for step in steps:
            if step in available_actions:
                print(f"Using learned skill with success rate: {success_rate:.2f}")
                return step
    
    # If no applicable skill, check past successful experiences
    successful_experiences = self.experiences.query(
        task,
        context_keys=["task", "success"]
    )
    
    # Filter for successful experiences with this specific task
    successful_experiences = [
        exp for exp in successful_experiences 
        if exp.get("context", {}).get("task") == task and 
           exp.get("context", {}).get("success") == True
    ]
    
    if successful_experiences:
        # Analyze successful experiences to find commonly used actions
        action_counts = {}
        for exp in successful_experiences:
            content = exp.get("content", "")
            for line in content.split("\n"):
                if line.startswith("Action:"):
                    action = line[7:].strip()
                    if action in available_actions:
                        action_counts[action] = action_counts.get(action, 0) + 1
        
        if action_counts:
            # Choose the most successful action
            best_action = max(action_counts.items(), key=lambda x: x[1])[0]
            print(f"Using action based on {action_counts[best_action]} successful experiences")
            return best_action
    
    # If no past experience or skill applies, choose randomly
    print("No applicable experience or skill, choosing randomly")
    return random.choice(available_actions)

def reflect_on_experiences(self, task: str = None) -> Dict[str, Any]:
    """
    Reflect on past experiences to improve performance.
    
    Args:
        task: Optional specific task to reflect on (all tasks if None)
        
    Returns:
        Dictionary of insights from reflection
    """
    # Get all experiences, or filter by task
    experiences_query = task if task else ""
    experiences = self.experiences.query(experiences_query)
    
    if task:
        # Filter for exact task match
        experiences = [
            exp for exp in experiences 
            if exp.get("context", {}).get("task") == task
        ]
    
    if not experiences:
        return {"insights": "No experiences to reflect on"}
    
    # Count successful vs. unsuccessful experiences
    success_count = 0
    failure_count = 0
    
    # Track actions and their success rates
    action_results = {}
    
    for exp in experiences:
        # Parse the experience
        content = exp.get("content", "")
        action = None
        
        for line in content.split("\n"):
            if line.startswith("Action:"):
                action = line[7:].strip()
        
        success = exp.get("context", {}).get("success", False)
        
        if success:
            success_count += 1
        else:
            failure_count += 1
        
        if action:
            if action not in action_results:
                action_results[action] = {"success": 0, "failure": 0}
            
            if success:
                action_results[action]["success"] += 1
            else:
                action_results[action]["failure"] += 1
    
    # Calculate overall success rate
    total_experiences = success_count + failure_count
    overall_success_rate = success_count / total_experiences if total_experiences > 0 else 0
    
    # Calculate action success rates
    action_success_rates = {}
    for action, results in action_results.items():
        total = results["success"] + results["failure"]
        success_rate = results["success"] / total if total > 0 else 0
        action_success_rates[action] = {
            "success_rate": success_rate,
            "total_uses": total
        }
    
    # Generate insights
    best_actions = sorted(
        [(action, data["success_rate"]) for action, data in action_success_rates.items() if data["total_uses"] >= 3],
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    worst_actions = sorted(
        [(action, data["success_rate"]) for action, data in action_success_rates.items() if data["total_uses"] >= 3],
        key=lambda x: x[1]
    )[:3]
    
    insights = {
        "total_experiences": total_experiences,
        "success_rate": overall_success_rate,
        "action_success_rates": action_success_rates,
        "best_actions": best_actions,
        "worst_actions": worst_actions,
        "insights": []
    }
    
    # Add textual insights
    if best_actions:
        insights["insights"].append(
            f"Most effective actions: {', '.join([a[0] for a in best_actions])}"
        )
    
    if worst_actions:
        insights["insights"].append(
            f"Least effective actions: {', '.join([a[0] for a in worst_actions])}"
        )
    
    # Update exploration rate based on performance
    # Reduce exploration as success rate improves
    if total_experiences >= 10:
        self.exploration_rate = max(0.05, 0.5 - (overall_success_rate * 0.3))
        insights["exploration_rate_updated"] = self.exploration_rate
    
    return insights
```

## Step 4: Implementing Adaptive Learning

Let's add methods to make the agent adapt its strategies over time:

```python
def adapt_learning_rate(self, task_difficulty: float) -> None:
    """
    Adapt the learning rate based on task difficulty.
    
    Args:
        task_difficulty: Difficulty rating from 0.0 (easy) to 1.0 (hard)
    """
    # Learn faster from easy tasks, slower from difficult ones
    self.learning_rate = 0.05 + ((1.0 - task_difficulty) * 0.15)
    print(f"Adjusted learning rate to {self.learning_rate:.2f} based on task difficulty")

def improve_skill(self, task: str) -> bool:
    """
    Actively try to improve a skill based on experiences.
    
    Args:
        task: The task to improve skill in
        
    Returns:
        Whether the skill was improved
    """
    # Analyze experiences with this task
    insights = self.reflect_on_experiences(task)
    
    # Look for the skill for this task
    skills = self.skills.query(task, domain="tasks")
    
    if not skills:
        print(f"No existing skill found for task: {task}")
        return False
    
    skill = skills[0]
    skill_id = skill["id"]
    current_steps = skill.get("steps", [])
    
    # Get the best actions from reflection
    best_actions = insights.get("best_actions", [])
    best_action_names = [a[0] for a in best_actions]
    
    if not best_actions:
        print("Not enough data to improve skill")
        return False
    
    # Improve the skill by updating steps
    # Add top-performing actions if not already present
    improved = False
    new_steps = current_steps.copy()
    
    for action in best_action_names:
        if action not in new_steps:
            new_steps.append(action)
            improved = True
    
    # Remove poorly performing actions
    worst_actions = insights.get("worst_actions", [])
    for action, success_rate in worst_actions:
        if success_rate < 0.3 and action in new_steps and len(new_steps) > 1:
            new_steps.remove(action)
            improved = True
    
    if improved:
        # Update the skill with improved steps
        self.skills.update(
            skill_id,
            steps=new_steps,
            metadata={
                "success_rate": insights.get("success_rate", 0.5),
                "last_improved": datetime.now().isoformat()
            }
        )
        print(f"Improved skill for task: {task}")
        print(f"New steps: {new_steps}")
        return True
    else:
        print(f"Skill for task {task} already optimal based on current experiences")
        return False

def extract_knowledge_from_experiences(self) -> int:
    """
    Extract general knowledge from experiences.
    
    Returns:
        Number of knowledge items extracted
    """
    # Get all experiences
    all_experiences = self.experiences.query("")
    
    # Extract patterns and correlations
    extracted_count = 0
    
    # Look for task-action pairs with high success rates
    task_action_results = {}
    
    for exp in all_experiences:
        content = exp.get("content", "")
        context = exp.get("context", {})
        
        task = context.get("task")
        success = context.get("success", False)
        
        if not task:
            continue
        
        # Extract action from content
        action = None
        for line in content.split("\n"):
            if line.startswith("Action:"):
                action = line[7:].strip()
                break
        
        if not action:
            continue
        
        # Track results for this task-action pair
        key = f"{task}:{action}"
        if key not in task_action_results:
            task_action_results[key] = {"success": 0, "failure": 0}
        
        if success:
            task_action_results[key]["success"] += 1
        else:
            task_action_results[key]["failure"] += 1
    
    # Find high-confidence patterns
    for key, results in task_action_results.items():
        task, action = key.split(":", 1)
        total = results["success"] + results["failure"]
        
        if total >= 5:  # Only extract knowledge from sufficient data
            success_rate = results["success"] / total
            
            # Look for existing knowledge about this
            existing = self.knowledge.query(
                f"{task} {action}",
                category="extracted_knowledge"
            )
            
            if existing:
                # Update existing knowledge
                for item in existing:
                    if item.get("metadata", {}).get("task") == task and \
                       item.get("metadata", {}).get("action") == action:
                        # Update this knowledge item
                        self.knowledge.update(
                            item["id"],
                            content=f"For task '{task}', the action '{action}' has a " +
                                   f"success rate of {success_rate:.0%} based on {total} attempts.",
                            metadata={
                                "success_rate": success_rate,
                                "sample_size": total,
                                "last_updated": datetime.now().isoformat()
                            }
                        )
                        break
            elif success_rate >= 0.7 or success_rate <= 0.3:
                # Create new knowledge for very successful or unsuccessful actions
                effectiveness = "effective" if success_rate >= 0.7 else "ineffective"
                confidence = min(0.5 + (total / 20), 0.95)  # Confidence grows with sample size
                
                self.knowledge.create(
                    content=f"For task '{task}', the action '{action}' is {effectiveness} " +
                           f"with a success rate of {success_rate:.0%} based on {total} attempts.",
                    category="extracted_knowledge",
                    tags=[task, action, effectiveness],
                    metadata={
                        "task": task,
                        "action": action,
                        "success_rate": success_rate,
                        "sample_size": total,
                        "confidence": confidence,
                        "extracted_at": datetime.now().isoformat()
                    }
                )
                extracted_count += 1
    
    print(f"Extracted {extracted_count} knowledge items from experiences")
    return extracted_count
```

## Step 5: Adding Meta-Learning Capabilities

Let's implement meta-learning for the agent to improve its own learning process:

```python
def evaluate_learning_progress(self) -> Dict[str, Any]:
    """
    Evaluate how well the agent is learning over time.
    
    Returns:
        Dictionary with learning progress metrics
    """
    # Get all experiences sorted by time
    all_experiences = self.experiences.query("")
    if not all_experiences:
        return {"progress": "No experiences yet"}
    
    # Sort by timestamp
    all_experiences.sort(key=lambda x: x.get("timestamp"))
    
    # Split into time periods (e.g., first half vs. second half)
    midpoint = len(all_experiences) // 2
    early_experiences = all_experiences[:midpoint]
    recent_experiences = all_experiences[midpoint:]
    
    # Calculate success rates for each period
    early_success = sum(1 for exp in early_experiences if exp.get("context", {}).get("success", False))
    early_success_rate = early_success / len(early_experiences) if early_experiences else 0
    
    recent_success = sum(1 for exp in recent_experiences if exp.get("context", {}).get("success", False))
    recent_success_rate = recent_success / len(recent_experiences) if recent_experiences else 0
    
    # Calculate improvement
    improvement = recent_success_rate - early_success_rate
    
    return {
        "total_experiences": len(all_experiences),
        "early_success_rate": early_success_rate,
        "recent_success_rate": recent_success_rate,
        "improvement": improvement,
        "learning_rate": self.learning_rate,
        "exploration_rate": self.exploration_rate,
        "skills_count": len(self.skills.query("")),
        "knowledge_items": len(self.knowledge.query(""))
    }

def adjust_learning_strategy(self) -> Dict[str, Any]:
    """
    Adjust learning strategy based on performance evaluation.
    
    Returns:
        Dictionary with adjustments made
    """
    # Evaluate current learning progress
    progress = self.evaluate_learning_progress()
    
    adjustments = {
        "previous_learning_rate": self.learning_rate,
        "previous_exploration_rate": self.exploration_rate
    }
    
    # If we don't have enough experiences, do nothing
    if progress.get("total_experiences", 0) < 10:
        return {"status": "Not enough experiences to adjust strategy"}
    
    # Adjust exploration rate based on improvement
    improvement = progress.get("improvement", 0)
    
    if improvement >= 0.1:
        # We're learning well, reduce exploration to exploit knowledge
        self.exploration_rate = max(0.05, self.exploration_rate - 0.05)
    elif improvement <= -0.1:
        # We're doing worse, increase exploration to find better approaches
        self.exploration_rate = min(0.5, self.exploration_rate + 0.1)
    
    # Adjust learning rate based on recent success
    recent_success_rate = progress.get("recent_success_rate", 0)
    
    if recent_success_rate >= 0.8:
        # We're doing well, can afford to learn more aggressively
        self.learning_rate = min(0.3, self.learning_rate + 0.05)
    elif recent_success_rate <= 0.3:
        # We're struggling, be more conservative in learning
        self.learning_rate = max(0.05, self.learning_rate - 0.03)
    
    adjustments.update({
        "new_learning_rate": self.learning_rate,
        "new_exploration_rate": self.exploration_rate,
        "reason": f"Adjusted based on improvement of {improvement:.2f} and " +
                 f"recent success rate of {recent_success_rate:.2f}"
    })
    
    return adjustments
```

## Step 6: Implementing Task Planning

Now, let's add methods for the agent to plan its approach to tasks:

```python
def plan_approach(self, task: str, available_actions: List[str]) -> List[str]:
    """
    Plan an approach for a task based on knowledge and skills.
    
    Args:
        task: The task to plan for
        available_actions: Available actions to use in the plan
        
    Returns:
        List of actions forming the plan
    """
    # Check if we have a skill for this task
    skills = self.skills.query(task, domain="tasks")
    
    if skills and skills[0].get("steps"):
        # Use existing skill if available
        skill = skills[0]
        steps = skill.get("steps", [])
        success_rate = skill.get("metadata", {}).get("success_rate", 0.0)
        
        # Filter steps to only include available actions
        valid_steps = [step for step in steps if step in available_actions]
        
        if valid_steps:
            print(f"Using learned skill with {len(valid_steps)} steps, " +
                 f"success rate: {success_rate:.2f}")
            return valid_steps
    
    # If no applicable skill, check knowledge for effective actions
    knowledge = self.knowledge.query(task, category="extracted_knowledge")
    
    effective_actions = []
    for item in knowledge:
        metadata = item.get("metadata", {})
        action = metadata.get("action")
        success_rate = metadata.get("success_rate", 0)
        
        if action in available_actions and success_rate >= 0.5:
            effective_actions.append((action, success_rate))
    
    if effective_actions:
        # Sort by success rate
        effective_actions.sort(key=lambda x: x[1], reverse=True)
        plan = [action for action, _ in effective_actions]
        print(f"Created plan with {len(plan)} actions based on knowledge")
        return plan
    
    # If no knowledge, try similar tasks
    similar_tasks = self.skills.query(
        task,
        use_vector=True,
        n_results=3
    )
    
    for similar in similar_tasks:
        if similar.get("task") != task and similar.get("steps"):  # Different task
            # Adapt steps from similar task
            adaptation = [
                step for step in similar.get("steps", [])
                if step in available_actions
            ]
            if adaptation:
                print(f"Adapted plan from similar task: {similar.get('task')}")
                return adaptation
    
    # If all else fails, create a random plan
    exploration_plan = random.sample(
        available_actions,
        min(3, len(available_actions))
    )
    print("Created exploratory plan")
    return exploration_plan
```

## Step 7: Putting It All Together

Now, let's create our complete learning agent application:

```python
# learning_agent.py
import uuid
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from agentmem.semantic import SemanticMemory
from agentmem.episodic import EpisodicMemory
from agentmem.procedural import ProceduralMemory
from agentmem import configure_logging, LogLevel

# Configure logging
configure_logging(LogLevel.INFO)

class LearningAgent:
    def __init__(self, name="AgentMem Learner", persistence_dir=None):
        """Initialize the learning agent with memory systems."""
        self.name = name
        
        # Initialize memory systems
        self.knowledge = SemanticMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.experiences = EpisodicMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        self.skills = ProceduralMemory(
            persistence=persistence_dir,
            vector_search=True
        )
        
        # Initialize agent state
        self.agent_id = str(uuid.uuid4())
        self.current_task = None
        self.learning_rate = 0.1  # How quickly the agent adapts
        self.exploration_rate = 0.2  # Probability of trying something new
        
        print(f"Learning Agent '{name}' initialized with ID: {self.agent_id}")

    def record_experience(self, task: str, action: str, outcome: str, 
                         success: bool, context: Dict[str, Any] = None) -> str:
        """
        Record an experience in episodic memory.
        
        Args:
            task: The task that was attempted
            action: The action that was taken
            outcome: The outcome that was observed
            success: Whether the action was successful
            context: Additional contextual information
            
        Returns:
            ID of the recorded experience
        """
        if context is None:
            context = {}
        
        # Determine importance based on outcome
        importance = 7 if success else 8  # Failures are slightly more important to remember
        
        # Calculate a performance score
        performance_score = 1.0 if success else 0.0
        
        # Add task information to context
        context.update({
            "task": task,
            "success": success,
            "performance_score": performance_score,
            "timestamp": datetime.now().isoformat()
        })
        
        # Record the experience
        experience_id = self.experiences.create(
            content=f"Task: {task}\nAction: {action}\nOutcome: {outcome}\nSuccess: {success}",
            timestamp=datetime.now(),
            context=context,
            importance=importance
        )
        
        # Learn from this experience
        self._learn_from_experience(task, action, outcome, success, context)
        
        return str(experience_id)

    def _learn_from_experience(self, task: str, action: str, outcome: str, 
                              success: bool, context: Dict[str, Any]) -> None:
        """
        Internal method to learn from an experience.
        
        This updates both semantic knowledge and procedural skills.
        """
        # 1. Update knowledge based on outcome
        if success:
            # If successful, record what worked
            self.knowledge.create(
                content=f"The action '{action}' was effective for task '{task}'.",
                category="task_knowledge",
                tags=[task, "successful_approach"],
                metadata={
                    "task": task,
                    "action": action,
                    "success_count": 1,
                    "confidence": 0.5 + (0.5 * self.learning_rate)  # Start with moderate confidence
                }
            )
        else:
            # If unsuccessful, record what didn't work
            self.knowledge.create(
                content=f"The action '{action}' was ineffective for task '{task}'.",
                category="task_knowledge",
                tags=[task, "unsuccessful_approach"],
                metadata={
                    "task": task,
                    "action": action,
                    "failure_count": 1,
                    "confidence": 0.5 * self.learning_rate  # Start with low confidence
                }
            )
        
        # 2. Update or create a skill for this task
        existing_skills = self.skills.query(task, domain="tasks")
        
        if existing_skills:
            # Update existing skill
            skill = existing_skills[0]
            skill_id = skill["id"]
            
            # Get existing steps and success rate
            steps = skill.get("steps", [])
            success_rate = skill.get("metadata", {}).get("success_rate", 0.5)
            attempts = skill.get("metadata", {}).get("attempts", 0)
            
            # Update success rate with new experience
            new_success_rate = ((success_rate * attempts) + (1.0 if success else 0.0)) / (attempts + 1)
            
            # Modify steps based on outcome
            if success and action not in steps:
                # Add successful action if not already present
                steps.append(action)
            elif not success and action in steps and len(steps) > 1:
                # Remove unsuccessful action if it was previously included
                steps.remove(action)
            
            # Update the skill
            self.skills.update(
                skill_id,
                steps=steps,
                metadata={
                    "success_rate": new_success_rate,
                    "attempts": attempts + 1,
                    "last_updated": datetime.now().isoformat()
                }
            )
        else:
            # Create new skill
            self.skills.create(
                content=f"How to perform task: {task}",
                task=task,
                steps=[action] if success else [],
                prerequisites=[],
                domains=["tasks", task.lower().replace(" ", "_")],
                metadata={
                    "success_rate": 1.0 if success else 0.0,
                    "attempts": 1,
                    "created_at": datetime.now().isoformat()
                }
            )

    def choose_action(self, task: str, available_actions: List[str], 
                     context: Dict[str, Any] = None) -> str:
        """
        Choose an action for a given task based on past experiences.
        
        Args:
            task: The task to perform
            available_actions: List of available actions to choose from
            context: Additional context for the decision
            
        Returns:
            The chosen action
        """
        if not available_actions:
            return None
        
        if context is None:
            context = {}
        
        self.current_task = task
        
        # Check if we should explore (try something new)
        if random.random() < self.exploration_rate:
            chosen_action = random.choice(available_actions)
            print(f"Exploring: Trying {chosen_action}")
            return chosen_action
        
        # Look for skills related to this task
        skills = self.skills.query(task, domain="tasks")
        
        if skills and skills[0].get("steps"):
            # Use existing skill if available
            skill = skills[0]
            steps = skill.get("steps", [])
            success_rate = skill.get("metadata", {}).get("success_rate", 0.0)
            
            # Find the best known action that's in available_actions
            for step in steps:
                if step in available_actions:
                    print(f"Using learned skill with success rate: {success_rate:.2f}")
                    return step
        
        # If no applicable skill, check past successful experiences
        successful_experiences = self.experiences.query(
            task,
            context_keys=["task", "success"]
        )
        
        # Filter for successful experiences with this specific task
        successful_experiences = [
            exp for exp in successful_experiences 
            if exp.get("context", {}).get("task") == task and 
               exp.get("context", {}).get("success") == True
        ]
        
        if successful_experiences:
            # Analyze successful experiences to find commonly used actions
            action_counts = {}
            for exp in successful_experiences:
                content = exp.get("content", "")
                for line in content.split("\n"):
                    if line.startswith("Action:"):
                        action = line[7:].strip()
                        if action in available_actions:
                            action_counts[action] = action_counts.get(action, 0) + 1
            
            if action_counts:
                # Choose the most successful action
                best_action = max(action_counts.items(), key=lambda x: x[1])[0]
                print(f"Using action based on {action_counts[best_action]} successful experiences")
                return best_action
        
        # If no past experience or skill applies, choose randomly
        print("No applicable experience or skill, choosing randomly")
        return random.choice(available_actions)

    def reflect_on_experiences(self, task: str = None) -> Dict[str, Any]:
        """
        Reflect on past experiences to improve performance.
        
        Args:
            task: Optional specific task to reflect on (all tasks if None)
            
        Returns:
            Dictionary of insights from reflection
        """
        # Get all experiences, or filter by task
        experiences_query = task if task else ""
        experiences = self.experiences.query(experiences_query)
        
        if task:
            # Filter for exact task match
            experiences = [
                exp for exp in experiences 
                if exp.get("context", {}).get("task") == task
            ]
        
        if not experiences:
            return {"insights": "No experiences to reflect on"}
        
        # Count successful vs. unsuccessful experiences
        success_count = 0
        failure_count = 0
        
        # Track actions and their success rates
        action_results = {}
        
        for exp in experiences:
            # Parse the experience
            content = exp.get("content", "")
            action = None
            
            for line in content.split("\n"):
                if line.startswith("Action:"):
                    action = line[7:].strip()
            
            success = exp.get("context", {}).get("success", False)
            
            if success:
                success_count += 1
            else:
                failure_count += 1
            
            if action:
                if action not in action_results:
                    action_results[action] = {"success": 0, "failure": 0}
                
                if success:
                    action_results[action]["success"] += 1
                else:
                    action_results[action]["failure"] += 1
        
        # Calculate overall success rate
        total_experiences = success_count + failure_count
        overall_success_rate = success_count / total_experiences if total_experiences > 0 else 0
        
        # Calculate action success rates
        action_success_rates = {}
        for action, results in action_results.items():
            total = results["success"] + results["failure"]
            success_rate = results["success"] / total if total > 0 else 0
            action_success_rates[action] = {
                "success_rate": success_rate,
                "total_uses": total
            }
        
        # Generate insights
        best_actions = sorted(
            [(action, data["success_rate"]) for action, data in action_success_rates.items() if data["total_uses"] >= 3],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        worst_actions = sorted(
            [(action, data["success_rate"]) for action, data in action_success_rates.items() if data["total_uses"] >= 3],
            key=lambda x: x[1]
        )[:3]
        
        insights = {
            "total_experiences": total_experiences,
            "success_rate": overall_success_rate,
            "action_success_rates": action_success_rates,
            "best_actions": best_actions,
            "worst_actions": worst_actions,
            "insights": []
        }
        
        # Add textual insights
        if best_actions:
            insights["insights"].append(
                f"Most effective actions: {', '.join([a[0] for a in best_actions])}"
            )
        
        if worst_actions:
            insights["insights"].append(
                f"Least effective actions: {', '.join([a[0] for a in worst_actions])}"
            )
        
        # Update exploration rate based on performance
        # Reduce exploration as success rate improves
        if total_experiences >= 10:
            self.exploration_rate = max(0.05, 0.5 - (overall_success_rate * 0.3))
            insights["exploration_rate_updated"] = self.exploration_rate
        
        return insights

    def adapt_learning_rate(self, task_difficulty: float) -> None:
        """
        Adapt the learning rate based on task difficulty.
        
        Args:
            task_difficulty: Difficulty rating from 0.0 (easy) to 1.0 (hard)
        """
        # Learn faster from easy tasks, slower from difficult ones
        self.learning_rate = 0.05 + ((1.0 - task_difficulty) * 0.15)
        print(f"Adjusted learning rate to {self.learning_rate:.2f} based on task difficulty")

    def improve_skill(self, task: str) -> bool:
        """
        Actively try to improve a skill based on experiences.
        
        Args:
            task: The task to improve skill in
            
        Returns:
            Whether the skill was improved
        """
        # Analyze experiences with this task
        insights = self.reflect_on_experiences(task)
        
        # Look for the skill for this task
        skills = self.skills.query(task, domain="tasks")
        
        if not skills:
            print(f"No existing skill found for task: {task}")
            return False
        
        skill = skills[0]
        skill_id = skill["id"]
        current_steps = skill.get("steps", [])
        
        # Get the best actions from reflection
        best_actions = insights.get("best_actions", [])
        best_action_names = [a[0] for a in best_actions]
        
        if not best_actions:
            print("Not enough data to improve skill")
            return False
        
        # Improve the skill by updating steps
        # Add top-performing actions if not already present
        improved = False
        new_steps = current_steps.copy()
        
        for action in best_action_names:
            if action not in new_steps:
                new_steps.append(action)
                improved = True
        
        # Remove poorly performing actions
        worst_actions = insights.get("worst_actions", [])
        for action, success_rate in worst_actions:
            if success_rate < 0.3 and action in new_steps and len(new_steps) > 1:
                new_steps.remove(action)
                improved = True
        
        if improved:
            # Update the skill with improved steps
            self.skills.update(
                skill_id,
                steps=new_steps,
                metadata={
                    "success_rate": insights.get("success_rate", 0.5),
                    "last_improved": datetime.now().isoformat()
                }
            )
            print(f"Improved skill for task: {task}")
            print(f"New steps: {new_steps}")
            return True
        else:
            print(f"Skill for task {task} already optimal based on current experiences")
            return False

    def extract_knowledge_from_experiences(self) -> int:
        """
        Extract general knowledge from experiences.
        
        Returns:
            Number of knowledge items extracted
        """
        # Get all experiences
        all_experiences = self.experiences.query("")
        
        # Extract patterns and correlations
        extracted_count = 0
        
        # Look for task-action pairs with high success rates
        task_action_results = {}
        
        for exp in all_experiences:
            content = exp.get("content", "")
            context = exp.get("context", {})
            
            task = context.get("task")
            success = context.get("success", False)
            
            if not task:
                continue
            
            # Extract action from content
            action = None
            for line in content.split("\n"):
                if line.startswith("Action:"):
                    action = line[7:].strip()
                    break
            
            if not action:
                continue
            
            # Track results for this task-action pair
            key = f"{task}:{action}"
            if key not in task_action_results:
                task_action_results[key] = {"success": 0, "failure": 0}
            
            if success:
                task_action_results[key]["success"] += 1
            else:
                task_action_results[key]["failure"] += 1
        
        # Find high-confidence patterns
        for key, results in task_action_results.items():
            task, action = key.split(":", 1)
            total = results["success"] + results["failure"]
            
            if total >= 5:  # Only extract knowledge from sufficient data
                success_rate = results["success"] / total
                
                # Look for existing knowledge about this
                existing = self.knowledge.query(
                    f"{task} {action}",
                    category="extracted_knowledge"
                )
                
                if existing:
                    # Update existing knowledge
                    for item in existing:
                        if item.get("metadata", {}).get("task") == task and \
                           item.get("metadata", {}).get("action") == action:
                            # Update this knowledge item
                            self.knowledge.update(
                                item["id"],
                                content=f"For task '{task}', the action '{action}' has a " +
                                       f"success rate of {success_rate:.0%} based on {total} attempts.",
                                metadata={
                                    "success_rate": success_rate,
                                    "sample_size": total,
                                    "last_updated": datetime.now().isoformat()
                                }
                            )
                            break
                elif success_rate >= 0.7 or success_rate <= 0.3:
                    # Create new knowledge for very successful or unsuccessful actions
                    effectiveness = "effective" if success_rate >= 0.7 else "ineffective"
                    confidence = min(0.5 + (total / 20), 0.95)  # Confidence grows with sample size
                    
                    self.knowledge.create(
                        content=f"For task '{task}', the action '{action}' is {effectiveness} " +
                               f"with a success rate of {success_rate:.0%} based on {total} attempts.",
                        category="extracted_knowledge",
                        tags=[task, action, effectiveness],
                        metadata={
                            "task": task,
                            "action": action,
                            "success_rate": success_rate,
                            "sample_size": total,
                            "confidence": confidence,
                            "extracted_at": datetime.now().isoformat()
                        }
                    )
                    extracted_count += 1
        
        print(f"Extracted {extracted_count} knowledge items from experiences")
        return extracted_count

    def evaluate_learning_progress(self) -> Dict[str, Any]:
        """
        Evaluate how well the agent is learning over time.
        
        Returns:
            Dictionary with learning progress metrics
        """
        # Get all experiences sorted by time
        all_experiences = self.experiences.query("")
        if not all_experiences:
            return {"progress": "No experiences yet"}
        
        # Sort by timestamp
        all_experiences.sort(key=lambda x: x.get("timestamp"))
        
        # Split into time periods (e.g., first half vs. second half)
        midpoint = len(all_experiences) // 2
        early_experiences = all_experiences[:midpoint]
        recent_experiences = all_experiences[midpoint:]
        
        # Calculate success rates for each period
        early_success = sum(1 for exp in early_experiences if exp.get("context", {}).get("success", False))
        early_success_rate = early_success / len(early_experiences) if early_experiences else 0
        
        recent_success = sum(1 for exp in recent_experiences if exp.get("context", {}).get("success", False))
        recent_success_rate = recent_success / len(recent_experiences) if recent_experiences else 0
        
        # Calculate improvement
        improvement = recent_success_rate - early_success_rate
        
        return {
            "total_experiences": len(all_experiences),
            "early_success_rate": early_success_rate,
            "recent_success_rate": recent_success_rate,
            "improvement": improvement,
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate,
            "skills_count": len(self.skills.query("")),
            "knowledge_items": len(self.knowledge.query(""))
        }

    def adjust_learning_strategy(self) -> Dict[str, Any]:
        """
        Adjust learning strategy based on performance evaluation.
        
        Returns:
            Dictionary with adjustments made
        """
        # Evaluate current learning progress
        progress = self.evaluate_learning_progress()
        
        adjustments = {
            "previous_learning_rate": self.learning_rate,
            "previous_exploration_rate": self.exploration_rate
        }
        
        # If we don't have enough experiences, do nothing
        if progress.get("total_experiences", 0) < 10:
            return {"status": "Not enough experiences to adjust strategy"}
        
        # Adjust exploration rate based on improvement
        improvement = progress.get("improvement", 0)
        
        if improvement >= 0.1:
            # We're learning well, reduce exploration to exploit knowledge
            self.exploration_rate = max(0.05, self.exploration_rate - 0.05)
        elif improvement <= -0.1:
            # We're doing worse, increase exploration to find better approaches
            self.exploration_rate = min(0.5, self.exploration_rate + 0.1)
        
        # Adjust learning rate based on recent success
        recent_success_rate = progress.get("recent_success_rate", 0)
        
        if recent_success_rate >= 0.8:
            # We're doing well, can afford to learn more aggressively
            self.learning_rate = min(0.3, self.learning_rate + 0.05)
        elif recent_success_rate <= 0.3:
            # We're struggling, be more conservative in learning
            self.learning_rate = max(0.05, self.learning_rate - 0.03)
        
        adjustments.update({
            "new_learning_rate": self.learning_rate,
            "new_exploration_rate": self.exploration_rate,
            "reason": f"Adjusted based on improvement of {improvement:.2f} and " +
                     f"recent success rate of {recent_success_rate:.2f}"
        })
        
        return adjustments

    def plan_approach(self, task: str, available_actions: List[str]) -> List[str]:
        """
        Plan an approach for a task based on knowledge and skills.
        
        Args:
            task: The task to plan for
            available_actions: Available actions to use in the plan
            
        Returns:
            List of actions forming the plan
        """
        # Check if we have a skill for this task
        skills = self.skills.query(task, domain="tasks")
        
        if skills and skills[0].get("steps"):
            # Use existing skill if available
            skill = skills[0]
            steps = skill.get("steps", [])
            success_rate = skill.get("metadata", {}).get("success_rate", 0.0)
            
            # Filter steps to only include available actions
            valid_steps = [step for step in steps if step in available_actions]
            
            if valid_steps:
                print(f"Using learned skill with {len(valid_steps)} steps, " +
                     f"success rate: {success_rate:.2f}")
                return valid_steps
        
        # If no applicable skill, check knowledge for effective actions
        knowledge = self.knowledge.query(task, category="extracted_knowledge")
        
        effective_actions = []
        for item in knowledge:
            metadata = item.get("metadata", {})
            action = metadata.get("action")
            success_rate = metadata.get("success_rate", 0)
            
            if action in available_actions and success_rate >= 0.5:
                effective_actions.append((action, success_rate))
        
        if effective_actions:
            # Sort by success rate
            effective_actions.sort(key=lambda x: x[1], reverse=True)
            plan = [action for action, _ in effective_actions]
            print(f"Created plan with {len(plan)} actions based on knowledge")
            return plan
        
        # If no knowledge, try similar tasks
        similar_tasks = self.skills.query(
            task,
            use_vector=True,
            n_results=3
        )
        
        for similar in similar_tasks:
            if similar.get("task") != task and similar.get("steps"):  # Different task
                # Adapt steps from similar task
                adaptation = [
                    step for step in similar.get("steps", [])
                    if step in available_actions
                ]
                if adaptation:
                    print(f"Adapted plan from similar task: {similar.get('task')}")
                    return adaptation
        
        # If all else fails, create a random plan
        exploration_plan = random.sample(
            available_actions,
            min(3, len(available_actions))
        )
        print("Created exploratory plan")
        return exploration_plan

    def save(self) -> None:
        """Save the agent's memory systems to disk."""
        print(f"Saving agent '{self.name}'...")
        
        # Save all memory systems
        self.knowledge.save_all()
        self.experiences.save_all()
        self.skills.save_all()
        
        print(f"Agent saved successfully")

    def load(self) -> None:
        """Load the agent's memory systems from disk."""
        print(f"Loading agent '{self.name}'...")
        
        # Load all memory systems
        self.knowledge.load_all()
        self.experiences.load_all()
        self.skills.load_all()
        
        # Get statistics
        experience_count = len(self.experiences.query(""))
        knowledge_count = len(self.knowledge.query(""))
        skill_count = len(self.skills.query(""))
        
        print(f"Agent loaded successfully with {experience_count} experiences, " +
              f"{knowledge_count} knowledge items, and {skill_count} skills")

# Example usage
if __name__ == "__main__":
    import os
    
    # Create a simple puzzle solver example
    
    # Define the puzzle environment
    class PuzzleEnvironment:
        def __init__(self):
            self.puzzles = {
                "sorting": {
                    "description": "Sort a list of numbers",
                    "actions": ["bubble_sort", "merge_sort", "quick_sort", "selection_sort"],
                    "optimal": "merge_sort",
                    "difficulty": 0.3
                },
                "searching": {
                    "description": "Find an element in a list",
                    "actions": ["linear_search", "binary_search", "hash_lookup", "tree_search"],
                    "optimal": "binary_search",
                    "difficulty": 0.4
                },
                "pathfinding": {
                    "description": "Find the shortest path in a graph",
                    "actions": ["depth_first", "breadth_first", "dijkstra", "a_star"],
                    "optimal": "a_star",
                    "difficulty": 0.7
                }
            }
        
        def attempt_puzzle(self, puzzle_name, action):
            """Simulate an attempt at solving a puzzle."""
            if puzzle_name not in self.puzzles:
                return False, "Unknown puzzle"
            
            puzzle = self.puzzles[puzzle_name]
            
            if action not in puzzle["actions"]:
                return False, "Invalid action"
            
            # Simple simulation: optimal action always works, others work with
            # decreasing probability based on how "far" they are from optimal
            if action == puzzle["optimal"]:
                success = True
                outcome = f"Successfully solved the puzzle using {action}"
            else:
                # Calculate probability based on distance from optimal in action list
                optimal_idx = puzzle["actions"].index(puzzle["optimal"])
                action_idx = puzzle["actions"].index(action)
                distance = abs(optimal_idx - action_idx)
                success_prob = 0.9 - (distance * 0.2)
                
                success = random.random() < success_prob
                
                if success:
                    outcome = f"Solved the puzzle using {action}, but not optimally"
                else:
                    outcome = f"Failed to solve the puzzle using {action}"
            
            return success, outcome
    
    # Create the persistence directory if it doesn't exist
    os.makedirs("./learning_agent", exist_ok=True)
    
    # Initialize the learning agent and environment
    agent = LearningAgent(
        name="PuzzleSolver",
        persistence_dir="./learning_agent"
    )
    
    env = PuzzleEnvironment()
    
    # Function to run a learning cycle
    def run_learning_cycle(num_cycles=50):
        """Run multiple learning cycles."""
        puzzles = list(env.puzzles.keys())
        
        performance_history = {puzzle: [] for puzzle in puzzles}
        
        for cycle in range(num_cycles):
            # Choose a random puzzle
            puzzle_name = random.choice(puzzles)
            puzzle = env.puzzles[puzzle_name]
            
            print(f"\n--- Cycle {cycle + 1}: {puzzle_name} puzzle ---")
            print(f"Description: {puzzle['description']}")
            
            # Plan approach or choose action
            if random.random() < 0.7:  # 70% of the time, use planning
                plan = agent.plan_approach(puzzle_name, puzzle["actions"])
                print(f"Plan: {plan}")
                
                if plan:
                    action = plan[0]  # Use the first action in the plan
                else:
                    action = agent.choose_action(puzzle_name, puzzle["actions"])
            else:
                action = agent.choose_action(puzzle_name, puzzle["actions"])
            
            print(f"Action chosen: {action}")
            
            # Attempt the puzzle
            success, outcome = env.attempt_puzzle(puzzle_name, action)
            print(f"Outcome: {outcome}")
            
            # Record the experience
            agent.record_experience(
                puzzle_name,
                action,
                outcome,
                success,
                {"puzzle_difficulty": puzzle["difficulty"]}
            )
            
            # Track performance
            performance_history[puzzle_name].append(1 if success else 0)
            
            # Adapt learning based on puzzle difficulty
            if cycle % 5 == 0:
                agent.adapt_learning_rate(puzzle["difficulty"])
            
            # Periodically extract knowledge and improve skills
            if cycle % 10 == 0:
                agent.extract_knowledge_from_experiences()
                
                for puzzle_name in puzzles:
                    agent.improve_skill(puzzle_name)
            
            # Periodically adjust learning strategy
            if cycle % 15 == 0:
                adjustments = agent.adjust_learning_strategy()
                if "status" not in adjustments:
                    print("\nAdjusted learning strategy:")
                    print(f"Learning rate: {adjustments['previous_learning_rate']:.2f} -> {adjustments['new_learning_rate']:.2f}")
                    print(f"Exploration rate: {adjustments['previous_exploration_rate']:.2f} -> {adjustments['new_exploration_rate']:.2f}")
        
        # Show final performance stats
        print("\n=== Learning Performance ===")
        for puzzle_name in puzzles:
            history = performance_history[puzzle_name]
            if history:
                first_half = history[:len(history)//2]
                second_half = history[len(history)//2:]
                
                first_half_success = sum(first_half) / len(first_half) if first_half else 0
                second_half_success = sum(second_half) / len(second_half) if second_half else 0
                
                print(f"{puzzle_name} puzzle:")
                print(f"  Early success rate: {first_half_success:.2f}")
                print(f"  Recent success rate: {second_half_success:.2f}")
                print(f"  Improvement: {second_half_success - first_half_success:.2f}")
        
        # Final reflection
        for puzzle_name in puzzles:
            insights = agent.reflect_on_experiences(puzzle_name)
            
            print(f"\nInsights for {puzzle_name} puzzle:")
            for insight in insights.get("insights", []):
                print(f"- {insight}")
        
        # Show learned skills
        for puzzle_name in puzzles:
            skills = agent.skills.query(puzzle_name, domain="tasks")
            
            if skills:
                skill = skills[0]
                print(f"\nLearned skill for {puzzle_name}:")
                print(f"Steps: {skill.get('steps', [])}")
                print(f"Success rate: {skill.get('metadata', {}).get('success_rate', 0):.2f}")
        
        # Save the agent
        agent.save()
    
    # Run the learning process
    run_learning_cycle(50)
```

## Step 8: Understanding the Results

After running the learning agent, you'll see output showing how it adapts and improves its performance over time. Key aspects to observe:

1. **Learning Curve**: The agent should improve its success rate for each puzzle type over time.

2. **Skill Development**: The agent should develop increasingly effective skills with better success rates.

3. **Knowledge Extraction**: The agent extracts generalizable knowledge from its experiences.

4. **Adaptive Strategy**: The learning rate and exploration rate should adapt based on performance.

5. **Meta-Learning**: The agent becomes better at learning itself over time.

## Step 9: Advanced Applications

This learning agent framework can be extended for various applications:

### Reinforcement Learning

```python
def reinforcement_update(self, task: str, action: str, reward: float) -> None:
    """
    Update knowledge based on reinforcement learning principles.
    
    Args:
        task: The task performed
        action: The action taken
        reward: The reward received (-1.0 to 1.0)
    """
    # Find existing action values for this task
    action_values = {}
    knowledge_items = self.knowledge.query(
        task, 
        category="reinforcement_values"
    )
    
    # Extract current values
    for item in knowledge_items:
        metadata = item.get("metadata", {})
        if metadata.get("task") == task:
            action_values = metadata.get("action_values", {})
            kb_id = item["id"]
            break
    
    # Update or create action values
    alpha = self.learning_rate  # Learning rate
    
    if action_values:
        # Update existing values
        old_value = action_values.get(action, 0.0)
        new_value = old_value + alpha * (reward - old_value)
        action_values[action] = new_value
        
        # Update in knowledge base
        self.knowledge.update(
            kb_id,
            metadata={
                "action_values": action_values,
                "last_updated": datetime.now().isoformat()
            }
        )
    else:
        # Create new entry
        action_values = {action: reward * alpha}
        
        self.knowledge.create(
            content=f"Reinforcement learning values for task: {task}",
            category="reinforcement_values",
            tags=[task, "rl_values"],
            metadata={
                "task": task,
                "action_values": action_values,
                "created_at": datetime.now().isoformat()
            }
        )
```

### Multi-Agent Learning

```python
def share_knowledge(self, other_agent, task: str = None) -> int:
    """
    Share knowledge with another agent.
    
    Args:
        other_agent: Another LearningAgent instance
        task: Optional specific task to share knowledge about
        
    Returns:
        Number of knowledge items shared
    """
    # Query knowledge to share
    query = task if task else ""
    knowledge_filter = {"category": "extracted_knowledge"}
    
    if task:
        knowledge_filter["tags"] = [task]
    
    knowledge_items = self.knowledge.query(query, **knowledge_filter)
    
    shared_count = 0
    
    for item in knowledge_items:
        metadata = item.get("metadata", {})
        confidence = metadata.get("confidence", 0.0)
        
        # Only share high-confidence knowledge
        if confidence >= 0.7:
            # Check if other agent already has this knowledge
            existing = other_agent.knowledge.query(
                item["content"],
                exact_match=True
            )
            
            if not existing:
                # Share the knowledge
                other_agent.knowledge.create(
                    content=item["content"],
                    category=item.get("category", "shared_knowledge"),
                    tags=item.get("tags", []) + ["shared"],
                    metadata={
                        **metadata,
                        "source_agent": self.agent_id,
                        "shared_at": datetime.now().isoformat(),
                        # Reduce confidence slightly when sharing
                        "confidence": confidence * 0.9
                    }
                )
                shared_count += 1
    
    print(f"Shared {shared_count} knowledge items with another agent")
    return shared_count
```

### Transfer Learning

```python
def transfer_learning(self, source_task: str, target_task: str) -> bool:
    """
    Apply knowledge from one task to another similar task.
    
    Args:
        source_task: Task to transfer knowledge from
        target_task: Task to transfer knowledge to
        
    Returns:
        Whether any knowledge was transferred
    """
    # Check if tasks are similar using vector search
    source_skills = self.skills.query(source_task, domain="tasks")
    target_skills = self.skills.query(target_task, domain="tasks")
    
    if not source_skills:
        print(f"No skills found for source task: {source_task}")
        return False
    
    source_skill = source_skills[0]
    source_steps = source_skill.get("steps", [])
    
    if not source_steps:
        print(f"Source task has no steps to transfer")
        return False
    
    if target_skills:
        # Update existing target skill
        target_skill = target_skills[0]
        target_id = target_skill["id"]
        
        # Transfer steps with adjustment for the new task
        self.skills.update(
            target_id,
            content=f"Transferred skill for task: {target_task} (adapted from {source_task})",
            steps=source_steps,
            metadata={
                "adapted_from": source_task,
                "transfer_confidence": 0.6,  # Lower confidence for transferred skills
                "transferred_at": datetime.now().isoformat()
            }
        )
        print(f"Updated target skill for {target_task} with knowledge from {source_task}")
        return True
    else:
        # Create new skill for target task
        self.skills.create(
            content=f"Transferred skill for task: {target_task}",
            task=target_task,
            steps=source_steps,
            prerequisites=[],
            domains=["tasks", "transferred", target_task.lower().replace(" ", "_")],
            metadata={
                "adapted_from": source_task,
                "transfer_confidence": 0.5,
                "success_rate": 0.0,  # No attempts yet
                "attempts": 0,
                "transferred_at": datetime.now().isoformat()
            }
        )
        print(f"Created new skill for {target_task} based on knowledge from {source_task}")
        return True
```

## Conclusion

In this tutorial, we've built a comprehensive learning agent that uses AgentMem's memory systems to:

1. Remember experiences using episodic memory
2. Extract and store knowledge using semantic memory
3. Develop and refine skills using procedural memory
4. Adapt its learning strategy based on performance
5. Plan approaches to tasks using past experiences
6. Apply meta-learning to improve its own learning process

This framework provides a foundation for building adaptive AI agents that can:

- Learn from their experiences
- Improve their performance over time
- Transfer knowledge between tasks
- Share knowledge with other agents
- Adapt to different task difficulties

By leveraging AgentMem's memory systems, we've created an agent that not only solves problems but also learns to solve them more effectively over time, much like humans do.

For more advanced applications, consider extending this agent with:

1. Integration with specific problem domains (e.g., game playing, dialogue systems)
2. More sophisticated planning algorithms
3. Hierarchical skill representation
4. Social learning from multiple agents
5. Long-term curriculum learning across progressive tasks

The AgentMem library provides the flexible memory infrastructure needed to implement these advanced features, making it an excellent foundation for learning-enabled AI agents.