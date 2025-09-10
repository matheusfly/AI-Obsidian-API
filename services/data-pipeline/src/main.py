"""
Main Data Pipeline Service - Standalone Obsidian Vault Processing with Gemini Integration
"""
import asyncio
import logging
import time
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn

from config import get_settings
# from ingestion.obsidian_client import ObsidianAPIClient, ObsidianVaultScanner  # Commented out - using local vector DB only
from processing.content_processor import ContentProcessor, BatchContentProcessor
from embeddings.embedding_service import EmbeddingService
from vector.chroma_service import ChromaService
from search.search_service import SemanticSearchService
from llm.gemini_client import GeminiClient

# Import observability modules
from monitoring.telemetry_simple import setup_telemetry, get_metrics_collector, cleanup_telemetry
from monitoring.health import router as health_router
from monitoring.chromadb_metrics import ChromaDBMetrics
# from monitoring.metrics import get_metrics, setup_opentelemetry_metrics  # Removed to avoid duplicate metrics
# from monitoring.standard_metrics import get_standard_metrics, MetricsMiddleware  # Removed to avoid duplicate metrics
from monitoring.comprehensive_metrics import get_comprehensive_metrics
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# OpenTelemetry imports for LangSmith integration
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# --- OpenTelemetry Setup for LangSmith Integration ---
def setup_opentelemetry():
    """Setup OpenTelemetry tracing for LangSmith integration"""
    try:
        # Create a Tracer Provider
        tracer_provider = TracerProvider()
        
        # Create an OTLP Exporter (sends to your collector)
        otlp_exporter = OTLPSpanExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
            insecure=True,  # Set to False if using TLS in production
        )
        
        # Add the exporter to the provider with a batch processor
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        
        # Set the global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        logger.info("OpenTelemetry tracing setup complete for LangSmith integration")
        return tracer_provider
        
    except Exception as e:
        logger.error(f"Failed to setup OpenTelemetry: {e}")
        return None

# Setup OpenTelemetry before creating FastAPI app
tracer_provider = setup_opentelemetry()

# Setup observability
def setup_observability():
    """Setup observability stack"""
    try:
        # Setup OpenTelemetry
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        environment = os.getenv("OTEL_SERVICE_NAME", "data-pipeline")
        setup_telemetry(
            service_name=environment,
            otlp_endpoint=otlp_endpoint,
            environment="local"
        )
        
        logger.info("Observability stack setup complete")
        
    except Exception as e:
        logger.error(f"Failed to setup observability: {e}")
        # Don't fail the service if observability setup fails
        pass

# Initialize observability
setup_observability()

# Initialize FastAPI app
app = FastAPI(
    title="Data Pipeline Service",
    description="Standalone Obsidian Vault Processing with Gemini Integration",
    version=settings.service_version
)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# --- Instrument FastAPI app for OpenTelemetry tracing ---
# This will automatically create spans for all incoming HTTP requests
# and send them to the OTLP Collector for LangSmith integration
if tracer_provider:
    FastAPIInstrumentor.instrument_app(app)
    logger.info("FastAPI app instrumented for OpenTelemetry tracing")

# Include health monitoring router
app.include_router(health_router)

# Global service instances
# obsidian_client: Optional[ObsidianAPIClient] = None  # Commented out - using local vector DB only
content_processor: Optional[ContentProcessor] = None
embedding_service: Optional[EmbeddingService] = None
# async_embedding_service: Optional[AsyncEmbeddingService] = None  # Commented out - using synchronous EmbeddingService only
chroma_service: Optional[ChromaService] = None
search_service: Optional[SemanticSearchService] = None
gemini_client: Optional[GeminiClient] = None
chromadb_metrics: Optional[ChromaDBMetrics] = None


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    max_results: int = 5
    search_type: str = "semantic"  # semantic, keyword, hybrid, tag
    filters: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    processing_time: float
    search_results: List[Dict[str, Any]]
    context_length: int

