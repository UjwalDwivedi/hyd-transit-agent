import os
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from tools import get_current_weather, get_hyderabad_traffic, get_real_events
from langchain_core.messages import SystemMessage, HumanMessage

class TrafficState(TypedDict):
    query: str                      
    city: str                      
    location: Optional[str]         
    weather_data: Optional[str]     
    traffic_data: Optional[str]    
    event_data: Optional[str]       
    final_prediction: Optional[str] 

load_dotenv()

def supervisor_node(state: TrafficState):

    query_text = state.get("query", "")

    groq_key = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, groq_api_key=groq_key)

    messages = [
        SystemMessage(content="You are a data extraction bot. Extract the city or neighborhood name from the user's transit query. Respond ONLY with the location name. If no location is found, respond with 'Hyderabad'."),
        HumanMessage(content=f"Query: {query_text}")
    ]
    
    try:
        response = llm.invoke(messages)
        target_location = response.content.strip()
    except:
        target_location = "Hyderabad"
        
    
    return {
        "city": "Hyderabad", 
        "location": target_location
    }

def event_agent_node(state: TrafficState):
    target_zone = state.get("location", "Hyderabad")

    actual_events = get_real_events(target_zone)
    
    return {"event_data": actual_events}

def weather_agent_node(state: TrafficState):

    actual_weather = get_current_weather(state['city'])
    print(f"    -> Result: {actual_weather}")
    return {"weather_data": actual_weather}

def traffic_agent_node(state: TrafficState):
    target_zone = state.get("location", "Hitech City")

    actual_traffic = get_hyderabad_traffic(target_zone)
    print(f"    -> Result:\n{actual_traffic}")
    return {"traffic_data": actual_traffic}


def predictor_node(state: TrafficState):
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env')
    load_dotenv(dotenv_path=env_path, override=True)

    query = state.get("query", "N/A")
    weather = state.get("weather_data", "No weather data collected.")
    traffic = state.get("traffic_data", "No traffic telemetry collected.")
    events = state.get("event_data", "No event data collected.")

    groq_key = os.getenv("GROQ_API_KEY")

    llm = ChatGroq(
        model="llama-3.1-8b-instant", 
        temperature=0.3,
        groq_api_key=groq_key
    )
    
    messages = [
        SystemMessage(content=(
            "You are an elite Smart City Transit Assistant for Hyderabad. "
            "Your task is to take raw data inputs from specific weather and traffic sensors "
            "and synthesize them into a highly readable, clear, contextual advisory for commuters. "
            "Highlight if there is heavy congestion, list travel advisories based on weather, "
            "and estimate if it's an optimal time to travel."
        )),
        HumanMessage(content=(
            f"User Original Query: {query}\n\n"
            f"Live Sensor Feeds Provided:\n"
            f"1. Weather Feed: {weather}\n"
            f"2. Traffic Flow Telemetry: {traffic}\n"
            f"3. Local Events: {events}\n\n"
            "Draft your sharp response now based on this data."
        ))
    ]
    
    try:
        response = llm.invoke(messages)
        final_answer = response.content
    except Exception as e:
        final_answer = f"LLM Generation failed"
        
    return {"final_prediction": final_answer}

workflow = StateGraph(TrafficState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("weather_agent", weather_agent_node)
workflow.add_node("traffic_agent", traffic_agent_node)
workflow.add_node("event_agent", event_agent_node)
workflow.add_node("predictor", predictor_node)

workflow.set_entry_point("supervisor")
workflow.add_edge("supervisor", "weather_agent")
workflow.add_edge("supervisor", "traffic_agent")
workflow.add_edge("supervisor", "event_agent")
workflow.add_edge("weather_agent", "predictor")
workflow.add_edge("traffic_agent", "predictor")
workflow.add_edge("event_agent", "predictor")
workflow.add_edge("predictor", END)

app = workflow.compile()

if __name__ == "__main__":
    print("="*50)
    print("  Smart City NLP Transit System")
    print(" Type 'quit' to exit.")
    print("="*50)
    
    while True:
        user_input = input("\n[You]: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        if not user_input.strip():
            continue
            
        initial_state = {"query": user_input, "city": "Hyderabad"}
        final_state = initial_state
        
        for output in app.stream(initial_state):
            for key, value in output.items():
                final_state.update(value)
                
        print("\n[Final AI Assistant Summary]:")
        print(final_state.get("final_prediction", "No response generated."))