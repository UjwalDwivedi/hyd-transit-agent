
# Hyderabad Smart City Transit Agent (hyd-transit-agent)

An intelligent, multi-agent conversational transit assistant for Hyderabad. This system leverages LangGraph to orchestrate parallel data streams—combining live weather metadata, real-time TomTom traffic telemetry, and web-scraped local events—into a unified, context-aware commuter advisory synthesized via Groq (Llama 3.1).

---

## System Architecture

The application is built as a stateful graph where a central NLP Supervisor node dynamically assesses user intent before broadcasting requests to specialized worker agents in parallel.

               [ User Input ]
                      │
                      ▼
             [ Supervisor Node ]
         (NLP Location Extraction)
             /        |        \
            /         |         \
           ▼          ▼          ▼
   [Weather Agent] [Traffic Agent] [Event Agent]
   (OpenWeather)     (TomTom)       (DDGS Scraper)
           \          |          /
            \         |         /
             ▼        ▼        ▼
            [ Predictor Node ]
         (Groq Llama 3.1 Synthesis)
                      │
                      ▼
         [ Context-Aware Advisory ]

---

## Core Components & Features

* **NLP Supervisor / Assessor Node:** Uses Groq to parse natural, casual human language queries (e.g., "Is it going to rain near Kukatpally if I head out in an hour?") and cleanly extract the target neighborhood or landmark, bypassing rigid keyword matching.
* **Traffic Agent Node (TomTom API):** Computes real-time traffic congestion levels by comparing live street-level speeds against standard free-flow parameters.
* **Weather Agent Node (OpenWeather API):** Fetches immediate environmental variables critical to commuting, such as temperature, precipitation conditions, and road visibility constraints.
* **Event Agent Node (DDGS Web Scraper):** Dynamically scrapes the web using DuckDuckGo Search (ddgs) to identify high-impact local public events, festivals, or schedules matching the location to anticipate upcoming pedestrian or vehicular gridlock.
* **Predictor Node (Groq Llama-3.1-8b-instant):** Synthesizes the raw JSON payloads from all three parallel streams into a polished, executive-level travel advisory.

---

## Tech Stack

* **Orchestration:** LangGraph / LangChain Core
* **LLM Provider:** Groq Cloud API (llama-3.1-8b-instant)
* **Data Feeds:** TomTom Traffic API, OpenWeather API, DuckDuckGo Search Scraper (ddgs)
* **Environment Management:** Python dotenv

---

Example Interactive Sequence:

Smart City NLP Transit System
Type 'quit' to exit.
==================================================

[You]: How is the traffic looking around Hitech City right now?

[Supervisor]: Assessing NLP query to extract target location...
    -> Extracted Location: Hitech City
[Weather Agent]: Fetching real-time weather for Hyderabad...
[Traffic Agent]: Querying live traffic telemetry for Hitech City...
[Event Agent]: Scraping live web events for Hitech City...

[Final AI Assistant Summary]:
TRAFFIC ADVISORY: Gachibowli to Hitech City route is experiencing heavy congestion (speeds dropped to 18 km/h due to waterlogging from recent overcast showers). 
LOCAL EVENT IMPACT: An exhibition is underway at the HITEX Exhibition Center, causing high pedestrian cross-traffic near Cyber Towers. 
RECOMMENDATION: Delay non-essential travel by 45 minutes or opt for the Hyderabad Metro to avoid gridlock.
