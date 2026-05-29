# ============================================
# STEP 1 — Load API Keys
# ============================================
import os
from dotenv import load_dotenv

load_dotenv()  # reads your .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

print("✅ OpenAI:", "Loaded" if OPENAI_API_KEY else "❌ Missing")
print("✅ Tavily:", "Loaded" if TAVILY_API_KEY else "❌ Missing")
print("✅ SerpAPI:", "Loaded" if SERPAPI_API_KEY else "❌ Missing")

# ============================================
# STEP 2 — Set Up the LLM (ChatOpenAI)
# ============================================
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",  # cheaper & faster than gpt-4
    temperature=0.2,       # low = more focused answers
    api_key=OPENAI_API_KEY
)

print("✅ LLM ready!")

# Quick test
response = llm.invoke("Say hello in one sentence!")
print("🤖 LLM Test:", response.content)

# ============================================
# STEP 3 — Set Up Tavily Web Search Tool
# ============================================
from langchain_tavily import TavilySearch

internet_search = TavilySearch(
    max_results=5,          # return top 5 results
    topic="general",        # general web search
    search_depth="advanced" # deep search for better results
)

print("✅ Tavily Search ready!")

# Quick test
test_search = internet_search.invoke({"query": "Top tourist attractions in Paris"})
print("🔍 Search Test:", str(test_search)[:200])

# ============================================
# STEP 4 — Set Up SerpAPI Flight & Hotel Search
# ============================================
from serpapi import GoogleSearch

def search_flights(origin, destination, date):
    params = {
        "engine": "google_flights",
        "departure_id": origin,       # e.g. "JFK"
        "arrival_id": destination,    # e.g. "LHR"
        "outbound_date": date,        # e.g. "2025-06-01"
        "currency": "USD",
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("best_flights", [])

def search_hotels(location, check_in, check_out):
    params = {
        "engine": "google_hotels",
        "q": f"hotels in {location}",
        "check_in_date": check_in,    # e.g. "2025-06-01"
        "check_out_date": check_out,  # e.g. "2025-06-05"
        "currency": "USD",
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("properties", [])

print("✅ Flight & Hotel Search ready!")

# ============================================
# STEP 5 — Define the State
# ============================================
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages

class TravelState(TypedDict):
    user_query: str           # what the user asked
    messages: Annotated[list, add_messages]  # conversation history
    search_results: list      # flight & hotel results
    itinerary: str            # planned travel itinerary
    final_answer: str         # final combined response

print("✅ State defined!")

# ============================================
# STEP 6 — Build the Search Agent
# ============================================
from langchain_core.messages import HumanMessage, SystemMessage

def search_agent(state: TravelState):
    print("🔍 Search Agent running...")

    # System prompt — tells agent what its job is
    system_prompt = """You are a travel search specialist.
    Your job is to search for flights and hotels based on user request.
    Extract origin, destination, travel dates from the user query.
    Return a clear summary of available flights and hotels."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_query"])
    ]

    # Search for flights and hotels using Tavily
    search_results = internet_search.invoke(
        {"query": f"flights and hotels for {state['user_query']}"}
    )

    # LLM summarizes the search results
    search_summary = llm.invoke(
        messages + [HumanMessage(content=f"Search results: {str(search_results)[:1000]}")]
    )

    return {
        "search_results": [str(search_results)[:500]],
        "messages": [search_summary]
    }

print("✅ Search Agent defined!")

# ============================================
# STEP 7 — Build the Itinerary Agent
# ============================================
def itinerary_agent(state: TravelState):
    print("🗺️ Itinerary Agent running...")

    # System prompt — tells agent what its job is
    system_prompt = """You are a professional travel itinerary planner.
    Your job is to create a detailed day-by-day travel itinerary.
    Include:
    - Day by day activities (morning, afternoon, evening)
    - Specific places to visit with timings
    - Local food recommendations
    - Transportation tips
    - Estimated costs
    Make it practical, realistic and exciting!"""

    # Search for travel information about the destination
    travel_info = internet_search.invoke(
        {"query": f"best things to do travel guide {state['user_query']}"}
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
        User Request: {state['user_query']}
        Search Results: {str(travel_info)[:1000]}
        Please create a detailed itinerary.
        """)
    ]

    # LLM creates the itinerary
    itinerary_response = llm.invoke(messages)

    return {
        "itinerary": itinerary_response.content,
        "messages": [itinerary_response]
    }

print("✅ Itinerary Agent defined!")

