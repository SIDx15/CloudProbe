import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import streamlit as st
import google.auth
from google.cloud import logging
from google.oauth2 import service_account
import google.generativeai as genai
import csv

# Import CloudProbe styling
from styles import (
    apply_cloudprobe_styling, 
    render_cloudprobe_header, 
    show_status,
    show_metric,
    show_query,
    show_insight,
    render_footer
)

# Configure Streamlit page
st.set_page_config(
    page_title="CloudProbe - GCP Logging Assistant",
    page_icon="🔍",
    layout="wide"
)

# Apply CloudProbe styling
apply_cloudprobe_styling()

# Render header
render_cloudprobe_header()

class GCPLoggingQueryApp:
    def __init__(self):
        self.logging_client = None
        self.credentials = None
        self.project_id = None
        
    def validate_and_set_credentials(self, credentials_json: str) -> bool:
        """Validate GCP credentials and set up logging client"""
        try:
            # Parse the JSON credentials
            credentials_data = json.loads(credentials_json)
            
            # Validate required fields
            required_fields = ['type', 'project_id', 'client_id', 'client_email', 'private_key']
            for field in required_fields:
                if field not in credentials_data:
                    st.error(f"Missing required field: {field}")
                    return False
            
            # Create credentials object
            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_data
            )
            
            # Set project ID
            self.project_id = credentials_data['project_id']
            
            # Create logging client
            self.logging_client = logging.Client(
                credentials=self.credentials,
                project=self.project_id
            )
            
            return True
            
        except json.JSONDecodeError:
            st.error("Invalid JSON format in credentials")
            return False
        except Exception as e:
            st.error(f"Error setting up credentials: {str(e)}")
            return False
    
    def generate_logging_query(self, user_question: str, gemini_api_key: str) -> str:
        """Generate Cloud Logging query using Gemini API"""
        try:
            # Configure Gemini API
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Create a detailed prompt for query generation
            prompt = f"""
            You are an expert in Google Cloud Logging queries. Generate a Cloud Logging query based on the user's question.
            
            User Question: {user_question}
            
            Guidelines:
            1. Use proper Cloud Logging query syntax
            2. Include relevant resource types (like gce_instance, dataflow_job, etc.)
            3. Use appropriate time filters (today means last 24 hours)
            4. Include severity levels when relevant
            5. For cost queries, look for billing or cost-related logs
            6. For failure queries, look for ERROR severity or specific error messages
            7. Return ONLY the query string, no explanations
            8. do not use syntax like timestamp >= "now-24h" give proper timestamp value
            
            Common resource types:
            - dataflow_job (for Dataflow jobs)
            - gce_instance (for Compute Engine)
            - cloud_function (for Cloud Functions)
            - gke_cluster (for GKE)
            - cloud_sql_database (for Cloud SQL)
            
            Examples:
            - For failed Dataflow jobs today: resource.type="dataflow_job" AND severity="ERROR" AND timestamp>="2024-01-01T00:00:00Z"
            - For cost information: resource.type="billing_account" OR jsonPayload.cost EXISTS
            
            Generate the query:
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            st.error(f"Error generating query with Gemini: {str(e)}")
            return ""
    
    def execute_logging_query(self, query_string: str, max_results: int = 100) -> List[Dict]:
        """Execute the logging query and return results"""
        try:
            if not self.logging_client:
                st.error("Logging client not initialized")
                return []
            
            # Execute the query
            entries = list(self.logging_client.list_entries(
                filter_=query_string,
                max_results=max_results,
                order_by=logging.DESCENDING
            ))
            
            # Convert entries to dictionaries for easier processing
            results = []
            for entry in entries:
                entry_dict = {
                    'timestamp': entry.timestamp.isoformat() if entry.timestamp else '',
                    'severity': entry.severity,
                    'resource_type': entry.resource.type if entry.resource else '',
                    'log_name': entry.log_name,
                    'text_payload': entry.payload.get('message', '') if hasattr(entry.payload, 'get') else str(entry.payload),
                    'json_payload': str(dict(entry.payload)) if hasattr(entry.payload, 'items') else '',
                    'labels': str(dict(entry.labels)) if entry.labels else ''
                }
                results.append(entry_dict)
            
            # Save to CSV
            with open('my_dict.csv', 'w', newline='', encoding='utf-8') as file:
                if results:
                    fieldnames = results[0].keys()
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)
            
            return results
            
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            return []
    
    def analyze_results(self, results: List[Dict], user_question: str, gemini_api_key: str) -> str:
        """Analyze query results and provide insights using Gemini"""
        try:
            if not results:
                return "No results found for your query."
            
            # Configure Gemini API
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Prepare results summary for analysis
            results_summary = {
                'total_entries': len(results),
                'severity_counts': {},
                'resource_types': {},
                'time_range': {
                    'earliest': min(r['timestamp'] for r in results if r['timestamp']),
                    'latest': max(r['timestamp'] for r in results if r['timestamp'])
                }
            }
            
            # Count severities and resource types
            for result in results:
                sev = result.get('severity', 'UNKNOWN')
                res_type = result.get('resource_type', 'UNKNOWN')
                
                results_summary['severity_counts'][sev] = results_summary['severity_counts'].get(sev, 0) + 1
                results_summary['resource_types'][res_type] = results_summary['resource_types'].get(res_type, 0) + 1
            
            # Sample of actual log entries (first 3)
            sample_entries = results[:3]
            
            analysis_prompt = f"""
            Analyze these Google Cloud Logging query results and answer the user's question.
            
            User Question: {user_question}
            
            Results Summary:
            {json.dumps(results_summary, indent=2)}
            
            Sample Log Entries:
            {json.dumps(sample_entries, indent=2)}
            
            Please provide:
            1. Direct answer to the user's question
            2. Key insights from the logs
            3. Any patterns or trends noticed
            4. Recommendations if applicable
            
            Keep the response clear and actionable.
            """
            
            response = model.generate_content(analysis_prompt)
            return response.text
            
        except Exception as e:
            st.error(f"Error analyzing results: {str(e)}")
            return "Error analyzing results"

def main():
    st.markdown("Ask questions about your GCP resources and get intelligent insights from Cloud Logging data.")
    
    # Initialize the app
    app = GCPLoggingQueryApp()
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # GCP Credentials input
    st.sidebar.subheader("GCP Service Account Key")
    credentials_input = st.sidebar.text_area(
        "Paste your GCP Service Account JSON key:",
        height=200,
        help="This should be the complete JSON content of your service account key file."
    )
    
    # Gemini API Key input
    gemini_api_key = st.sidebar.text_input(
        "Gemini API Key:",
        type="password",
        help="Enter your Google Gemini API key"
    )
    
    # Validate credentials
    credentials_valid = False
    if credentials_input and gemini_api_key:
        if st.sidebar.button("Validate Credentials"):
            if app.validate_and_set_credentials(credentials_input):
                credentials_valid = True
                show_status(f"✅ Connected to project: {app.project_id}", True)
            else:
                show_status("❌ Invalid credentials", False)
    
    # Main interface
    if credentials_valid or (credentials_input and gemini_api_key):
        # Auto-validate if not done yet
        if not app.logging_client and credentials_input:
            app.validate_and_set_credentials(credentials_input)
        
        st.header("Ask Your Question")
        
        # Pre-defined example questions
        example_questions = [
            "How many Dataflow jobs failed today?",
            "What was the cost incurred in the last 24 hours?",
            "Show me all ERROR level logs from today",
            "How many Cloud Function invocations failed this week?",
            "What are the most common errors in my GKE clusters?",
            "Show me billing-related logs from today"
        ]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            user_question = st.text_input(
                "Enter your question:",
                placeholder="e.g., How many Dataflow jobs failed today?"
            )
        
        with col2:
            selected_example = st.selectbox(
                "Or select an example:",
                [""] + example_questions
            )
            
            if selected_example:
                user_question = selected_example
        
        if user_question and gemini_api_key:
            if st.button("🔍 Analyze with CloudProbe", type="primary"):
                with st.spinner("Generating Cloud Logging query..."):
                    # Generate query using Gemini
                    query_string = app.generate_logging_query(user_question, gemini_api_key)
                    
                    if query_string:
                        st.subheader("Generated Query")
                        show_query(query_string)
                        
                        with st.spinner("Executing query..."):
                            # Execute the query
                            results = app.execute_logging_query(query_string)
                            
                            if results:
                                st.subheader("Query Results")
                                
                                # Show metrics
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    show_metric("Total Entries", str(len(results)))
                                with col2:
                                    error_count = sum(1 for r in results if r.get('severity') == 'ERROR')
                                    show_metric("Error Entries", str(error_count))
                                with col3:
                                    unique_resources = len(set(r.get('resource_type', '') for r in results))
                                    show_metric("Resource Types", str(unique_resources))
                                
                                # Show results in expandable section
                                with st.expander("View Raw Results", expanded=False):
                                    for i, result in enumerate(results[:10]):  # Show first 10
                                        st.json(result)
                                        if i < len(results) - 1:
                                            st.divider()
                                
                                with st.spinner("Analyzing results..."):
                                    # Analyze results using Gemini
                                    analysis = app.analyze_results(results, user_question, gemini_api_key)
                                    
                                    st.subheader("Analysis & Insights")
                                    show_insight("AI Analysis", analysis)
                            else:
                                st.warning("No results found for your query. Try rephrasing your question.")
                    else:
                        st.error("Failed to generate query. Please check your question and try again.")
    
    else:
        st.info("👈 Please provide your GCP Service Account JSON key and Gemini API key in the sidebar to get started.")
        
        # Show some example usage
        st.header("How to Use")
        st.markdown("""
        1. **Get your GCP Service Account Key:**
           - Go to the Google Cloud Console
           - Navigate to IAM & Admin > Service Accounts
           - Create a new service account or use an existing one
           - Grant it the "Logging Viewer" role
           - Download the JSON key file
        
        2. **Get your Gemini API Key:**
           - Go to Google AI Studio
           - Create a new API key
           - Copy the key
        
        3. **Paste the credentials** in the sidebar
        
        4. **Ask questions** like:
           - "How many Dataflow jobs failed today?"
           - "What errors occurred in my Cloud Functions?"
           - "Show me cost-related logs from this week"
        """)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()