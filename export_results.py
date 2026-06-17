"""
Export scan results from monitor.db to Excel and CSV formats
"""
import sqlite3
import pandas as pd
from datetime import datetime
import os

def export_scan_results(scan_id=None, output_dir='reports'):
    """Export scan results to Excel and CSV files"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('data/monitor.db')
    
    try:
        # Get the latest scan if no scan_id provided
        if scan_id is None:
            cursor = conn.cursor()
            cursor.execute("SELECT scan_id FROM scan_history ORDER BY start_time DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                scan_id = result[0]
            else:
                print("No scans found in database")
                return
        
        print(f"Exporting results for scan: {scan_id}")
        
        # 1. Export Scan Summary
        scan_summary_query = """
        SELECT
            scan_id,
            start_time,
            end_time,
            status,
            pages_scanned,
            links_checked,
            images_checked,
            issues_found,
            new_issues,
            resolved_issues,
            error_message
        FROM scan_history
        WHERE scan_id = ?
        """
        df_summary = pd.read_sql_query(scan_summary_query, conn, params=(scan_id,))
        
        # 2. Export All Issues
        issues_query = """
        SELECT
            i.id as issue_id,
            p.url as page_url,
            p.offering,
            p.priority,
            i.resource_url,
            i.issue_type,
            i.status_code,
            i.error_message,
            i.confidence_score,
            i.first_detected,
            i.last_detected,
            i.detection_count,
            CASE WHEN i.resolved = 1 THEN 'resolved' ELSE 'active' END as status,
            i.resolved_at,
            i.notification_sent
        FROM issues i
        JOIN pages p ON i.page_id = p.id
        ORDER BY p.url, i.issue_type, i.resource_url
        """
        df_issues = pd.read_sql_query(issues_query, conn)
        
        # 3. Export Issues Summary by Page
        page_summary_query = """
        SELECT
            p.url as page_url,
            p.offering,
            p.priority,
            COUNT(*) as total_issues,
            SUM(CASE WHEN i.issue_type = 'broken_link' THEN 1 ELSE 0 END) as broken_links,
            SUM(CASE WHEN i.issue_type = 'broken_image' THEN 1 ELSE 0 END) as broken_images,
            SUM(CASE WHEN i.issue_type = 'redirect' THEN 1 ELSE 0 END) as redirects,
            SUM(CASE WHEN i.issue_type = 'slow_response' THEN 1 ELSE 0 END) as slow_responses,
            SUM(CASE WHEN i.resolved = 0 THEN 1 ELSE 0 END) as active_issues,
            SUM(CASE WHEN i.resolved = 1 THEN 1 ELSE 0 END) as resolved_issues
        FROM issues i
        JOIN pages p ON i.page_id = p.id
        GROUP BY p.url, p.offering, p.priority
        ORDER BY total_issues DESC
        """
        df_page_summary = pd.read_sql_query(page_summary_query, conn)
        
        # 4. Export Issues by Type
        type_summary_query = """
        SELECT
            i.issue_type,
            COUNT(*) as count,
            AVG(i.confidence_score) as avg_confidence,
            SUM(CASE WHEN i.resolved = 0 THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN i.resolved = 1 THEN 1 ELSE 0 END) as resolved
        FROM issues i
        GROUP BY i.issue_type
        ORDER BY count DESC
        """
        df_type_summary = pd.read_sql_query(type_summary_query, conn)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export to Excel (multiple sheets)
        excel_filename = f'{output_dir}/scan_results_{scan_id}_{timestamp}.xlsx'
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Scan Summary', index=False)
            df_page_summary.to_excel(writer, sheet_name='Issues by Page', index=False)
            df_type_summary.to_excel(writer, sheet_name='Issues by Type', index=False)
            df_issues.to_excel(writer, sheet_name='All Issues', index=False)
        
        print(f"[OK] Excel report created: {excel_filename}")
        
        # Export to CSV files
        csv_summary_file = f'{output_dir}/scan_summary_{scan_id}_{timestamp}.csv'
        csv_issues_file = f'{output_dir}/all_issues_{scan_id}_{timestamp}.csv'
        csv_page_summary_file = f'{output_dir}/issues_by_page_{scan_id}_{timestamp}.csv'
        csv_type_summary_file = f'{output_dir}/issues_by_type_{scan_id}_{timestamp}.csv'
        
        df_summary.to_csv(csv_summary_file, index=False)
        df_issues.to_csv(csv_issues_file, index=False)
        df_page_summary.to_csv(csv_page_summary_file, index=False)
        df_type_summary.to_csv(csv_type_summary_file, index=False)
        
        print(f"[OK] CSV reports created:")
        print(f"   - {csv_summary_file}")
        print(f"   - {csv_issues_file}")
        print(f"   - {csv_page_summary_file}")
        print(f"   - {csv_type_summary_file}")
        
        # Print summary statistics
        print("\n" + "="*60)
        print("SCAN SUMMARY")
        print("="*60)
        if not df_summary.empty:
            print(f"Scan ID: {df_summary['scan_id'].iloc[0]}")
            print(f"Status: {df_summary['status'].iloc[0]}")
            print(f"Pages Scanned: {df_summary['pages_scanned'].iloc[0]}")
            print(f"Links Checked: {df_summary['links_checked'].iloc[0]}")
            print(f"Images Checked: {df_summary['images_checked'].iloc[0]}")
            print(f"Total Issues: {df_summary['issues_found'].iloc[0]}")
        
        print("\n" + "="*60)
        print("ISSUES BY TYPE")
        print("="*60)
        print(df_type_summary.to_string(index=False))
        
        print("\n" + "="*60)
        print("TOP 10 PAGES WITH MOST ISSUES")
        print("="*60)
        print(df_page_summary.head(10).to_string(index=False))
        
        print("\n" + "="*60)
        print(f"[SUCCESS] All reports exported to '{output_dir}/' directory")
        print("="*60)
        
    except Exception as e:
        print(f"[ERROR] Error exporting results: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    # Export the latest scan results
    export_scan_results()

# Made with Bob