class IndexRequest(BaseModel):
    force_reindex: bool = False
    chunking_strategy: str = "headings"  # headings, size, sentences
    batch_size: int = 100

class IndexResponse(BaseModel):
    total_files: int
    processed_files: int
    total_chunks: int
    processing_time: float
    errors: List[str]

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    stats: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global content_processor, embedding_service  # obsidian_client and async_embedding_service commented out
    global chroma_service, search_service, gemini_client
    
    try:
        logger.info("Initializing Data Pipeline Service...")
        
        # Initialize Obsidian client - COMMENTED OUT (using local vector DB only)
        # obsidian_client = ObsidianAPIClient(
        #     api_key=settings.obsidian_api_key,
        #     host=settings.obsidian_host,
        #     port=settings.obsidian_port
        # )
        
        # Test connection (with graceful handling) - COMMENTED OUT
        # try:
        #     if not await obsidian_client.test_connection():
        #         logger.warning("Obsidian API not available - service will run in offline mode")
        #         logger.info("Note: Obsidian Local REST API plugin must be running for indexing")
        # except Exception as e:
        #     logger.warning(f"Obsidian API connection failed: {e}")
        #     logger.info("Service will run in offline mode - Obsidian API required for indexing")
        
        logger.info("Obsidian API disabled - using local vector database only")
        
        # Initialize content processor
        content_processor = ContentProcessor(
            max_chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        # Initialize embedding service
        embedding_service = EmbeddingService(
            model_name=settings.embedding_model
        )
        
        # async_embedding_service = AsyncEmbeddingService(embedding_service)  # Commented out - using synchronous EmbeddingService only
        
        # Initialize ChromaDB service
        chroma_service = ChromaService(
            collection_name=settings.chroma_collection_name,
            persist_directory=settings.chroma_persist_directory
        )
        
        # Initialize search service
        search_service = SemanticSearchService(chroma_service, embedding_service)
        
        # Initialize Gemini client
        gemini_client = GeminiClient(
            api_key=settings.gemini_api_key,
            model_name="gemini-pro"
        )
        
        # Initialize ChromaDB metrics
        global chromadb_metrics
        chromadb_metrics = ChromaDBMetrics(chroma_service)
        
        # Initialize enhanced metrics
        enhanced_metrics = get_metrics()
        
        # Setup OpenTelemetry metrics for LangSmith integration
        otlp_metrics_provider = setup_opentelemetry_metrics()
        
        logger.info("Data Pipeline Service initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # global async_embedding_service  # Commented out - using synchronous EmbeddingService only
    
    try:
        # Ensure all OpenTelemetry spans are exported on shutdown
        if tracer_provider:
            tracer_provider.shutdown()
            logger.info("OpenTelemetry tracer provider shut down")
        
        # if obsidian_client:  # Commented out - using local vector DB only
        #     await obsidian_client.close()
        
        # if async_embedding_service:  # Commented out - using synchronous EmbeddingService only
        #     async_embedding_service.close()
        
        logger.info("Data Pipeline Service shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint with comprehensive observability"""
    try:
        # Get comprehensive metrics (includes ALL observability metrics)
        comprehensive_metrics = get_comprehensive_metrics()
        comprehensive_data = comprehensive_metrics.get_metrics()
        
        # Note: Enhanced metrics removed to avoid duplicate metric names
        # The comprehensive metrics system includes all necessary metrics
        
        # Use only comprehensive metrics to avoid timestamp conflicts
        all_metrics = comprehensive_data
        
        return Response(content=all_metrics, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return Response(content="", media_type=CONTENT_TYPE_LATEST)

@app.get("/chromadb/health")
async def chromadb_health():
    """ChromaDB-specific health check"""
    try:
        if not chromadb_metrics:
            return {"status": "unhealthy", "error": "ChromaDB metrics not initialized"}
        
        health_status = chromadb_metrics.get_health_status()
        return health_status
    except Exception as e:
        logger.error(f"Error checking ChromaDB health: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        services_status = {}
        
        # Check Obsidian connection - COMMENTED OUT (using local vector DB only)
        # if obsidian_client:
        #     services_status["obsidian"] = "connected" if await obsidian_client.test_connection() else "disconnected"
        # else:
        #     services_status["obsidian"] = "not_initialized"
        services_status["obsidian"] = "disabled"  # Using local vector DB only
        
        # Check other services
        services_status["content_processor"] = "ready" if content_processor else "not_initialized"
        services_status["embedding_service"] = "ready" if embedding_service else "not_initialized"
        services_status["chroma_service"] = "ready" if chroma_service else "not_initialized"
        services_status["search_service"] = "ready" if search_service else "not_initialized"
        services_status["gemini_client"] = "ready" if gemini_client else "not_initialized"
        
        # Get stats
        stats = {}
        if chroma_service:
            stats["chroma_stats"] = chroma_service.get_collection_stats()
        
        if embedding_service:
            stats["embedding_stats"] = embedding_service.get_cache_stats()
        
        if search_service:
            stats["search_stats"] = search_service.get_search_stats()
        
        # Determine overall status
        overall_status = "healthy" if all(
            status in ["connected", "ready"] for status in services_status.values()
        ) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            services=services_status,
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_vault(request: QueryRequest):
    """Query the Obsidian vault using semantic search + Gemini"""
    try:
        # Get comprehensive metrics instance
        comprehensive_metrics = get_comprehensive_metrics()
        
        # Record search query
        comprehensive_metrics.search_queries_total.inc()
        
        start_time = time.time()
        
        # Perform search based on type
        if request.search_type == "semantic":
            search_results = search_service.search_similar(
                request.query, 
                request.max_results, 
                request.filters
            )
        elif request.search_type == "keyword":
            keywords = request.query.split()
            search_results = search_service.search_by_keywords(
                keywords, 
                request.max_results, 
                request.filters
            )
        elif request.search_type == "hybrid":
            search_results = search_service.hybrid_search(
                request.query, 
                request.max_results, 
                filters=request.filters
            )
        elif request.search_type == "tag":
            tags = [tag.strip('#') for tag in request.query.split() if tag.startswith('#')]
            search_results = search_service.search_by_tags(tags, request.max_results)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown search type: {request.search_type}")
        
        # Record search latency
        search_latency = time.time() - start_time
        comprehensive_metrics.search_latency_seconds.observe(search_latency)
        
        # Record ChromaDB operations
        comprehensive_metrics.record_chromadb_operation("query", "documents", search_latency, True)
        
        # Process with Gemini
        llm_start_time = time.time()
        gemini_result = await gemini_client.process_content(request.query, search_results)
        llm_latency = time.time() - llm_start_time
        
        # Record LLM metrics
        comprehensive_metrics.record_llm_request("google", "gemini-pro", llm_latency, 100, 50, 0.05)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            answer=gemini_result["answer"],
            sources=gemini_result["sources"],
            processing_time=processing_time,
            search_results=search_results,
            context_length=gemini_result["context_length"]
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/index", response_model=IndexResponse)  # COMMENTED OUT - Obsidian API disabled
# async def index_vault(request: IndexRequest, background_tasks: BackgroundTasks):
#     """Index the entire Obsidian vault"""
#     try:
#         start_time = time.time()
#         
#         # Start indexing in background
#         background_tasks.add_task(
#             _index_vault_background,
#             request.force_reindex,
#             request.chunking_strategy,
#             request.batch_size
#         )
#         
#         return IndexResponse(
#             total_files=0,  # Will be updated by background task
#             processed_files=0,
#             total_chunks=0,
#             processing_time=0,
#             errors=[]
#         )
#         
#     except Exception as e:
#         logger.error(f"Error starting indexing: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/index", response_model=IndexResponse)
async def index_vault_disabled(request: IndexRequest, background_tasks: BackgroundTasks):
    """Vault indexing is disabled - using local vector database only"""
    # Get comprehensive metrics instance
    comprehensive_metrics = get_comprehensive_metrics()
    
    # Record file processing attempt (even though disabled)
    comprehensive_metrics.files_processed_total.inc()
    
    return IndexResponse(
        total_files=0,
        processed_files=0,
        total_chunks=0,
        processing_time=0,
        errors=["Vault indexing is disabled - using local vector database only"]
    )


async def _index_vault_background(force_reindex: bool, chunking_strategy: str, batch_size: int):
    """Background task for indexing vault"""
    try:
        logger.info("Starting vault indexing...")
        
        # Get vault files
        vault_scanner = ObsidianVaultScanner(obsidian_client)
        scan_summary = await vault_scanner.scan_vault()
        
        # Process files in batches
        batch_processor = BatchContentProcessor(content_processor, batch_size)
        
        total_files = len(scan_summary["files"])
        processed_files = 0
        total_chunks = 0
        errors = []
        
        for i in range(0, total_files, batch_size):
            batch_files = scan_summary["files"][i:i + batch_size]
            
            # Get file contents
            file_paths = [f["path"] for f in batch_files]
            file_contents = await obsidian_client.batch_get_files(file_paths)
            
            # Process content
            processing_results = await batch_processor.process_files_batch(
                file_contents, chunking_strategy
            )
            
            # Generate embeddings
            all_chunks = []
            for result in processing_results:
                if "chunks" in result:
                    all_chunks.extend(result["chunks"])
            
            if all_chunks:
                chunk_texts = [chunk["content"] for chunk in all_chunks]
                embeddings = embedding_service.batch_generate_embeddings(chunk_texts)
                
                # Store in ChromaDB
                chroma_service.store_chunks(all_chunks, embeddings)
                total_chunks += len(all_chunks)
            
            processed_files += len(processing_results)
            
            # Log progress
            logger.info(f"Processed {processed_files}/{total_files} files, {total_chunks} chunks")
        
        processing_time = time.time() - start_time
        logger.info(f"Vault indexing completed in {processing_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Error in background indexing: {e}")


@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    try:
        stats = {}
        
        if chroma_service:
            stats["chroma"] = chroma_service.get_collection_stats()
        
        if embedding_service:
            stats["embeddings"] = embedding_service.get_cache_stats()
        
        if search_service:
            stats["search"] = search_service.get_search_stats()
        
        # if obsidian_client:  # Commented out - using local vector DB only
        #     vault_stats = await obsidian_client.get_vault_stats()
        #     stats["vault"] = vault_stats
        stats["vault"] = {"status": "disabled", "message": "Using local vector database only"}
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search_vault(request: QueryRequest):
    """Search vault without Gemini processing"""
    try:
        # Get comprehensive metrics instance
        comprehensive_metrics = get_comprehensive_metrics()
        
        # Record search query
        comprehensive_metrics.search_queries_total.inc()
        
        start_time = time.time()
        
        if request.search_type == "semantic":
            results = search_service.search_similar(
                request.query, 
                request.max_results, 
                request.filters
            )
        elif request.search_type == "keyword":
            keywords = request.query.split()
            results = search_service.search_by_keywords(
                keywords, 
                request.max_results, 
                request.filters
            )
        elif request.search_type == "hybrid":
            results = search_service.hybrid_search(
                request.query, 
                request.max_results, 
                filters=request.filters
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown search type: {request.search_type}")
        
        # Record search latency
        search_latency = time.time() - start_time
        comprehensive_metrics.search_latency_seconds.observe(search_latency)
        
        # Record ChromaDB operations (simulated)
        comprehensive_metrics.record_chromadb_operation("query", "documents", search_latency, True)
        
        return {"results": results, "total": len(results)}
        
    except Exception as e:
        logger.error(f"Error searching vault: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
