import argparse
import sys
# Dynamic imports based on phase execution

def main():
    parser = argparse.ArgumentParser(description="Weekly Product Review Pulse System")
    parser.add_argument("--mode", choices=["analyze", "full", "check-only"], default="analyze", help="Execution mode")
    parser.add_argument("--product", default="Groww", help="Product name to process")
    parser.add_argument("--min-cluster", type=int, default=15, help="Min reviews per theme (increase for cleaner report)")
    parser.add_argument("--max-themes", type=int, default=7, help="Max number of themes to summarize (LLM calls)")
    args = parser.parse_args()

    print(f"Starting {args.mode} mode for {args.product}...")

    if args.mode == "check-only":
        print("No report due for this week. Exiting.")
        return

    # Phase 1: Ingest
    if args.mode in ["full", "analyze"]:
        from src.phase_1.ingestor import run_ingestion
        run_ingestion(product_name=args.product, weeks=12)
    
    # Phase 2: Clustering
    clustered_df = None
    if args.mode in ["full", "analyze"]:
        from src.phase_2.clustering import run_clustering_pipeline
        clustered_df = run_clustering_pipeline(
            product_id=args.product,
            min_cluster_size=args.min_cluster
        )
    
    # Phase 3: Summarization
    summaries = []
    if args.mode in ["full", "analyze"] and clustered_df is not None:
        from src.phase_3.summarizer import run_summarization_pipeline
        summaries = run_summarization_pipeline(
            clustered_df=clustered_df,
            product_name=args.product,
            max_clusters=args.max_themes
        )

    # Phase 4: Render Report
    report_md = None
    if args.mode in ["full", "analyze"] and summaries:
        from src.phase_4.renderer import render_report
        total_reviews = len(clustered_df) if clustered_df is not None else 0
        report_md = render_report(
            summaries=summaries,
            product_name=args.product,
            total_reviews=total_reviews,
        )
        print("\n" + report_md)
        
        # Save a local copy for review
        import os
        os.makedirs("data/summaries", exist_ok=True)
        with open("data/summaries/latest_report.md", "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"\n[Phase 4] Local copy saved to: data/summaries/latest_report.md")

    # Phase 5: Deliver to Google Docs
    doc_url = None
    if args.mode == "full" and summaries:
        try:
            from src.phase_5.docs_delivery import append_to_doc
            doc_url = append_to_doc(
                summaries=summaries,
                product_name=args.product,
                total_reviews=total_reviews
            )
        except Exception as e:
            print(f"[Phase 5] Google Docs delivery failed: {e}")
            print("  Report is still available in console above.")

    # Phase 6: Send notification email
    if args.mode == "full" and doc_url:
        try:
            from src.phase_6.gmail_delivery import send_summary_email
            send_summary_email(
                doc_link=doc_url,
                product_name=args.product,
                theme_count=len(summaries),
            )
        except Exception as e:
            print(f"[Phase 6] Gmail delivery failed: {e}")

    # Summary
    if args.mode == "full":
        print("\n--- Full pipeline complete ---")
    elif args.mode == "analyze":
        print("\nAnalysis complete. Use --mode full to deliver to Google Workspace.")

if __name__ == "__main__":
    main()
