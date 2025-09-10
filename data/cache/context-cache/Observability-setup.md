
 
 Our goal is a **simple, functional, reliable, and ready-to-deploy observability stack** that gives you immediate visibility into your **ChromaDB vector database** and the **data pipeline serving your LangGraph agents**. This is your "Starter Kit" for observability.

We will use the **absolute minimum viable set of tools** to achieve this, focusing on **metrics** (for database health and performance) and **tracing** (for request flows, which will integrate with LangSmith). 
The core philosophy is: **Start Small, Ship Fast, Iterate Later.**

---
### **🚀 Observability Starter Kit: Roadmap**
This roadmap is divided into two phases: **Phase 0 (Foundation)** and **Phase 1 (Core Observability)**. Phase 0 gets you a working dashboard. Phase 1 adds the critical instrumentation for your database and pipeline.

---
### **Phase 0: Foundation - The "Hello World" of Observability (1 Day)**
Goal: Get Grafana, Prometheus, and a basic OpenTelemetry Collector running with Docker. Verify you can see *something*.

#### **Step 0.1: Define Your `docker-compose.yml`**

This is the heart of your starter kit. It defines the minimal services.

```yaml
# docker-compose.yml
version: '3.8'

services:
  # --- Observability Stack ---
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.95.0
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./config/otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317" # OTLP gRPC (for traces and metrics from your app)
      - "4318:4318" # OTLP HTTP (alternative)
    depends_on:
      - prometheus

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus # Persist metrics data
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:10.2.2
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your_secure_password_here # CHANGE THIS
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana # Persist dashboards
    depends_on:
      - prometheus

  # --- Your Existing Data Pipeline Service ---
  data-pipeline:
    build: ./services/data-pipeline # Path to your existing service's Dockerfile
    volumes:
      - ./vault:/app/vault # Mount your Obsidian vault
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      # OpenTelemetry Configuration for Auto-Instrumentation
      - OTEL_SERVICE_NAME=data-pipeline
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
      - OTEL_EXPORTER_OTLP_PROTOCOL=grpc
      - OTEL_METRICS_EXPORTER=none # We'll do manual metrics for now to keep it simple
      - OTEL_LOGS_EXPORTER=none    # We'll skip logs for the starter kit
    depends_on:
      - otel-collector

volumes:
  prometheus_data:
  grafana_data:
```

#### **Step 0.2: Create Configuration Files**

Create a `./config/` directory and add these two files.

*   **File: `./config/otel-collector-config.yaml`**
    This configures the collector to receive data and send it to Prometheus.
    ```yaml
    receivers:
      otlp:
        protocols:
          grpc:
          http:

    processors:
      batch: # Batches data to reduce network calls
        timeout: 10s
        send_batch_size: 1024

    exporters:
      prometheus:
        endpoint: "0.0.0.0:8889" # The collector will expose a /metrics endpoint on this port
        namespace: obsidian_pipeline
        const_labels:
          environment: local

    service:
      pipelines:
        metrics: # We are only setting up metrics for now
          receivers: [otlp]
          processors: [batch]
          exporters: [prometheus]
    ```

*   **File: `./config/prometheus.yml`**
    This tells Prometheus where to scrape metrics from (the OpenTelemetry Collector).
    ```yaml
    global:
      scrape_interval: 15s # How often to scrape targets

    scrape_configs:
      - job_name: 'otel-collector'
        static_configs:
          - targets: ['otel-collector:8889'] # Scrape the collector's /metrics endpoint
        metric_relabel_configs:
          # Optional: Clean up metric names if needed
          - source_labels: [__name__]
            regex: 'obsidian_pipeline_(.*)'
            target_label: __name__
            replacement: '$1'
    ```

#### **Step 0.3: Deploy and Verify**

1.  **Start the Stack:**
    ```bash
    docker-compose up -d
    ```

2.  **Verify Services:**
    *   Go to `http://localhost:9090/targets`. You should see the `otel-collector` target as **UP**.
    *   Go to `http://localhost:3000`. Log in with `admin` and your `your_secure_password_here`.
    *   In Grafana, go to `Configuration` > `Data Sources` > `Add data source`.
    *   Select **Prometheus**.
    *   Set the URL to `http://prometheus:9090`.
    *   Click "Save & Test". It should say "Data source is working".

3.  **Create Your First Dashboard:**
    *   In Grafana, click `Create` > `Dashboard`.
    *   Click `Add new panel`.
    *   In the "Metrics" browser, type `up`. You should see a metric like `up{job="otel-collector"}`.
    *   Set the visualization to "Stat".
    *   Click the panel title, edit, and set the name to "Collector Status".
    *   A value of `1` means it's up.
    *   Click "Save dashboard" and give it a name like "Starter Kit".

