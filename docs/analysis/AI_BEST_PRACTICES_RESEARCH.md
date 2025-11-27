# Clean Architecture & Service Boundaries

Adopt a layered, domain-driven design so that AI calls are isolated from core business logic.  For example, use separate layers/modules – e.g. a Domain layer with survival-gear entities and rules, an Application/Service layer orchestrating workflows, an Infrastructure layer handling external calls (databases, LLM APIs), and a Presentation/API layer (FastAPI endpoints).  In practice, implement an AIService (in Infrastructure) that encapsulates all LLM interactions (via OpenRouter) and is injected into your application logic (Presentation layer) via FastAPI’s dependency injection.  This ensures the business logic (recommending gear) doesn’t depend on OpenRouter or FastAPI specifics.  Define clear interfaces or repository patterns for inventory and user data, so AI calls become just another external dependency. For example, Kumar et al. use an AIService class with methods (and caching) injected into FastAPI routes. This clean layering (domain→application→infrastructure→API) yields maintainability and testability.

Separate Concerns: Keep “what gear to recommend” logic in domain/use-case classes; have a PromptFactory build LLM prompts; and an AIService that calls OpenRouter.  Inject these via FastAPI dependencies so routes remain thin.

Dependency Injection: Define interfaces (e.g. IGearRepository) for data access. The LLM integration should call these interfaces (or use retrieved data) rather than hardcode queries.

Stateless Services: Make the AIService and related components stateless or idempotent, using external storage (cache, DB) for state. This allows horizontal scaling (e.g. deploying on multiple instances or serverless functions).

Microservice Option: If scale demands or organizational separation, consider running AI logic as a separate microservice. But even within one FastAPI app, logically isolate it (as above) so you could extract it later.


# Prompt Engineering Best Practices

Design prompts to be clear, specific, and unambiguous. Always describe the task, expected answer format, and provide context (climate, terrain, user profile, etc.) to “ground” the model. For example, start with a system or first message like: “You are an expert survival gear recommender. Given the user’s trip details and inventory, return a JSON list of needed items.” Then in the user prompt include explicit requirements (terrain type, climate conditions) and any relevant user constraints. Use few-shot examples if needed to illustrate format and style, and specify tone or verbosity if relevant. Iteratively refine prompts: test outputs, examine errors, and adjust wording until results are reliable.

Explicit Instructions: Tell the model exactly what data to produce and how (e.g. “List each recommended item with keys: name, category, reason”). Clearly define any domain-specific terms (e.g. “ALICE pack” or “synthetic insulation”). Avoid vague queries like “What should I pack?” without structure.

System Messages: Use a system prompt layer to set rules (e.g. “Do not suggest illegal or unsafe items” or “Answer only based on given info”) to guard against off-topic or hallucinated responses.

Temperature/Creativity: For factual or recommendation tasks, keep model temperature low (~0) to favor consistency and reduce randomness. Only raise temperature when creativity is desired (e.g. storytelling about survival tips).

Conciseness: Keep prompts as brief as possible while providing needed context. Long prompts can introduce noise. CloudSquid notes that “shorter prompts often outperform longer ones” due to focus.

Prompt Templates: Factor out static parts of prompts into reusable templates (for each feature/endpoint). Have a PromptFactory module that, given parameters (user_profile, context, etc.), returns a fully-formed prompt. This ensures consistency and maintainability.


# Enforcing Structured (JSON) Responses

To parse AI output automatically, enforce a structured JSON format.  Modern LLM APIs support structured output modes or function calls. You should:

Supply a JSON Schema or Format: In the system/user prompt, include a clear JSON schema or example. For instance, “Respond ONLY with a JSON object matching: { items: [ {name: string, weight_kg: number, category: string, rationale: string} ] }.” Many models now honor a provided schema (OpenRouter calls this structured outputs, a subset of tool-calling).

Use JSON Mode or Function Call: If using OpenAI (via OpenRouter), set response_format={"type":"json_object"} or invoke as a function call. This forces the model to output valid JSON. The Instructor library example shows defining a Pydantic response model and instructing the model to match it.

Prompt Conventions: Tell the model explicitly: “Output must be valid JSON with no extraneous text.” You can start/stop delimiters (e.g. json ...) but many new APIs do this automatically.

