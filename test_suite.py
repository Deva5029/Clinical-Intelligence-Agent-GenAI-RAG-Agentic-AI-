import os
import requests
import time
import pandas as pd
from datetime import datetime

# The API endpoint
API_URL = "http://localhost:8000/ask"

# Diverse test cases to challenge the RAG system
TEST_QUERIES = [
    "What is the primary purpose of trial NCT01007279?",
    "Which trials involve Rosuvastatin and its effects on myonecrosis?",
    "Are there any studies focusing on cardiovascular outcomes in PCI patients?",
    "Summarize the intervention used in the trial titled 'Statins in PCI'.",
    "Compare the goals of NCT01007279 with other statin-related trials in the database."
]

def run_performance_test():
    results = []
    print(f"🧪 Starting Performance Test at {datetime.now()}...")

    for query in TEST_QUERIES:
        start_time = time.time()
        
        try:
            response = requests.post(f"{API_URL}?query={query}")
            duration = round(time.time() - start_time, 2)
            
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer found")
                status = "✅ PASS"
            else:
                answer = f"Error: {response.status_code}"
                status = "❌ FAIL"
        except Exception as e:
            duration = 0
            answer = str(e)
            status = "❌ CRASH"

        results.append({
            "Query": query,
            "Response Time (sec)": duration,
            "Status": status,
            "Agent Answer Snippet": answer[:150] + "..."
        })
        print(f"{status} | {query} | {duration}s")

    # 2. Save the Report
    df = pd.DataFrame(results)
    report_name = f"reports/performance_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    if not os.path.exists('reports'):
        os.makedirs('reports')
        
    df.to_csv(report_name, index=False)
    print(f"\n📄 Report generated: {report_name}")

if __name__ == "__main__":
    run_performance_test()