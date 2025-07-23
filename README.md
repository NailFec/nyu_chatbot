### **I. Core AI & Conversation Features**

1.  **Advanced AI Integration (DeepSeek API)**
    *   The chatbot leverages a powerful Large Language Model (LLM) via the DeepSeek API, moving beyond simple scripted responses. All user interactions are processed by the AI for dynamic, context-aware replies.

2.  **Natural Language Understanding (NLU)**
    *   It can understand complex, conversational user requests for booking, querying, and getting recommendations without requiring rigid commands. For example, it can process "I need a powerful GPU for training a LLaMA model sometime next week."

3.  **Function Calling for Real-Time Data**
    *   The AI is equipped with a set of "tools" (functions) it can call to interact with the system's backend data. This allows it to answer questions with live, accurate information from the gpu_inventory.json and bookings.json files.

4.  **Context-Aware, Multi-Turn Conversations**
    *   The system maintains a `conversation_history` for each user session. This allows the chatbot to remember previous parts of the conversation, ask follow-up questions, and gather all necessary information for a complex task (like a booking) over several messages.

5.  **Secure Confirmation Workflow**
    *   For critical operations like booking or canceling, the chatbot uses a two-step confirmation process to prevent accidental actions.
        *   **Preparation Step**: It first calls a `prepare_..._confirmation` function to gather all details and present a formatted summary to the user for review.
        *   **Execution Step**: Only after the user explicitly confirms (e.g., by typing "yes" or "confirm"), the chatbot calls the `confirm_operation` function to execute the transaction.

6.  **AI-Powered GPU Recommendations**
    *   The chatbot can provide intelligent GPU recommendations based on the user's described `use_case` (e.g., "LLaMA 8B training," "4K video rendering," "gaming"), budget, and memory requirements. The logic includes specific suggestions for different types of tasks.

7.  **Rich Markdown & HTML Formatting**
    *   The AI's responses are formatted using Markdown for enhanced readability, including bold text, code blocks, tables, and lists. This is then converted to HTML for the web interface.

### **II. Booking & Inventory Management**

1.  **Real-Time GPU Availability Search**
    *   Users can query for available GPUs. The search can be filtered by:
        *   GPU Model (e.g., RTX-4090)
        *   Specific time range (start and end time)
        *   Minimum VRAM requirement

2.  **End-to-End GPU Booking**
    *   The chatbot guides users through the entire booking process, from initial query to final confirmation. It collects all necessary details: user name, email, desired GPU, and time slot.

3.  **Comprehensive Booking Management**
    *   **Query Bookings**: Users can retrieve details of their existing bookings using their email address, a specific booking ID, or a unique booking hash.
    *   **Secure Cancellation**: Users can cancel a booking, but for security, they must provide both the correct booking hash and the associated email address.

4.  **Dynamic Booking Card Generation**
    *   Upon successful booking or cancellation, the system automatically generates a professional, detailed HTML "booking card." This card is saved as a temporary file and opened in the user's default web browser, providing a persistent, well-formatted receipt of the transaction.

5.  **Detailed GPU & Booking Database**
    *   **GPU Inventory (gpu_inventory.json)**: Manages a catalog of 8 different GPU models (H100, A100, RTX series, etc.), each with multiple instances, detailed specifications (memory, CUDA cores), and pricing.
    *   **Booking Records (bookings.json)**: Stores a comprehensive history of all bookings, including user details, GPU assigned, timing, cost, and status (scheduled, active, completed, cancelled).

### **III. System Architecture & API**

1.  **Unified Flask Application (app.py)**
    *   A single, centralized server handles all functionalities, including the web chat interface, the data dashboard, and all API endpoints, simplifying deployment and management.

2.  **Hybrid Session Management**
    *   The system provides robust multi-user support with session persistence.
        *   **Redis Integration**: If a Redis server is available, it's used for persistent session storage, meaning conversation context survives server restarts.
        *   **In-Memory Fallback**: If Redis is not connected, the application seamlessly falls back to in-memory session storage for development and simple use cases.

3.  **Dual API Structure**
    *   The application offers both stateful and stateless APIs to serve different needs.
        *   **Session-based API (`/api/chat`)**: Uses cookies and session IDs to maintain conversation context, ideal for interactive chat clients.
        *   **Direct/Stateless API (`/api/direct/*`)**: Allows for direct, one-off calls to backend functions (like searching GPUs or getting recommendations) without needing a session, suitable for scripting or integration with other services.

4.  **Comprehensive RESTful Endpoints**
    *   The API exposes all core functionalities:
        *   Chatting (session and direct)
        *   Searching available GPUs
        *   Getting recommendations
        *   Retrieving GPU inventory and booking data
        *   Clearing user sessions

5.  **Debugging and Monitoring Tools**
    *   Special `/debug` endpoints are available for developers:
        *   `/debug/history`: View the full conversation history for the current session.
        *   `/debug/sessions`: See a list of all active user sessions being managed by the server.

### **IV. User Interfaces**

1.  **Interactive Web Chat Interface (chat_interface.html)**
    *   A clean, modern web-based UI for users to chat with the AI assistant directly in their browser.

2.  **Data Visualization Dashboard (timeline_dashboard.html)**
    *   A separate web page that provides a visual timeline of GPU bookings, allowing for an at-a-glance overview of the schedule and resource utilization.

3.  **Command-Line Interface (CLI)**
    *   By running hpc_chatbot.py directly, the system can be used as a traditional command-line chatbot within the terminal.