Validation Post-Processing: On the backend, validate/parsing the returned JSON (e.g. with Pydantic). If parsing fails or required fields are missing, treat it as an error or retry with a clearer prompt. For fallback, you might strip any extra text and attempt to JSON-parse.

Benefits: Well-structured output “helps integrate the model’s responses into workflows without cleanup” – it “reduces ambiguity and hallucinations” by constraining the answer.   Tasks like listing gear are ideal for JSON (fixed fields like item names, quantities, categories).


# Safety, Hallucination Checks & Fallbacks

AI hallucinations or unsafe suggestions must be guarded against. Build multi-layer checks:

Guard in Prompts: As a first step, instruct the model not to invent items. E.g. “If unsure, return an empty list or say you don’t know”. Use system rules like “Answer only based on input data.” Maintain a very low temperature for safety.

Ground with Facts (RAG): Don’t rely on the model’s memory. Instead retrieve related info (e.g. from gear manuals or a knowledge base) and include it in the prompt. Retrieval-augmented generation (RAG) ensures responses are based on provided facts. For example, embed relevant gear specs or survival guidelines so the model “answers from these specific facts”.

Output Validation: After receiving AI output, automatically verify it. For example, check that recommended item names exist in your gear database. Use business rules (e.g. weight limits, duplications). Parasoft suggests “automated verification” – e.g. a lightweight “judge” model or simple code that assigns confidence or flags inconsistencies. If checks fail, you can retry, switch prompts, or warn the user.

Error Handling: Wrap all LLM calls with try/except. On API errors or timeouts, log the issue and retry (using exponential backoff) or switch to a backup model/provider via OpenRouter. For example, annotate calls with @retry to recover from transient failures. Have an alternate path: if one model fails, route the request to another model with similar capability (OpenRouter supports “routing across providers”).

Fallback Responses: If AI fails or output is invalid, return a safe default (e.g. an empty recommendation list with a warning) rather than crashing. In critical cases, flag for human review. The Parasoft guide even suggests human-in-the-loop checks if errors are costly. For most gear recommendations, an incomplete answer is likely preferable to a hallucination, so handle it gracefully (e.g. “Unable to generate recommendations at this time”).


# Data Handling, Privacy & Logging

Treat all user/trip data carefully. Ensure compliance (GDPR, CCPA) and avoid leaking PII:

Minimal Data to LLM: Don’t send more user data than needed. Strip obvious PII (names, contact info) from prompts. Use privacy filters or token-level redaction before LLM calls, as recommended by privacy best practices. For example, mask or anonymize any identifying details in user profiles.

Secure Storage & Encryption: Encrypt sensitive data at rest and in transit. Any stored prompts or responses in logs or databases should use end-to-end encryption where possible. Likewise, use secure credential storage for API keys. If using a vector DB for RAG, encrypt embeddings to prevent inversion attacks.

Logging Practices: Log enough to audit and debug, but never log raw PII or full user input unmasked. For example, log request metadata (user ID, timestamp, model used) but omit the user’s actual trip details or health info. If you must log part of the request (like a query), apply hashing or redaction. Follow FastAPI logging best practices: use structured logs (JSON) and include context IDs, but ensure sensitive fields are redacted.

Consent and Retention: Inform users (via privacy policy) how their data may be used. Don’t retain sensitive data longer than needed. If the system learns from user feedback, only store anonymized or aggregate insights.

Data Governance: Use role-based access so that only authorized components can read the full user profiles. Regularly audit logs and storage to ensure no unintentional leaks of private info.


# Performance & Scaling

Optimize LLM usage and backend performance for low latency and high throughput:

Caching: Cache AI responses for identical or similar prompts to avoid repeated API calls. For example, use an LRU cache keyed by (user_id, prompt_text) as in Kumar’s example. Log cache hit/miss rates to tune cache size (see [30]). Also consider semantic caching: for very similar queries, reuse the nearest cached response.

Asynchronous Concurrency: Call OpenRouter asynchronously so multiple users or parallel tasks can be served. FastAPI’s async support lets you await the LLM call, and you can run many in parallel (bounded by rate limits). If on a multi-core server, use asyncio or thread pools to maximize throughput.

Rate Limiting: Throttle incoming requests per user or IP to avoid API quota spikes and to protect backend resources. In [30], they limit chat to “10 requests per minute per IP”. Use FastAPI middleware or libraries (like slowapi) to enforce rate limits.

