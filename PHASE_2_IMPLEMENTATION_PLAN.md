# Phase 2: AI & Content Generation - Implementation Plan

## 🎯 Overview

**Phase 2 Goal**: Complete AI & Content Generation capabilities for StoryMaker v1.6

**Current Status**: ✅ Phase 1 Complete (Core APIs), ✅ Groq 70B Integration Working
**Target**: Full AI-powered content generation with proper architecture separation

## 🏗️ Architecture (Single-Source Alignment)

**Creative Generation (prose/dialogue/rewrites)**: Groq 70B only
**Everything Else (planning, QA/structure, embeddings, reranking)**: LM Studio + Cursor (local)
**Hugging Face**: Not used

## 📋 Phase 2 Breakdown (1-2 Hours)

### **2.1 LM Studio Integration (30 minutes)**

#### **2.1.1 LM Studio Client Implementation**
- [ ] **Basic LM Studio Client**
  - Connect to LM Studio API (port 1234)
  - Implement health checking
  - Add model listing and selection
  - Create fallback mechanisms

#### **2.1.2 Embedding & Reranking System**
- [ ] **Qwen 1024-dim Embeddings**
  - Generate embeddings for all content
  - Implement semantic search
  - Create content similarity matching
  - Build recommendation engine

- [ ] **Chat-based Reranking**
  - Implement content quality scoring
  - Add relevance ranking
  - Create user preference weighting
  - Build personalized recommendations

### **2.2 Groq Integration Cleanup (15 minutes)**

#### **2.2.1 Groq Client Simplification**
- [x] **Creative Generation Only**
  - Keep Groq strictly for creative content
  - Remove embedding/reranking methods
  - Clean up environment variables
  - Ensure single responsibility

### **2.3 Environment & Configuration (15 minutes)**

#### **2.3.1 Environment Variable Cleanup**
- [ ] **Standardize Configuration**
  - Use `GROQ_API_KEY` and `GROQ_MODEL` for Groq
  - Remove all `HF_*` references
  - Add LM Studio configuration
  - Update documentation

### **2.4 Integration Testing (30 minutes)**

#### **2.4.1 End-to-End Verification**
- [ ] **Architecture Validation**
  - Test Groq for creative generation
  - Test LM Studio for embeddings/reranking
  - Verify no cross-contamination
  - Run full test suite

## 🛠️ Technical Implementation Details

### **2.1 LM Studio Integration Architecture**

```python
# services/ai/lm_studio_client.py
class LMStudioClient:
    def __init__(self, base_url: str = "http://127.0.0.1:1234"):
        self.base_url = base_url
        self.models = {}
        self.current_model = None
        self.embedding_model = "qwen/qwen3-4b-2507"  # 1024-dim embeddings
    
    async def list_models(self) -> List[ModelInfo]:
        """List available models in LM Studio"""
        
    async def load_model(self, model_id: str) -> bool:
        """Load a specific model"""
        
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate Qwen 1024-dim embeddings for content"""
        
    async def rerank_content(self, query: str, candidates: List[str]) -> List[RankedContent]:
        """Chat-based reranking for content quality"""
        
    async def health_check(self) -> bool:
        """Check if LM Studio is running and healthy"""
```

### **2.2 Groq Integration (Creative Only)**

```python
# services/ai/groq_client.py
class GroqClient:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        # NOTE: embeddings/reranking intentionally NOT here (LM Studio owns them)
    
    async def generate_creative_content(self, prompt: str, **kwargs) -> str:
        """Generate creative content (prose/dialogue/rewrites) only"""
        
    async def health_check(self) -> bool:
        """Check if Groq API is accessible"""
```

### **2.3 Content Generation Workflows**

```python
# services/ai/content_generator.py
class ContentGenerator:
    def __init__(self, groq_client: GroqClient, lm_studio_client: LMStudioClient):
        self.groq = groq_client  # Creative generation only
        self.lm_studio = lm_studio_client  # Embeddings, reranking, planning
    
    async def generate_story_outline(self, premise: str) -> StoryOutline:
        """Generate story outline using LM Studio"""
        
    async def generate_creative_content(self, prompt: str) -> str:
        """Generate creative content using Groq 70B"""
        
    async def enhance_content(self, content: str, enhancement_type: str) -> str:
        """Enhance content using appropriate service"""
```

## 📊 Success Metrics

### **Functional Requirements**
- [ ] **LM Studio Integration**: Local models working for all content generation
- [ ] **Content Quality**: Generated content passes quality gates
- [ ] **Performance**: Content generation < 5 seconds for most tasks
- [ ] **Consistency**: Character and world consistency maintained
- [ ] **User Experience**: Seamless content creation workflow