**Congratulations!** You have a working observability foundation. You can see if your collector is alive. Now, let's make it useful.

---
- We will defer complex logging (Loki) and advanced alerting for now.
### **Phase 1: Core Observability - Instrument Your Database & Pipeline (2-3 Days)**

Goal: Instrument your `data-pipeline` service to emit metrics about ChromaDB and track requests with traces (for LangSmith).

#### **Step 1.1: Add OpenTelemetry Dependencies to Your Data Pipeline**

Update your `services/data-pipeline/requirements.txt` to include:

```txt
opentelemetry-api==1.24.0
opentelemetry-sdk==1.24.0
opentelemetry-exporter-otlp==1.24.0
opentelemetry-instrumentation-fastapi==0.45b0
opentelemetry-instrumentation==0.45b0
```

#### **Step 1.2: Instrument Your FastAPI App for Tracing (LangSmith Integration)**

Modify your `services/data-pipeline/src/main.py` to add tracing. This is crucial for LangSmith.

```python
# services/data-pipeline/src/main.py
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import os

# --- STEP 1: Set up OpenTelemetry Tracing ---
# This will automatically create spans for your FastAPI endpoints
# and send them to the OTLP Collector, which LangSmith can ingest.

# Create a Tracer Provider
tracer_provider = TracerProvider()

# Create an OTLP Exporter (sends to your collector)
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
    insecure=True, # Set to False if using TLS
)

# Add the exporter to the provider
tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# Set the global tracer provider
trace.set_tracer_provider(tracer_provider)

# Initialize FastAPI app
app = FastAPI(title="Obsidian Vault Data Pipeline Service")

# --- STEP 2: Instrument the FastAPI app ---
# This will automatically create spans for all incoming HTTP requests.
FastAPIInstrumentor.instrument_app(app)

# ... [rest of your existing code: routes, dependencies, etc.] ...

@app.on_event("shutdown")
async def shutdown_event():
    # Ensure all spans are exported on shutdown
    tracer_provider.shutdown()
```

*   **Why this matters for LangSmith:** LangSmith can ingest OpenTelemetry traces. By setting this up, every `/query` request to your FastAPI app will generate a trace. When you later integrate LangGraph agents, their steps will be part of this trace, giving you end-to-end visibility in LangSmith.

#### **Step 1.3: Add Custom Metrics for ChromaDB**

This is the core of your "database observability." You need to track its size and query performance.

*   **File: `services/data-pipeline/src/monitoring/metrics.py`**
    ```python
    # services/data-pipeline/src/monitoring/metrics.py
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    from opentelemetry import metrics
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    import os

    # --- Option A: Use Prometheus Client Library (Simpler for Starter Kit) ---
    # We'll use this for now as it's straightforward.

    # Define Metrics
    CHROMA_COLLECTION_SIZE = Gauge(
        'chroma_collection_size',
        'Number of items (chunks) in the ChromaDB collection'
    )

    CHROMA_QUERY_LATENCY = Histogram(
        'chroma_query_latency_seconds',
        'Latency of ChromaDB queries in seconds',
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0] # Define buckets for your expected latency
    )

    CHROMA_QUERY_ERRORS = Counter(
        'chroma_query_errors_total',
        'Total number of errors during ChromaDB queries'
    )

    SEARCH_REQUESTS = Counter(
        'search_requests_total',
        'Total number of search requests received',
        ['endpoint'] # You can add labels like endpoint="/query"
    )

    SEARCH_LATENCY = Histogram(
        'search_latency_seconds',
        'Total latency of the search request (including ChromaDB and LLM)',
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
    )

    # Start a Prometheus metrics server on port 8001
    # This allows Prometheus to scrape these custom metrics directly from your app.
    start_http_server(8001)
    ```

*   **Update `services/data-pipeline/src/vector/chroma_service.py` to use these metrics:**
    ```python
    # At the top of chroma_service.py
    from ..monitoring.metrics import CHROMA_COLLECTION_SIZE, CHROMA_QUERY_LATENCY, CHROMA_QUERY_ERRORS

    class ChromaService:
        # ... [existing code] ...

        def get_collection_stats(self) -> int:
            """Get the current size of the collection and update the metric."""
            count = self.collection.count()
            CHROMA_COLLECTION_SIZE.set(count) # Update the Gauge
            return count

        def search_with_metrics(self, query_embedding: List[float], n_results: int = 5) -> Dict:
            """Wrapper around collection.query that records metrics."""
            start_time = time.time()
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                latency = time.time() - start_time
                CHROMA_QUERY_LATENCY.observe(latency)
                return results
            except Exception as e:
                CHROMA_QUERY_ERRORS.inc()
                raise e
    ```

