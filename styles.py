"""
CloudProbe Styling Components
This file contains all the CSS styles and UI components for CloudProbe
"""

import streamlit as st

class CloudProbeStyles:
    """Class containing all styling methods for CloudProbe"""
    
    @staticmethod
    def inject_custom_css():
        """Inject custom CSS for overall app styling"""
        st.markdown("""
        <style>
        /* Custom CSS for CloudProbe */
        .main-header {
            background: linear-gradient(90deg, #4285f4, #34a853);
            color: white;
            padding: 30px 0;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 3.5rem;
            font-weight: 700;
        }
        
        .main-header p {
            margin: 10px 0 0 0;
            font-size: 1.3rem;
            opacity: 0.9;
        }
        
        .sidebar-header {
            background: #f8fafc;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }
        
        .status-badge {
            background: #10b981;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .error-badge {
            background: #ef4444;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .metric-card {
            background: #f8fafc;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            text-align: center;
            margin: 10px 0;
        }
        
        .metric-card h3 {
            color: #1e40af;
            margin: 0;
            font-size: 2rem;
        }
        
        .metric-card p {
            color: #64748b;
            margin: 5px 0 0 0;
            font-size: 0.9rem;
        }
        
        .query-box {
            background: #f8fafc;
            color: #1f2937;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4285f4;
            margin: 10px 0;
            border: 1px solid #e2e8f0;
        }
        
        .insight-box {
            background: #f0f9ff;
            color: #000000;
            border: 1px solid #0ea5e9;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .insight-box h4 {
            color: #0c4a6e;
            margin: 0 0 10px 0;
        }
        
        .insight-box p {
            color: #0f172a;
            line-height: 1.6;
        }
        
        .footer {
            text-align: center;
            color: #666;
            padding: 20px 0;
            border-top: 1px solid #e2e8f0;
            margin-top: 30px;
        }
        
        /* Custom button styling */
        .stButton > button {
            background: linear-gradient(90deg, #4285f4, #34a853);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1rem;
        }
        
        .stButton > button:hover {
            background: linear-gradient(90deg, #3367d6, #2d8f3f);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header():
        """Render the main CloudProbe header"""
        st.markdown("""
        <div class="main-header">
            <h1>🔍 CloudProbe</h1>
            <p>AI-Powered GCP Logging & Analytics Platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_header():
        """Render styled sidebar header"""
        st.markdown("""
        <div class="sidebar-header">
            <h3 style="margin: 0; color: #1e40af;">🔍 CloudProbe Settings</h3>
            <p style="margin: 5px 0 0 0; color: #64748b; font-size: 0.9rem;">
                Configure your GCP connection
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_status_badge(status: str, is_success: bool = True):
        """Render status badge"""
        badge_class = "status-badge" if is_success else "error-badge"
        st.markdown(f"""
        <div style="text-align: center; margin: 10px 0;">
            <span class="{badge_class}">{status}</span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric_card(title: str, value: str, description: str = ""):
        """Render a metric card"""
        st.markdown(f"""
        <div class="metric-card">
            <h3>{value}</h3>
            <p><strong>{title}</strong></p>
            {f'<p style="font-size: 0.8rem; color: #9ca3af;">{description}</p>' if description else ''}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_query_display(query: str):
        """Render query in styled box"""
        st.markdown(f"""
        <div class="query-box">
            <h4 style="color: #1e40af; margin: 0 0 10px 0;">Generated Query:</h4>
            <code style="color: #374151; background: #ffffff; padding: 10px; display: block; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.4; white-space: pre-wrap;">{query}</code>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_insight_box(title: str, content: str):
        """Render insights in styled box"""
        st.markdown(f"""
        <div class="insight-box">
            <h4>{title}</h4>
            <p style="margin: 0; color: #000000;">{content}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """Render footer with CloudProbe branding"""
        st.markdown("""
        <div class="footer">
            <p>Powered by <strong>CloudProbe</strong> - Intelligent GCP Analysis</p>
            <p style="font-size: 0.8rem; color: #9ca3af;">
                🚀 AI-Powered • ⚡ Real-time Analysis • 📊 Smart Insights
            </p>
        </div>
        """, unsafe_allow_html=True)

# Convenience functions for easy import
def apply_cloudprobe_styling():
    """Apply all CloudProbe styling - call this once at the start of your app"""
    CloudProbeStyles.inject_custom_css()

def render_cloudprobe_header():
    """Render the main header"""
    CloudProbeStyles.render_header()

def render_cloudprobe_sidebar():
    """Render sidebar header"""
    CloudProbeStyles.render_sidebar_header()

def show_status(message: str, success: bool = True):
    """Show status message"""
    CloudProbeStyles.render_status_badge(message, success)

def show_metric(title: str, value: str, description: str = ""):
    """Show metric card"""
    CloudProbeStyles.render_metric_card(title, value, description)

def show_query(query: str):
    """Show query in styled box"""
    CloudProbeStyles.render_query_display(query)

def show_insight(title: str, content: str):
    """Show insight box"""
    CloudProbeStyles.render_insight_box(title, content)

def render_footer():
    """Render footer"""
    CloudProbeStyles.render_footer()