### **Technical Requirements**
- [ ] **API Response Times**: < 200ms for content generation requests
- [ ] **Model Switching**: < 30 seconds to switch between models
- [ ] **Embedding Generation**: < 1 second for content embedding
- [ ] **Reranking**: < 500ms for content reranking
- [ ] **Error Handling**: Graceful fallbacks for all AI services

## 🚀 Implementation Timeline

### **Week 1: LM Studio Foundation**
- **Days 1-2**: LM Studio client implementation
- **Days 3-4**: Model management system
- **Days 5-7**: Basic content generation integration

### **Week 2: Enhanced LM Studio Integration**
- **Days 1-3**: Embedding and reranking system
- **Days 4-5**: Advanced content generation workflows
- **Days 6-7**: Quality control and optimization

### **Week 3: Media AI Integration**
- **Days 1-3**: Image generation enhancement
- **Days 4-5**: Multimedia content creation
- **Days 6-7**: Content synchronization

### **Week 4: Testing & Optimization**
- **Days 1-3**: Comprehensive testing
- **Days 4-5**: Performance optimization
- **Days 6-7**: Documentation and deployment

## 🔧 Development Environment Setup

### **Required Services**
```bash
# Start LM Studio
# 1. Download from https://lmstudio.ai
# 2. Load a chat model (e.g., qwen/qwen3-4b-2507)
# 3. Start server on port 1234

# Start StoryMaker services
make start

# Verify AI integration
make verify-ai
```

### **Environment Variables**
```bash
# Groq (Creative ONLY)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# LM Studio (Embeddings / Rerank / Planning)
LM_STUDIO_URL=http://127.0.0.1:1234
LM_STUDIO_MODEL=qwen/qwen3-4b-2507
LM_STUDIO_FALLBACK=true
```

## 🧪 Testing Strategy

### **Unit Tests**
- [ ] LM Studio client functionality
- [ ] Groq client enhancements
- [ ] Content generation workflows
- [ ] Embedding and reranking
- [ ] Error handling and fallbacks

### **Integration Tests**
- [ ] End-to-end content generation
- [ ] Model switching workflows
- [ ] Cross-service communication
- [ ] Performance benchmarks
- [ ] Quality gate validation

### **Acceptance Tests**
- [ ] User story completion
- [ ] Content quality standards
- [ ] Performance requirements
- [ ] Error recovery scenarios
- [ ] User experience validation

## 📚 Documentation Requirements

### **API Documentation**
- [ ] LM Studio integration guide
- [ ] Enhanced Groq API documentation
- [ ] Content generation workflows
- [ ] Embedding and reranking APIs
- [ ] Error handling and troubleshooting

### **User Documentation**
- [ ] AI content generation guide
- [ ] Model selection and management
- [ ] Content quality optimization
- [ ] Troubleshooting common issues
- [ ] Best practices for content creation

## 🎯 Deliverables

### **Week 1 Deliverables**
- ✅ LM Studio client implementation
- ✅ Model management system
- ✅ Basic content generation integration
- ✅ Unit tests for LM Studio functionality

### **Week 2 Deliverables**
- ✅ Enhanced Groq integration
- ✅ Embedding and reranking system
- ✅ Advanced content generation workflows
- ✅ Quality control system

### **Week 3 Deliverables**
- ✅ Media AI integration
- ✅ Multimedia content creation
- ✅ Content synchronization
- ✅ Cross-modal consistency

### **Week 4 Deliverables**
- ✅ Comprehensive test suite
- ✅ Performance optimization
- ✅ Complete documentation
- ✅ Production-ready deployment

## 🚨 Risk Mitigation

### **Technical Risks**
- **LM Studio Connectivity**: Implement robust error handling and fallbacks
- **Model Performance**: Test with multiple models, optimize prompts
- **API Rate Limits**: Implement rate limiting and queuing
- **Content Quality**: Build comprehensive quality gates

### **Project Risks**
- **Timeline Delays**: Buffer time built into each week
- **Scope Creep**: Strict focus on Phase 2 objectives
- **Resource Constraints**: Prioritize core functionality first

## 📞 Next Steps

1. **Review and Approve Plan**: Validate timeline and scope
2. **Set Up Development Environment**: Ensure LM Studio is ready
3. **Begin Week 1**: Start with LM Studio client implementation
4. **Daily Check-ins**: Monitor progress and adjust as needed

---

**Contact**: For questions about this plan, contact Bryon McCoy at mccoyb00@gmail.com, 203-989-0875, or [LinkedIn](https://www.linkedin.com/in/bryon-m-00979462).
