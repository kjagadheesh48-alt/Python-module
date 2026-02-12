import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool

os.environ["GOOGLE_API_KEY"] = "AIzaSyC7vGxUxsgcjAMS5TLGE7TjeMb6cDt3i90"

# Initialize the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5 flash")

@tool
def syllabus_lookup(query: str) -> str:
    """Look up syllabus information for a given course name."""
    # Simulated syllabus data
    syllabi = {
        "operating system": """Operating Systems Syllabus:
1. Process Management (Processes, Threads, Scheduling)
2. Memory Management (Paging, Segmentation, Virtual Memory)
3. File Systems (File organization, Directory structures)
4. I/O Systems (Device drivers, Disk scheduling)
5. Synchronization (Semaphores, Monitors, Deadlocks)""",
        
        "computer networks": """Computer Networks Syllabus:
1. Application Layer (HTTP, FTP, DNS)
2. Transport Layer (TCP, UDP, Congestion control)
3. Network Layer (IP routing, Subnetting)
4. Link Layer (Ethernet, MAC protocols)
5. Physical Layer (Signals, Encoding)"""
    }
    
    # Case-insensitive lookup
    query_lower = query.lower()
    for key, value in syllabi.items():
        if key in query_lower:
            return value
    
    return f"No syllabus found for: {query}"

def demonstrate_agentic_ai():
    """Demonstration of Agentic AI - Agents that can reason and use tools"""
    print("=== AGENTS: Reasoning with Tools ===\n")
    
    # Try to import modern agent creation functions
    try:
        from langchain.agents import create_tool_calling_agent, AgentExecutor
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        # Modern approach with tool-calling agent
        print("Using modern LangChain agent creation\n")
        
        # Define the prompt for the agent
        agent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful teaching assistant. You have access to tools that can help you answer questions.
            Always use the syllabus_lookup tool when asked about course syllabi, topics, or curriculum.
            After getting the tool output, provide a clear, educational response."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the tool-calling agent
        agent = create_tool_calling_agent(
            llm=llm,
            tools=[syllabus_lookup],
            prompt=agent_prompt
        )
        
        # Create the executor that runs the agent loop
        agent_executor = AgentExecutor(
            agent=agent,
            tools=[syllabus_lookup],
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        # Example 1: Operating System syllabus
        print("--- Example 1: Operating System Query ---")
        result1 = agent_executor.invoke({
            "input": "What is in the Operating System syllabus? Please use the syllabus lookup tool."
        })
        print(f"\nAgent Response:\n{result1['output']}\n")
        print("-" * 50, "\n")
        
        # Example 2: Computer Networks syllabus
        print("--- Example 2: Computer Networks Query ---")
        result2 = agent_executor.invoke({
            "input": "What topics are covered in Computer Networks? Use the tool to find out."
        })
        print(f"\nAgent Response:\n{result2['output']}\n")
        
    except ImportError as e:
        print(f"Modern agent imports not available: {e}")
        print("Falling back to simple agent demonstration...")
        demonstrate_simple_agent()

def demonstrate_simple_agent():
    """Simplified agent demonstration when imports fail"""
    print("\nUsing Simplified Agent Demonstration:\n")
    
    class SimpleAgent:
        """Simple demonstration of an agent that reasons and uses tools"""
        def __init__(self, llm, tools):
            self.llm = llm
            self.tools = {tool.name: tool for tool in tools}
        
        def process_query(self, user_query):
            """Process a query with reasoning and tool use"""
            print(f"[Agent] Received query: {user_query}")
            
            # Step 1: Reason about whether to use a tool
            reasoning_prompt = f"""You are a teaching assistant. Analyze this request:
            
Request: {user_query}

Available tools: {list(self.tools.keys())}
- syllabus_lookup: Use this to get syllabus information for courses

Do you need to use a tool to answer this question?
Respond in this format:
THOUGHT: [your reasoning]
ACTION: [YES/NO]
TOOL: [tool name if YES, else NONE]"""
            
            reasoning_response = self.llm.invoke(reasoning_prompt)
            reasoning_text = reasoning_response.content if hasattr(reasoning_response, 'content') else str(reasoning_response)
            print(f"\n[Agent Reasoning]\n{reasoning_text}")
            
            # Step 2: Execute tool if needed
            if "ACTION: YES" in reasoning_text:
                tool_name = "syllabus_lookup"
                print(f"\n[Agent Action] Using tool: {tool_name}")
                
                try:
                    tool_result = self.tools[tool_name].invoke(user_query)
                    print(f"[Tool Result] Retrieved: {tool_result[:100]}...")
                    
                    # Step 3: Synthesize response
                    synthesis_prompt = f"""Based on this syllabus information:
{tool_result}

Question: {user_query}

Provide a helpful, educational response that explains the key topics and concepts."""
                    
                    final_response = self.llm.invoke(synthesis_prompt)
                    return final_response.content if hasattr(final_response, 'content') else str(final_response)
                    
                except Exception as tool_error:
                    print(f"[Tool Error] {tool_error}")
                    return f"Error using tool: {tool_error}"
            else:
                print("\n[Agent Action] Answering directly without tools")
                direct_prompt = f"Question: {user_query}\n\nAnswer concisely and helpfully:"
                direct_response = self.llm.invoke(direct_prompt)
                return direct_response.content if hasattr(direct_response, 'content') else str(direct_response)
    
    # Create and run the simple agent
    simple_agent = SimpleAgent(llm, [syllabus_lookup])
    
    # Test queries
    test_queries = [
        "What topics are covered in Operating System syllabus?",
        "Tell me about Computer Networks curriculum"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Example {i}: {query} ---")
        try:
            response = simple_agent.process_query(query)
            print(f"\n[Final Response]\n{response}")
            print("\n" + "-" * 50)
        except Exception as e:
            print(f"Agent execution error: {e}")

if __name__ == "__main__":
    demonstrate_agentic_ai()