*   **Update `services/data-pipeline/src/search/search_service.py`:**
    ```python
    # At the top
    from ..monitoring.metrics import SEARCH_REQUESTS, SEARCH_LATENCY

    class SemanticSearchService:
        def search_similar(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
            # Record that a search request was made
            SEARCH_REQUESTS.labels(endpoint="/search").inc()

            start_time = time.time()
            try:
                query_embedding = self.embedding_service.generate_embedding(query)
                # Use the instrumented ChromaDB method
                results = self.chroma_service.search_with_metrics(query_embedding, n_results)

                # ... [format results as before] ...
                return formatted_results

            finally:
                # Record the total search latency (embedding + chroma)
                total_latency = time.time() - start_time
                SEARCH_LATENCY.observe(total_latency)
    ```

*   **Update `services/data-pipeline/src/main.py` to expose the Prometheus endpoint to Prometheus:**
    Add this to your `docker-compose.yml` under the `data-pipeline` service:
    ```yaml
    ports:
      - "8000:8000" # Your FastAPI app
      - "8001:8001" # Expose the Prometheus metrics endpoint
    ```

    And update your `./config/prometheus.yml` to scrape your app directly:
    ```yaml
    scrape_configs:
      # ... [existing otel-collector config] ...
      - job_name: 'data-pipeline'
        static_configs:
          - targets: ['data-pipeline:8001'] # Scrape the /metrics endpoint on port 8001
    ```

#### **Step 1.4: Create Your Core Grafana Dashboard**

Now, create a dashboard in Grafana that shows your most critical metrics.

*   Go to `http://localhost:3000`.
*   Create a new dashboard.
*   Add panels with these PromQL queries:

    *   **Panel 1: ChromaDB Collection Size (Stat)**
        *   **Query:** `chroma_collection_size`
        *   **Visualization:** Stat
        *   **Title:** "Total Chunks in DB"

    *   **Panel 2: ChromaDB Query Latency (Graph)**
        *   **Query:** `histogram_quantile(0.95, rate(chroma_query_latency_seconds_bucket[5m]))`
        *   **Visualization:** Graph
        *   **Title:** "ChromaDB P95 Latency (Last 5m)"

    *   **Panel 3: Search Request Rate (Graph)**
        *   **Query:** `rate(search_requests_total[5m])`
        *   **Visualization:** Graph
        *   **Title:** "Search Requests per Second"

    *   **Panel 4: Total Search Latency (Stat)**
        *   **Query:** `histogram_quantile(0.90, rate(search_latency_seconds_bucket[5m]))`
        *   **Visualization:** Stat
        *   **Title:** "Search P90 Latency"

    *   **Panel 5: Error Rate (Stat)**
        *   **Query:** `rate(chroma_query_errors_total[5m])`
        *   **Visualization:** Stat
        *   **Title:** "ChromaDB Errors/sec"

Save this dashboard as **"Obsidian Vault - Core Metrics"**.

---

### **✅ Phase 1 Complete: Your Starter Kit is Ready**

You now have:

1.  **A Centralized Dashboard (Grafana):** Showing the health and performance of your ChromaDB and data pipeline.
2.  **Database Observability:** You can track the size of your DB and the latency of queries.
3.  **Request Tracing:** Your FastAPI endpoints are instrumented. When you set up LangSmith, it will automatically pick up these traces, giving you visibility into how your agents interact with your pipeline.
4.  **Simple and Reliable:** You're using battle-tested, open-source tools (Prometheus, Grafana, OpenTelemetry) without the complexity of Loki or complex alerting.

---

### **📈 Future Enhancements (Post-Starter Kit)**

Once this is stable, you can gradually add:

*   **Phase 2: Add Logging (Loki):** Ship structured logs from your app to Loki and correlate them with traces in Grafana.
*   **Phase 3: Add Alerting:** Set up Alertmanager to send you Slack messages if `chroma_collection_size` drops suddenly or `chroma_query_errors_total` spikes.
*   **Phase 4: Advanced Tracing:** Add manual spans in your `ContentProcessor` or `EmbeddingService` to see where time is spent during ingestion.
*   **Phase 5: LangSmith Deep Dive:** Use the LangSmith UI to analyze the traces from your agents, seeing exactly which tools they called and how long each step took.

This starter kit gives you 80% of the value with 20% of the effort. It’s production-ready for a local, high-end PC setup and provides the perfect foundation for your AI agentic retrieval system.