# ============================================
# STEP 8 — Build the Synthesizer Agent
# ============================================
def synthesizer_agent(state: TravelState):
    print("✍️ Synthesizer Agent running...")

    # Combines results from both agents into one final answer
    system_prompt = """You are a travel assistant that combines 
    search results and itinerary into one beautiful, 
    well-structured travel recommendation report."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
        User Request: {state['user_query']}

        Flight & Hotel Search Results:
        {str(state.get('search_results', []))[:500]}

        Planned Itinerary:
        {state.get('itinerary', 'No itinerary yet')}

        IMPORTANT: Show ALL prices and costs in {detected_currency} only.
        Please combine these into one complete travel recommendation!
        """)
    ]

    final_response = llm.invoke(messages)

    return {
        "final_answer": final_response.content,
        "messages": [final_response]
    }

print("✅ Synthesizer Agent defined!")

# ============================================
# STEP 9 — Build the Graph (Connect the Agents)
# ============================================
from langgraph.graph import StateGraph, START, END

def build_travel_agent():
    # Create the graph
    builder = StateGraph(TravelState)

    # Add all 3 agents as nodes
    builder.add_node("search_agent", search_agent)
    builder.add_node("itinerary_agent", itinerary_agent)
    builder.add_node("synthesizer", synthesizer_agent)

    # Connect the flow
    builder.add_edge(START, "search_agent")       # Start → Search Agent
    builder.add_edge(START, "itinerary_agent")    # Start → Itinerary Agent (parallel!)
    builder.add_edge("search_agent", "synthesizer")    # Search → Synthesizer
    builder.add_edge("itinerary_agent", "synthesizer") # Itinerary → Synthesizer
    builder.add_edge("synthesizer", END)          # Synthesizer → End

    return builder.compile()

# Build the agent
travel_agent = build_travel_agent()
print("✅ Travel Agent Graph built!")

# ============================================
# STEP 10 — Run the Travel Agent!
# ============================================
print("\n" + "="*60)
print("🌍 TRAVEL AGENT STARTING...")
print("="*60 + "\n")

# Your travel query!
destination = input("🌍 Enter your travel query: ")

