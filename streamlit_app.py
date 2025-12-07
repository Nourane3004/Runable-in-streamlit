"""
streamlit_app.py - Trading Assistant Streamlit Interface
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import sys
import os
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your trading system
from main import TradingAssistantSystem

# Page configuration
st.set_page_config(
    page_title="Trading Assistant AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'system' not in st.session_state:
        st.session_state.system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

init_session_state()

# Initialize Trading System
@st.cache_resource
def initialize_system(use_qdrant, qdrant_local, collection_name):
    """Initialize the trading system (cached)"""
    try:
        # Set environment variables based on user choice
        os.environ["USE_QDRANT"] = "true" if use_qdrant else "false"
        os.environ["QDRANT_LOCAL"] = "true" if qdrant_local else "false"
        
        system = TradingAssistantSystem()
        system.config["qdrant_collection"] = collection_name
        system.assistant = system._create_assistant()
        return system, None
    except Exception as e:
        return None, str(e)

# Sidebar Configuration
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Trading+AI", use_container_width=True)
    st.markdown("## ⚙️ Configuration")
    
    use_qdrant = st.checkbox("Enable Qdrant RAG", value=True, help="Use Qdrant for document retrieval")
    qdrant_local = st.checkbox("Use Local Qdrant", value=True, help="Use local Qdrant instance")
    collection_name = st.text_input("Collection Name", value="trading_knowledge")
    
    if st.button("🔄 Initialize System", type="primary"):
        with st.spinner("Initializing Trading Assistant..."):
            system, error = initialize_system(use_qdrant, qdrant_local, collection_name)
            if error:
                st.error(f"❌ Initialization failed: {error}")
            else:
                st.session_state.system = system
                st.session_state.initialized = True
                st.success("✅ System initialized successfully!")
                st.rerun()
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 📊 System Status")
    if st.session_state.initialized and st.session_state.system:
        config = st.session_state.system.config
        st.success("🟢 Active")
        st.info(f"**RAG:** {'Enabled' if config.get('use_qdrant') else 'Disabled'}")
        st.info(f"**Mode:** {'Local' if config.get('qdrant_local') else 'Cloud'}")
        st.info(f"**Collection:** {config.get('qdrant_collection', 'N/A')}")
    else:
        st.warning("🟡 Not initialized")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    if st.button("📋 View Configuration"):
        if st.session_state.system:
            st.json(st.session_state.system.config)
    
    st.markdown("---")
    
    # Example Queries
    st.markdown("### 💡 Example Queries")
    example_queries = [
        "Should I buy Apple stock?",
        "What's the market risk today?",
        "Analyze Tesla stock",
        "Give me a market summary",
        "Is Bitcoin a good investment?",
    ]
    
    for query in example_queries:
        if st.button(query, key=f"example_{query}"):
            st.session_state.current_query = query

# Main Content
st.markdown('<div class="main-header">📈 Trading Assistant AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your AI-powered trading advisor with multi-agent analysis</div>', unsafe_allow_html=True)

# Check if system is initialized
if not st.session_state.initialized:
    st.markdown('<div class="warning-box">⚠️ Please initialize the system using the sidebar configuration.</div>', unsafe_allow_html=True)
    
    # Show features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Signal Generation")
        st.write("Get buy/sell recommendations with confidence scores")
    
    with col2:
        st.markdown("### 🔍 Market Analysis")
        st.write("Deep analysis using multiple AI agents")
    
    with col3:
        st.markdown("### 📊 Risk Assessment")
        st.write("Comprehensive risk evaluation and position sizing")
    
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📈 Analysis", "📚 History"])
    
    with tab1:
        # Chat Interface
        st.markdown("### Ask Your Trading Question")
        
        # Use session state for query if set by example button
        default_query = st.session_state.get('current_query', '')
        if default_query:
            del st.session_state.current_query
        
        with st.form(key="query_form", clear_on_submit=True):
            user_query = st.text_input(
                "Enter your question:",
                value=default_query,
                placeholder="e.g., Should I buy Tesla stock?",
                help="Ask about trading signals, market analysis, or risk assessment"
            )
            submit_button = st.form_submit_button("🚀 Analyze", type="primary")
        
        if submit_button and user_query:
            with st.spinner("🤖 Analyzing your query..."):
                try:
                    # Process query
                    response = st.session_state.system.process_query_sync(user_query)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now(),
                        "query": user_query,
                        "response": response
                    })
                    
                    # Display response
                    if not response.get("success", False):
                        st.markdown(f'<div class="error-box">🚫 {response.get("message", "Query failed")}</div>', unsafe_allow_html=True)
                        if response.get('suggestion'):
                            st.info(f"💡 {response.get('suggestion')}")
                    else:
                        # Success response
                        st.markdown(f'<div class="success-box">✅ Analysis Complete</div>', unsafe_allow_html=True)
                        
                        # Metrics row
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            recommendation = response['recommendation']
                            color = "🟢" if recommendation == "BUY" else "🔴" if recommendation == "SELL" else "🟡"
                            st.metric("Recommendation", f"{color} {recommendation}")
                        
                        with col2:
                            st.metric("Confidence", f"{response['confidence']}%")
                        
                        with col3:
                            st.metric("Position Size", response['position_size'])
                        
                        with col4:
                            risk_emoji = "🟢" if response['risk_level'] == "Low" else "🟡" if response['risk_level'] == "Medium" else "🔴"
                            st.metric("Risk Level", f"{risk_emoji} {response['risk_level']}")
                        
                        # Explanation
                        st.markdown("### 📝 Explanation")
                        st.write(response['explanation'])
                        
                        # Key Factors
                        if response.get('key_factors'):
                            st.markdown("### 🔑 Key Factors")
                            for factor in response['key_factors']:
                                st.markdown(f"- {factor}")
                        
                        # Detailed Analysis (expandable)
                        with st.expander("🔬 Detailed Analysis"):
                            detailed = response.get('detailed_analysis', {})
                            
                            # Agent Outputs
                            if detailed.get('agent_outputs'):
                                st.markdown("#### Agent Outputs")
                                for agent_name, agent_data in detailed['agent_outputs'].items():
                                    st.markdown(f"**{agent_name}**")
                                    st.json(agent_data)
                            
                            # RAG Documents
                            if detailed.get('agent_outputs', {}).get('RAG_AGENT', {}).get('docs'):
                                st.markdown("#### 📄 Retrieved Documents")
                                docs = detailed['agent_outputs']['RAG_AGENT']['docs']
                                for i, doc in enumerate(docs, 1):
                                    st.markdown(f"**Document {i}** (Score: {doc.get('score', 'N/A')})")
                                    st.write(doc.get('text', ''))
                                    st.markdown("---")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("### 💬 Recent Queries")
            
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
                with st.expander(f"🕐 {chat['timestamp'].strftime('%H:%M:%S')} - {chat['query'][:50]}..."):
                    st.write(f"**Query:** {chat['query']}")
                    response = chat['response']
                    
                    if response.get('success'):
                        st.write(f"**Recommendation:** {response['recommendation']}")
                        st.write(f"**Confidence:** {response['confidence']}%")
                        st.write(f"**Explanation:** {response['explanation']}")
                    else:
                        st.write(f"**Status:** {response.get('message', 'Failed')}")
    
    with tab2:
        # Analysis Dashboard
        st.markdown("### 📈 Analysis Dashboard")
        
        if st.session_state.chat_history:
            # Statistics
            successful_queries = [c for c in st.session_state.chat_history if c['response'].get('success')]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Queries", len(st.session_state.chat_history))
            
            with col2:
                st.metric("Successful", len(successful_queries))
            
            with col3:
                success_rate = (len(successful_queries) / len(st.session_state.chat_history) * 100) if st.session_state.chat_history else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            # Recommendations distribution
            if successful_queries:
                st.markdown("#### 📊 Recommendation Distribution")
                buy_count = sum(1 for c in successful_queries if c['response']['recommendation'] == 'BUY')
                sell_count = sum(1 for c in successful_queries if c['response']['recommendation'] == 'SELL')
                hold_count = sum(1 for c in successful_queries if c['response']['recommendation'] == 'HOLD')
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🟢 BUY", buy_count)
                with col2:
                    st.metric("🔴 SELL", sell_count)
                with col3:
                    st.metric("🟡 HOLD", hold_count)
                
                # Average confidence
                avg_confidence = sum(c['response']['confidence'] for c in successful_queries) / len(successful_queries)
                st.metric("Average Confidence", f"{avg_confidence:.1f}%")
        else:
            st.info("📊 No analysis data yet. Start by asking some trading questions!")
    
    with tab3:
        # History
        st.markdown("### 📚 Query History")
        
        if st.session_state.chat_history:
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}**")
                        st.write(f"Q: {chat['query']}")
                        
                        response = chat['response']
                        if response.get('success'):
                            st.write(f"✅ {response['recommendation']} ({response['confidence']}% confidence)")
                        else:
                            st.write(f"🚫 {response.get('message', 'Failed')}")
                    
                    with col2:
                        if st.button("View Details", key=f"detail_{i}"):
                            st.json(chat['response'])
                    
                    st.markdown("---")
            
            # Export option
            if st.button("📥 Export History as JSON"):
                history_json = json.dumps(
                    [{"timestamp": c['timestamp'].isoformat(), 
                      "query": c['query'], 
                      "response": c['response']} 
                     for c in st.session_state.chat_history],
                    indent=2
                )
                st.download_button(
                    label="Download JSON",
                    data=history_json,
                    file_name=f"trading_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        else:
            st.info("📚 No query history yet. Start asking questions!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>⚠️ <strong>Disclaimer:</strong> This is an AI-powered tool for educational purposes. 
    Not financial advice. Always do your own research and consult with financial advisors.</p>
    <p>Powered by Multi-Agent Trading System | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)