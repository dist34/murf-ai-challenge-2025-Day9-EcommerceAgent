🎧 E-Commerce Voice Shopping Assistant
======================================

### Day 9 -- Murf AI Voice Agent Challenge

This project implements a **voice-driven shopping assistant** inspired by the **Agentic Commerce Protocol (ACP)**.\
Users can browse a product catalog, add items to cart, and place an order completely through **voice commands**.

Built using:

-   **LiveKit Agents**

-   **Google Gemini LLM**

-   **Deepgram STT**

-   **Murf Falcon TTS**

-   **Python merchant backend**

* * * * *

🚀 Features
-----------

### **1\. Voice-Driven Shopping Flow**

Users speak naturally, e.g.:

-   "Show me all hoodies under 1500."

-   "Do you have mugs in blue?"

-   "Add the second hoodie in size L."

-   "Place my order."

The system understands intent, resolves product references, and triggers backend commerce logic.

* * * * *

### **2\. ACP-Inspired Merchant Backend**

A structured commerce layer handles:

-   Product catalog

-   Product filtering

-   Cart operations

-   Order creation

-   Order persistence

The architecture separates:

-   **LLM + voice logic**

-   **Merchant functions (list_products, add_to_cart, place_order)**

This mimics ACP's separation of concerns.

* * * * *

### **3\. Persistent Order Storage**

All orders are stored inside:

`orders.json`

Each order includes:

-   Order ID

-   Line items

-   Quantity

-   Unit price & totals

-   Currency

-   Timestamp

-   Status

The product catalog lives in:

`products.json`

* * * * *

### **4\. Natural Voice Experience**

The agent uses:

-   **Deepgram STT** for speech recognition

-   **Google Gemini 2.5 Flash** for conversation + tool calling

-   **Murf Falcon (fastest TTS API)** for expressive voice responses

-   **Silero VAD + Turn detection** for smooth conversational turns

* * * * *

🏗 Project Structure
--------------------

`backend/
└── src/
    ├── agent.py          # Main Voice Agent
    ├── products.json     # Product catalog
    ├── orders.json       # Persisted orders
    └── ...`

* * * * *

📦 Installation & Setup
-----------------------

### 1\. Install dependencies

`pip install -r requirements.txt`

### 2\. Set environment variables

Create `.env.local`:

`MURF_API_KEY=...
GOOGLE_APPLICATION_CREDENTIALS=...
DEEPGRAM_API_KEY=...`

### 3\. Start the LiveKit Agent Worker

`python src/agent.py`

### 4\. Open your browser client

Connect your frontend or LiveKit test page to the agent room.

* * * * *

💳 Order Format (orders.json)
-----------------------------

Example entry:

`{
  "id": "order-7d0fba4f",
  "items": [
    {
      "product_id": "hoodie-black-01",
      "name": "Black Warrior Hoodie",
      "unit_price": 1499,
      "quantity": 1,
      "line_total": 1499,
      "attrs": {
        "size": "L"
      }
    }
  ],
  "total": 1499,
  "currency": "INR",
  "status": "CONFIRMED",
  "created_at": "2025-11-30T12:48:47Z"
}`

* * * * *

🧠 How the Agent Works
----------------------

### **1\. Voice Input → STT (Deepgram)**

User speaks → converted to text.

### **2\. LLM (Gemini) interprets intent**

LLM decides if it needs to call a tool like:

-   `show_catalog`

-   `add_to_cart`

-   `show_cart`

-   `place_order`

-   `last_order`

### **3\. Merchant backend executes logic**

Python functions handle filtering, cart manipulation, and order creation.

### **4\. Agent speaks the response using Murf Falcon**

Natural conversational feedback to user.

* * * * *

🎯 Challenge Requirements Satisfied
-----------------------------------

-   ✔ Voice-based product browsing

-   ✔ ACP-inspired backend

-   ✔ Structured product model

-   ✔ Order model with line items + metadata

-   ✔ Cart-based order placement

-   ✔ Persistent saved orders

-   ✔ Fetch last order

-   ✔ Proper LLM tool-calling flow

-   ✔ Clean separation of conversation + commerce layers