Serverless/Auto-Scaling: Deploy on platforms that auto-scale (Azure Functions, AWS Lambda, Kubernetes auto-scaling) so the system can handle bursts of traffic. This also helps manage cost during low-traffic periods.

Model/Provider Failover: Use OpenRouter’s multi-model capability. For example, if GPT-4o hits rate limit or latency spikes, route the call to Claude 3.5 or Gemini Flash transparently. Implement logic to switch providers on the fly (e.g. try-primary, else try-secondary).

Versioning: Keep track of LLM versions and prompt versions. Tag each request with the model name and version used. When upgrading models (e.g. moving from GPT-4 to GPT-4o), use A/B testing on a small user subset to compare outputs. Version your prompt templates too, so you can roll back if a new prompt yields poorer results.

Monitoring: Instrument latency and error metrics. Monitor LLM response times and tail latencies. Cache monitoring (hit rates) is critical, as Kumar’s example logs hits vs misses. Use these metrics to scale and optimize (e.g. increase cache if misses are high, or scale up concurrency if latencies grow).


# External Data Integration

Leverage domain data and knowledge sources to improve recommendations:

Gear Inventory Database: Keep a structured database (SQL/NoSQL) of all gear items, categories, weights, ratings, etc. Access it via a repository interface. Use this DB to validate or enrich AI output (e.g. only recommend items that exist and match constraints). The LLM prompt can reference some DB facts (e.g. “the following gear is already owned”).

Retrieval-Augmented Context (Embeddings): Build or use an embedding store (Pinecone, Weaviate, Redis, etc.) of relevant documents (e.g. user manuals, survival guides, past trip logs). When a recommendation is needed, retrieve top-k context paragraphs (based on user query/context) and include them in the prompt. This RAG approach “grounds” answers in real data. For example, retrieve technical specs for gear to ensure recommendations are factual.

Knowledge Graph/Ontologies: Optionally, construct a knowledge graph of gear relationships (e.g. “Tent” –[requires]→ “Tarp”; “Cold Climate” –[implies]→ “Insulated Sleeping Bag”). You can then query this graph to enforce logical consistency. Integrating with the LLM: either include the relevant slice of the KG in the prompt, or call the LLM to generate Cypher/GraphQL queries (like Neo4j’s GraphRAG) to fetch facts. Knowledge graphs can help infer non-obvious suggestions (e.g. if hiking in “tundra” add “microspikes”).

User Uploads: If users can upload additional data (e.g. a map image or text itinerary), preprocess it accordingly. Use OCR/vision models for images (e.g. extract altitude text from map) and convert to text; then feed that info into the AI prompt or embedding retrieval. For documents, parse and index them in your RAG pipeline. For example, a user’s training stats CSV could be parsed, summarized, and used to tailor gear fitness recommendations. Always sanitize uploads for security before processing.

APIs and External Services: Integrate third-party APIs as needed (e.g. a weather API for climate data, or a terrain classification API). These can be part of the prompt context or used in pre-/post-processing. For example, fetch expected temperature profile and feed it to the LLM.


# Quality Evaluation & Feedback Loops

Continuously measure and improve AI output quality:

Prompt/Response Logging: Log every prompt and model response (in a sanitized form) with metadata (timestamp, user ID hash, model version). This audit trail allows manual review of failures. It also provides data for training or finetuning. For JSON outputs, log both raw JSON and any parsing errors.

Automated Testing: Build tests for typical scenarios. For instance, craft sample trip inputs and check that the JSON output contains required fields and plausible values. Automated validators can raise flags (and alert developers) if outputs deviate (e.g. missing fields or unreasonable items).

Evaluation Metrics: Define metrics like valid JSON rate, schema adherence rate, and accuracy (if some ground truth exists). Track these over time. For recommendation tasks, you might use proxy metrics (e.g. user click-through or satisfaction).

A/B Testing: When adjusting prompts or switching models, do controlled A/B tests with real or synthetic traffic. Compare outputs for the same query across versions to spot improvements or regressions.

User Feedback: Provide a way for end-users or administrators to flag bad recommendations. This can feed back into the system: update the prompt instructions, add corner cases to test suite, or even finetune a custom model. Even a simple “Thumbs up/down” on suggestions yields valuable data.

