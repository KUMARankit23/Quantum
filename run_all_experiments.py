"""
Master script: Run all experiments and generate results.
Orchestrates Phases 3-5: Experiments, Visualization, and Dashboard.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.experiments.batch_runner import BatchExperimentRunner
from src.visualization.plot_generator import PlotGenerator
from src.visualization.comparison_plots import ImageComparisonPlotter
from src.visualization.results_analyzer import ResultsAnalyzer
from src.visualization.dashboard import DashboardGenerator
from src.visualization.report_generator import ResearchReportGenerator


def main():
    """Run complete experiment and analysis pipeline."""
    
    print("\n" + "="*70)
    print("QUANTUM IMAGE PROCESSING RESEARCH")
    print("COMPLETE PIPELINE: EXPERIMENTS → ANALYSIS → DASHBOARD → REPORT")
    print("="*70)
    
    start_time = time.time()
    
    # Phase 3: Run all experiments
    print("\n" + "-"*70)
    print("PHASE 3: RUNNING CONTROLLED EXPERIMENTS")
    print("-"*70)
    
    batch_runner = BatchExperimentRunner(verbose=True)
    results = batch_runner.run_all_experiments()
    
    # Save results to CSV
    print("\nSaving results...")
    batch_runner.save_results_to_csv(results)
    
    # Print summary
    summary = batch_runner.generate_summary_statistics(results)
    batch_runner.print_summary(summary)
    
    # Phase 4: Visualization
    print("\n" + "-"*70)
    print("PHASE 4: GENERATING VISUALIZATIONS & ANALYSIS")
    print("-"*70)
    
    # Generate plots
    plot_generator = PlotGenerator()
    if Path("results/experiments.csv").exists():
        plot_generator.generate_all_plots("results/experiments.csv")
    
    # Generate image comparisons
    comparison_plotter = ImageComparisonPlotter()
    comparison_plotter.generate_all_comparisons()
    
    # Analyze results
    print("\nAnalyzing results...")
    analyzer = ResultsAnalyzer()
    analyzer.print_analysis()
    analyzer.save_analysis()
    
    # Phase 5: Dashboard Generation
    print("\n" + "-"*70)
    print("PHASE 5: GENERATING DASHBOARD & REPORT")
    print("-"*70)
    
    print("\nGenerating interactive dashboard...")
    dashboard_gen = DashboardGenerator()
    dashboard_gen.generate_from_results()
    
    print("\nGenerating research report...")
    report_gen = ResearchReportGenerator()
    report_gen.generate()
    
    # Summary
    total_time = time.time() - start_time
    
    print("\n" + "="*70)
    print("ALL PHASES COMPLETE - FULL PIPELINE EXECUTED")
    print("="*70)
    print(f"\nTotal execution time: {total_time/60:.1f} minutes")
    print(f"\nAll outputs generated:")
    print(f"  ✓ results/experiments.csv (raw data)")
    print(f"  ✓ results/analysis_summary.txt (findings)")
    print(f"  ✓ results/RESEARCH_REPORT.md (full report)")
    print(f"  ✓ dashboard.html (interactive viewer)")
    print(f"  ✓ plots/ (7 analysis plots)")
    print(f"  ✓ plots/comparisons/ (image comparisons)")
    print(f"\nNext steps:")
    print(f"  1. Open dashboard.html in a web browser")
    print(f"  2. Review results/RESEARCH_REPORT.md")
    print(f"  3. Examine plots in plots/ directory")
    print(f"  4. Use DEMO_SCRIPT.md for presentation")
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExperiments interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