# Auto-detect currency based on destination
currency_map = {
    # Europe
    "ireland": "EUR (€)", "france": "EUR (€)", "germany": "EUR (€)",
    "italy": "EUR (€)", "spain": "EUR (€)", "portugal": "EUR (€)",
    "netherlands": "EUR (€)", "belgium": "EUR (€)", "austria": "EUR (€)",
    "greece": "EUR (€)", "finland": "EUR (€)", "luxembourg": "EUR (€)",
    "paris": "EUR (€)", "rome": "EUR (€)", "barcelona": "EUR (€)",
    "amsterdam": "EUR (€)", "berlin": "EUR (€)", "athens": "EUR (€)",
    "uk": "GBP (£)", "england": "GBP (£)", "london": "GBP (£)",
    "scotland": "GBP (£)", "wales": "GBP (£)",
    "switzerland": "CHF (Fr)", "zurich": "CHF (Fr)", "geneva": "CHF (Fr)",
    "norway": "NOK (kr)", "oslo": "NOK (kr)",
    "sweden": "SEK (kr)", "stockholm": "SEK (kr)",
    "denmark": "DKK (kr)", "copenhagen": "DKK (kr)",
    "poland": "PLN (zł)", "warsaw": "PLN (zł)",
    "czech": "CZK (Kč)", "prague": "CZK (Kč)",
    "hungary": "HUF (Ft)", "budapest": "HUF (Ft)",
    "croatia": "EUR (€)", "dubrovnik": "EUR (€)",
    "turkey": "TRY (₺)", "istanbul": "TRY (₺)",
    "russia": "RUB (₽)", "moscow": "RUB (₽)",

    # Asia
    "india": "INR (₹)", "delhi": "INR (₹)", "mumbai": "INR (₹)",
    "bangalore": "INR (₹)", "chennai": "INR (₹)", "kolkata": "INR (₹)",
    "hyderabad": "INR (₹)", "goa": "INR (₹)", "jaipur": "INR (₹)",
    "japan": "JPY (¥)", "tokyo": "JPY (¥)", "osaka": "JPY (¥)",
    "kyoto": "JPY (¥)",
    "china": "CNY (¥)", "beijing": "CNY (¥)", "shanghai": "CNY (¥)",
    "south korea": "KRW (₩)", "korea": "KRW (₩)", "seoul": "KRW (₩)",
    "singapore": "SGD (S$)",
    "thailand": "THB (฿)", "bangkok": "THB (฿)", "phuket": "THB (฿)",
    "vietnam": "VND (₫)", "hanoi": "VND (₫)", "ho chi minh": "VND (₫)",
    "indonesia": "IDR (Rp)", "bali": "IDR (Rp)", "jakarta": "IDR (Rp)",
    "malaysia": "MYR (RM)", "kuala lumpur": "MYR (RM)",
    "philippines": "PHP (₱)", "manila": "PHP (₱)",
    "hong kong": "HKD (HK$)",
    "taiwan": "TWD (NT$)", "taipei": "TWD (NT$)",
    "nepal": "NPR (₨)", "kathmandu": "NPR (₨)",
    "sri lanka": "LKR (₨)", "colombo": "LKR (₨)",
    "pakistan": "PKR (₨)", "karachi": "PKR (₨)",
    "bangladesh": "BDT (৳)", "dhaka": "BDT (৳)",
    "myanmar": "MMK (K)", "yangon": "MMK (K)",
    "cambodia": "KHR (៛)", "phnom penh": "KHR (៛)",

    # Middle East
    "dubai": "AED (د.إ)", "abu dhabi": "AED (د.إ)", "uae": "AED (د.إ)",
    "saudi arabia": "SAR (﷼)", "riyadh": "SAR (﷼)",
    "qatar": "QAR (﷼)", "doha": "QAR (﷼)",
    "kuwait": "KWD (د.ك)",
    "bahrain": "BHD (BD)",
    "oman": "OMR (﷼)", "muscat": "OMR (﷼)",
    "israel": "ILS (₪)", "tel aviv": "ILS (₪)",
    "jordan": "JOD (د.أ)", "amman": "JOD (د.أ)",

    # Americas
    "usa": "USD ($)", "america": "USD ($)",
    "new york": "USD ($)", "los angeles": "USD ($)",
    "chicago": "USD ($)", "miami": "USD ($)",
    "las vegas": "USD ($)", "san francisco": "USD ($)",
    "washington": "USD ($)", "boston": "USD ($)",
    "canada": "CAD (C$)", "toronto": "CAD (C$)",
    "vancouver": "CAD (C$)", "montreal": "CAD (C$)",
    "mexico": "MXN ($)", "mexico city": "MXN ($)", "cancun": "MXN ($)",
    "brazil": "BRL (R$)", "rio": "BRL (R$)", "sao paulo": "BRL (R$)",
    "argentina": "ARS ($)", "buenos aires": "ARS ($)",
    "colombia": "COP ($)", "bogota": "COP ($)",
    "peru": "PEN (S/)", "lima": "PEN (S/)", "machu picchu": "PEN (S/)",
    "chile": "CLP ($)", "santiago": "CLP ($)",

    # Africa
    "south africa": "ZAR (R)", "cape town": "ZAR (R)",
    "johannesburg": "ZAR (R)",
    "egypt": "EGP (£)", "cairo": "EGP (£)",
    "morocco": "MAD (د.م.)", "marrakech": "MAD (د.م.)",
    "kenya": "KES (KSh)", "nairobi": "KES (KSh)",
    "tanzania": "TZS (TSh)", "zanzibar": "TZS (TSh)",
    "ethiopia": "ETB (Br)", "addis ababa": "ETB (Br)",
    "ghana": "GHS (₵)", "accra": "GHS (₵)",
    "nigeria": "NGN (₦)", "lagos": "NGN (₦)",

    # Oceania
    "australia": "AUD (A$)", "sydney": "AUD (A$)",
    "melbourne": "AUD (A$)", "brisbane": "AUD (A$)",
    "new zealand": "NZD (NZ$)", "auckland": "NZD (NZ$)",
    "fiji": "FJD (FJ$)",

    # Default
    "europe": "EUR (€)",
}

# Detect currency from query
detected_currency = "USD ($)"  # default
for country, currency in currency_map.items():
    if country.lower() in destination.lower():
        detected_currency = currency
        break

print(f"💰 Detected Currency: {detected_currency}")

result = travel_agent.invoke({
    "user_query": destination,
    "messages": [],
    "search_results": [],
    "itinerary": "",
    "final_answer": ""
})

print("\n" + "="*60)
print("✈️ FINAL TRAVEL RECOMMENDATION:")
print("="*60)
print(result["final_answer"])