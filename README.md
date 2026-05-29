# Multi-Agent Travel Planner 🌍✈️

## AI-Powered Travel Planning using LangGraph & Multi-Agent Systems

### Project Overview
This project builds a production-ready Multi-Agent Travel Planning system using LangGraph, OpenAI, Tavily Search, and SerpAPI. Multiple specialized AI agents work in parallel to search for flights, hotels, and plan complete travel itineraries — all from a single natural language query.

### What It Does
- ✅ Searches flights and hotels based on user preferences
- ✅ Plans complete day-by-day travel itineraries
- ✅ Answers travel-related questions with real-time web research
- ✅ Auto-detects currency based on destination country
- ✅ Handles any destination worldwide
- ✅ Runs multiple agents in parallel for faster results

---

## 🏗️ Architecture

```
User Query
    ↓
┌─────────────────────────────────────┐
│  Search Agent    │  Itinerary Agent  │  ← Parallel Execution
│  (Flights/Hotels)│  (Day-by-day plan)│
└─────────────────────────────────────┘
            ↓
      Synthesizer Agent
      (Combines everything)
            ↓
   ✅ Complete Travel Report
```

### Agents
- **Search Agent** — Searches for real-time flight and hotel information using Tavily
- **Itinerary Agent** — Creates detailed day-by-day travel plans with timings and costs
- **Synthesizer Agent** — Combines results from both agents into one beautiful report

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/pranathi1107/multi-agent-travel-planner.git
cd multi-agent-travel-planner
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install python-dotenv langgraph langchain langchain-openai langchain-tavily tavily-python deepagents google-search-results ipykernel
```

### 4. Configure API Keys

Create a `.env` file:
```bash
touch .env
```

Add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here
```

### 5. Run the Travel Agent
```bash
python3 travel_agent.py
```

You will be prompted:
```
🌍 Enter your travel query: Plan a 5 day trip to Paris for 2 people in June 2025
```

---

## 🔑 Getting API Keys

| API | Cost | Link |
|---|---|---|
| OpenAI | Paid (cheap) | [platform.openai.com](https://platform.openai.com) |
| Tavily | Free tier available | [app.tavily.com](https://app.tavily.com) |
| SerpAPI | 100 free searches/month | [serpapi.com](https://serpapi.com) |

---

## 📁 Project Structure

```
multi-agent-travel-planner/
├── README.md               # This file
├── travel_agent.py         # Main multi-agent system
├── .env                    # API keys (never commit this!)
├── .gitignore             # Git ignore rules
└── venv/                  # Virtual environment (never commit this!)
```

---

## 💬 Example Queries

```
Plan a 5 day trip to Paris for 2 people in June 2025
Plan a 3 day trip to Tokyo Japan for 1 person in July 2025
Plan a 7 day trip to New York USA for a family of 4
Plan a weekend trip to Dubai for 2 people in December 2025
Plan a 10 day trip to India for 2 people in January 2025
```

---

## 💰 Example Output

```
============================================================
✈️ FINAL TRAVEL RECOMMENDATION:
============================================================
# Travel Recommendation Report: 5-Day Trip to Paris

## Overview
A delightful 5-day itinerary for two people visiting Paris in June 2025...

## Day 1: Arrival and Exploring Montmartre
Morning: Arrive at CDG Airport...
Afternoon: Visit Sacré-Cœur...
Evening: Dinner at Le Refuge des Fondus...

## Estimated Costs for Two People
- Accommodation: €750
- Meals: €450
- Transportation: €80
- Total: €1,880
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **LangGraph** | Multi-agent orchestration & workflow |
| **LangChain** | LLM framework & tool integration |
| **OpenAI GPT-4o-mini** | Language model for generating responses |
| **Tavily Search** | Real-time web search for travel info |
| **SerpAPI** | Google Flights & Hotels search |
| **Python-dotenv** | Secure API key management |

---

## ⚙️ Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here
```

### Supported Currencies
The agent auto-detects currency based on destination:

| Region | Currency |
|---|---|
| India | INR (₹) |
| USA | USD ($) |
| Europe | EUR (€) |
| UK | GBP (£) |
| Japan | JPY (¥) |
| Dubai | AED (د.إ) |
| And 50+ more... | Auto-detected |

---

## 🛠️ Troubleshooting

### ModuleNotFoundError
```bash
pip install langchain-tavily
pip install google-search-results
```

### API Key Errors
- Verify keys in `.env` file
- Make sure no spaces around `=`
- Check API credits/limits

### OpenAI Model Error
Change model in `travel_agent.py`:
```python
llm = ChatOpenAI(model="gpt-4o-mini")  # cheaper option
```

---

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Tavily API Docs](https://docs.tavily.com/)
- [SerpAPI Documentation](https://serpapi.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)

---

## 🎯 Skills Demonstrated

- Multi-Agent System Design
- LangGraph Workflow Orchestration
- Real-time Web Search Integration
- API Integration & Management
- Parallel Agent Execution
- Prompt Engineering
- Python Development

