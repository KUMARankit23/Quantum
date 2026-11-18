"""
Simple web-based dashboard for experiment visualization and interaction.
Provides UI for running experiments and viewing results.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class DashboardGenerator:
    """Generates a simple HTML dashboard for results visualization."""
    
    def __init__(self, output_file: str = "dashboard.html"):
        """
        Initialize dashboard generator.
        
        Args:
            output_file: Output HTML file path
        """
        self.output_file = Path(output_file)
    
    def generate_from_results(self, results_csv: str = "results/experiments.csv") -> None:
        """
        Generate dashboard HTML from results CSV.
        
        Args:
            results_csv: Path to results CSV file
        """
        if not Path(results_csv).exists():
            print(f"Results file not found: {results_csv}")
            print("Run experiments first: python run_all_experiments.py")
            return
        
        # Load results
        df = pd.read_csv(results_csv)
        
        # Generate HTML
        html = self._generate_html(df)
        
        # Save (with UTF-8 encoding for emoji support)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Dashboard generated: {self.output_file}")
    
    def _generate_html(self, df: pd.DataFrame) -> str:
        """Generate premium HTML dashboard with modern design."""
        
        # Calculate statistics
        stats = {
            'total_exp': len(df),
            'avg_psnr': df['psnr'].mean(),
            'avg_class_psnr': df['classical_psnr'].mean(),
            'avg_mse': df['mse'].mean(),
            'avg_ssim': df['ssim'].mean() if 'ssim' in df.columns else 0,
            'avg_q_time': df['quantum_total_time'].mean(),
            'avg_c_time': df['classical_time'].mean(),
            'avg_time_ratio': (df['quantum_total_time'].mean()) / (df['classical_time'].mean() + 0.01),
            'psnr_range': f"{df['psnr'].min():.1f} - {df['psnr'].max():.1f}",
        }
        
        top_5 = df.nlargest(5, 'psnr')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Research Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary: #667eea;
            --primary-dark: #5568d3;
            --primary-light: #8b9ef4;
            --secondary: #764ba2;
            --accent: #f093fb;
            --dark-bg: #0f1419;
            --darker-bg: #0a0e13;
            --card-bg: #1a1f2e;
            --border-color: #2a3142;
            --text-primary: #e8eaed;
            --text-secondary: #b0b4ba;
            --text-tertiary: #808588;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --shadow: 0 20px 60px rgba(0,0,0,0.5);
            --shadow-sm: 0 5px 15px rgba(0,0,0,0.3);
        }}
        
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--dark-bg) 0%, var(--darker-bg) 100%);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        /* Animated background */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 50%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
            z-index: 1;
        }}
        
        /* Navigation */
        nav {{
            background: rgba(26, 31, 46, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 0;
            margin-bottom: 40px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        nav .nav-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        nav ul {{
            display: flex;
            gap: 2rem;
            list-style: none;
        }}
        
        nav a {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            transition: color 0.3s ease;
        }}
        
        nav a:hover {{
            color: var(--primary);
        }}
        
        /* Header Section */
        .header {{
            background: linear-gradient(135deg, var(--card-bg) 0%, rgba(26, 31, 46, 0.5) 100%);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 60px 40px;
            margin-bottom: 40px;
            backdrop-filter: blur(10px);
            animation: fadeInDown 0.8s ease;
        }}
        
        .header h1 {{
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 10px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin-bottom: 5px;
        }}
        
        .header-meta {{
            color: var(--text-tertiary);
            font-size: 0.85rem;
            margin-top: 15px;
        }}
        
        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, var(--card-bg) 0%, rgba(26, 31, 46, 0.5) 100%);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            animation: fadeInUp 0.6s ease;
            cursor: hover;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            border-color: var(--primary);
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-unit {{
            color: var(--text-tertiary);
            font-size: 0.9rem;
            margin-top: 5px;
        }}
        
        /* Section Title */
        .section-title {{
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 25px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, var(--primary) 0%, transparent 100%);
        }}
        
        /* Card Section */
        .card-section {{
            background: linear-gradient(135deg, var(--card-bg) 0%, rgba(26, 31, 46, 0.5) 100%);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            animation: fadeIn 0.8s ease;
        }}
        
        /* Tables */
        .table-wrapper {{
            overflow-x: auto;
            border-radius: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: rgba(102, 126, 234, 0.1);
            border-bottom: 2px solid var(--primary);
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: var(--primary);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-secondary);
        }}
        
        tr:hover {{
            background: rgba(102, 126, 234, 0.05);
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            background: rgba(102, 126, 234, 0.2);
            color: var(--primary);
        }}
        
        .badge.success {{
            background: rgba(16, 185, 129, 0.2);
            color: var(--success);
        }}
        
        .badge.warning {{
            background: rgba(245, 158, 11, 0.2);
            color: var(--warning);
        }}
        
        /* Top Performers */
        .performer-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: rgba(102, 126, 234, 0.05);
            border-left: 3px solid var(--primary);
            border-radius: 5px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }}
        
        .performer-item:hover {{
            background: rgba(102, 126, 234, 0.1);
            transform: translateX(5px);
        }}
        
        .performer-rank {{
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            min-width: 40px;
        }}
        
        .performer-info {{
            flex: 1;
            margin: 0 15px;
        }}
        
        .performer-name {{
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .performer-metrics {{
            font-size: 0.85rem;
            color: var(--text-tertiary);
        }}
        
        .performer-value {{
            font-weight: 700;
            color: var(--success);
        }}
        
        /* Progress Bar */
        .progress-bar {{
            background: var(--border-color);
            height: 6px;
            border-radius: 3px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
            transition: width 0.5s ease;
        }}
        
        /* Animations */
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}
        
        /* Footer */
        footer {{
            background: rgba(26, 31, 46, 0.5);
            border-top: 1px solid var(--border-color);
            padding: 40px;
            text-align: center;
            margin-top: 60px;
            color: var(--text-secondary);
        }}
        
        footer p {{
            margin: 5px 0;
        }}
        
        .footer-gradient {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .header {{
                padding: 40px 20px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .section-title {{
                font-size: 1.3rem;
            }}
            
            nav ul {{
                gap: 1rem;
            }}
            
            .performer-item {{
                flex-direction: column;
                align-items: flex-start;
            }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="nav-content">
            <div class="logo">⚛️ Quantum Research</div>
            <ul>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#stats">Statistics</a></li>
                <li><a href="#results">Results</a></li>
            </ul>
        </div>
    </nav>
    
    <div class="container">
        <!-- Header -->
        <div class="header" id="overview">
            <h1>Quantum Image Processing Research</h1>
            <p>Advanced Performance Analysis & Interactive Dashboard</p>
            <div class="header-meta">
                <strong>Generated:</strong> {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}<br>
                <strong>Total Experiments:</strong> {stats['total_exp']} | <strong>Data Points:</strong> {stats['total_exp']}
            </div>
        </div>
        
        <!-- Stats Grid -->
        <div id="stats">
            <h2 class="section-title">Key Metrics Overview</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Experiments</div>
                    <div class="stat-value">{stats['total_exp']}</div>
                    <div class="stat-unit">data points collected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Quantum PSNR</div>
                    <div class="stat-value">{stats['avg_psnr']:.1f}</div>
                    <div class="stat-unit">dB (decibels)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Classical PSNR</div>
                    <div class="stat-value">{stats['avg_class_psnr']:.1f}</div>
                    <div class="stat-unit">dB (decibels)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Speed Ratio (Q/C)</div>
                    <div class="stat-value">{stats['avg_time_ratio']:.1f}×</div>
                    <div class="stat-unit">quantum slower than classical</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Quantum Time</div>
                    <div class="stat-value">{stats['avg_q_time']*1000:.0f}</div>
                    <div class="stat-unit">milliseconds</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Classical Time</div>
                    <div class="stat-value">{stats['avg_c_time']*1000:.0f}</div>
                    <div class="stat-unit">milliseconds</div>
                </div>
            </div>
        </div>
        
        <!-- Top Performers -->
        <div id="results">
            <div class="card-section">
                <h2 class="section-title">⭐ Top Performing Experiments</h2>
                <div style="display: grid; gap: 15px;">"""
        
        for idx, (_, row) in enumerate(top_5.iterrows(), 1):
            psnr_val = row['psnr']
            max_psnr = df['psnr'].max()
            progress = (psnr_val / max_psnr) * 100
            
            html += f"""
                    <div class="performer-item">
                        <div class="performer-rank">#{idx}</div>
                        <div class="performer-info">
                            <div class="performer-name">{row.get('experiment_id', 'Experiment')}</div>
                            <div class="performer-metrics">
                                Size: {row.get('image_size', 'N/A')}×{row.get('image_size', 'N/A')} | 
                                Qubits: {row.get('num_qubits', 'N/A')}
                            </div>
                            <div class="progress-bar" style="margin-top: 8px;">
                                <div class="progress-fill" style="width: {progress}%;"></div>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div class="performer-value">{psnr_val:.2f} dB</div>
                            <div style="font-size: 0.85rem; color: var(--text-tertiary);">MSE: {row['mse']:.4f}</div>
                        </div>
                    </div>"""
        
        html += """
                </div>
            </div>
        """
        
        # Full Results Table
        html += f"""
            <div class="card-section">
                <h2 class="section-title">📊 Complete Results Table</h2>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Experiment ID</th>
                                <th>Type</th>
                                <th>Size</th>
                                <th>Qubits</th>
                                <th>PSNR (dB)</th>
                                <th>MSE</th>
                                <th>Time (ms)</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>"""
        
        for _, row in df.head(15).iterrows():
            exp_id = row.get('experiment_id', 'N/A')
            exp_type = row.get('experiment_type', 'N/A')
            size = row.get('image_size', 'N/A')
            qubits = row.get('num_qubits', 'N/A')
            psnr = row['psnr']
            mse = row['mse']
            time_ms = row['quantum_total_time'] * 1000
            
            # Determine status badge
            if psnr > 30:
                status_badge = '<span class="badge success">Excellent</span>'
            elif psnr > 20:
                status_badge = '<span class="badge">Good</span>'
            else:
                status_badge = '<span class="badge warning">Fair</span>'
            
            html += f"""
                            <tr>
                                <td>{exp_id}</td>
                                <td>{exp_type.capitalize()}</td>
                                <td>{size}×{size}</td>
                                <td>{qubits}</td>
                                <td><strong>{psnr:.2f}</strong></td>
                                <td>{mse:.6f}</td>
                                <td>{time_ms:.1f}</td>
                                <td>{status_badge}</td>
                            </tr>"""
        
        if len(df) > 15:
            html += f"""
                            <tr>
                                <td colspan="8" style="text-align: center; color: var(--text-tertiary);">
                                    ... and {len(df) - 15} more experiments
                                </td>
                            </tr>"""
        
        html += """
                        </tbody>
                    </table>
                </div>
            </div>
        """
        
        # Footer
        html += """
    </div>
    
    <footer>
        <p class="footer-gradient">Quantum Image Processing Performance Research</p>
        <p>Advanced empirical study with interactive analysis dashboard</p>
        <p style="margin-top: 15px; font-size: 0.85rem;">
            For full analysis visit: <code style="color: var(--primary);">results/RESEARCH_REPORT.md</code>
        </p>
    </footer>
    
    <script>
        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
        
        // Animate stat cards on load
        window.addEventListener('load', () => {
            document.querySelectorAll('.stat-card').forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = '1';
                }, index * 100);
            });
        });
    </script>
</body>
</html>"""
        
        return html
    
    def generate_empty(self) -> None:
        """Generate empty dashboard with instructions."""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Quantum Image Processing - Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 600px;
            text-align: center;
        }
        h1 { color: #667eea; margin-bottom: 20px; }
        p { color: #666; margin-bottom: 15px; line-height: 1.6; }
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        .button {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border-radius: 5px;
            text-decoration: none;
            margin-top: 20px;
        }
        .button:hover { background: #764ba2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Quantum Image Processing Dashboard</h1>
        <p>No results found yet.</p>
        <p>To generate results, run:</p>
        <p><code>python run_all_experiments.py</code></p>
        <p>This will execute all experiments and generate visualizations.</p>
    </div>
</body>
</html>
"""
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Empty dashboard created: {self.output_file}")


if __name__ == "__main__":
    generator = DashboardGenerator()
    
    # Try to generate from results, otherwise create empty
    results_file = Path("results/experiments.csv")
    if results_file.exists():
        generator.generate_from_results()
    else:
        generator.generate_empty()