Version Control: Store prompt templates and system messages in source control (e.g. Git). Document why changes are made. Use tools (like weightless.ai, or prompt engineering platforms) to track prompt versions and testing results.


# Open-Source Examples

Several public projects demonstrate JSON-based AI/FastAPI integrations:

- Azure OpenAI FastAPI Chat: Microsoft’s openai-chat-backend-fastapi is a sample FastAPI backend that streams Azure OpenAI (GPT) responses. It uses Docker and Azure Container Apps, and shows how to accept JSON chat requests and stream back JSONL responses for a chat UI.

- Assistant API Streaming: The xbreid/fastapi-assistant-streaming repo (from a Medium tutorial) integrates FastAPI with OpenAI’s new Assistant API using SSE streaming. It handles JSON chat payloads, conversation threads, and streaming. This is a good model for asynchronous JSON exchanges.

- Simple FastAPI/OpenAI Example: The simple-openai-fastapi-server repo by thomassuedbroecker provides endpoints that accept JSON (text input, file upload, or context+question) and return the model’s JSON response. It illustrates using security (Basic Auth) and integrating file uploads with LLMs.

- Neo4j GraphRAG: Neo4j’s Knowledge Graph Builder (LLMGraphBuilder) is a FastAPI-based back end that combines LangChain with a Neo4j graph to extract information from documents and serve it via a GraphRAG interface. Although focused on document-to-graph, it exemplifies an AI+FastAPI service with JSON APIs (loading documents, querying graphs).


These examples all use JSON payloads and demonstrate structuring endpoints around LLM calls, with best practices like stream handling, dependency injection, and typed Pydantic models.


# Proposed AI Integration Architecture

Below is a high-level sketch of the FastAPI modules and flow:

- API Layer (FastAPI endpoints): Defines routes (e.g. POST /recommend) that accept JSON input (trip details, user profile). Uses Pydantic for input validation. Each route injects dependencies like AIService, GearRepository, CacheLayer, and an Auth guard.

- PromptFactory Module: Takes domain objects (trip context, inventory list, user profile) and constructs the final LLM prompt (system+user messages). Encapsulates prompt templates and formatting logic.

- AIService Module: Encapsulates all interaction with OpenRouter/LLMs. Methods like generate_recommendations(prompt) call the OpenRouter API, handle retries/backoff, and return raw JSON or text. Internally, it sets parameters (model name, temperature, JSON mode) and applies rate-limits. The service uses an asynchronous HTTP client.

- ResponseParser/Validator: After AIService returns data, this component parses the response into a structured form (e.g. a Pydantic model matching the expected schema). It checks JSON validity and required fields. If validation fails, it triggers fallback logic (e.g. try reformatting or a simpler prompt).

- CacheLayer: A simple cache (e.g. LRU cache or Redis) keyed on prompt hash or a request signature. Before calling AIService, check cache. After a successful parse, store the result. This reduces latency/cost for repeat queries.

- Embedding/RAG Module: Handles retrieval from the embedding store. Given the trip context or question, it queries a vector DB to fetch relevant text passages. Those are fed into PromptFactory to enrich the prompt. This module also manages vector store indexing/updating.

- GearRepository: Abstraction over the gear inventory database. Provides methods like get_equipment_by_category(), list_all_gear(), etc. Used to validate or augment LLM suggestions (e.g. filtering nonexistent items).

- RecommendationEngine (Business Logic): Applies domain rules and combines AI output with data. For instance, it might merge LLM-suggested items with user’s existing inventory, enforce weight limits, or score items. This keeps critical logic in code, not LLM.

- Logger & Metrics: Cross-cutting services that log each request/response (with sanitized data) and expose metrics (latency, error rates). Integrate with monitoring tools (Prometheus, Grafana, etc.).

- Security/Config: Modules for API key or JWT verification on endpoints, and config management (e.g. loading OpenRouter API keys, model names, and prompt templates from secure config).


In summary, the system flow is: Request → PromptFactory → (Cache?) → RAG retrieval → Enhanced Prompt → AIService → ResponseParser → RecommendationEngine → Response. Key modules like PromptFactory, AIService, CacheLayer, and Validator each handle one concern, yielding a clean, testable architecture.
