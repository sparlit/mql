import os
import sqlite3
import pandas as pd
import logging
import json
from datetime import datetime

class AutonomousOptimizer:
    def __init__(self, db_dir="Python/db"):
        """
        Initialize the AutonomousOptimizer with the path to the database directory.
        
        Parameters:
            db_dir (str): Filesystem path to the directory containing monthly SQLite databases (default: "Python/db").
        """
        self.db_dir = db_dir

    def run_weekend_optimization(self):
        """
        Run a weekend optimization cycle that computes regime-level weights and persists them.
        
        Loads signals from the current month's SQLite database (Python/db/trades_YYYYMM.db). If the database file is missing or contains fewer than 10 rows the method returns without making changes. Otherwise it computes the mean of the `verified` column grouped by `regime`, writes the resulting mapping to Python/models/weights_v2.json, executes a database VACUUM, and logs start and completion.
        """
        logging.info("Autonomous Optimization Cycle Started.")
        db_path = f"Python/db/trades_{datetime.now().strftime('%Y%m')}.db"
        if not os.path.exists(db_path): return

        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM signals", conn)

        if len(df) < 10:
            conn.close()
            return

        # Perform weight tuning based on regime performance
        perf = df.groupby('regime')['verified'].mean()
        weights = perf.to_dict()

        with open("Python/models/weights_v2.json", "w") as f:
            json.dump(weights, f)

        conn.execute("VACUUM")
        conn.close()
        logging.info("Maintenance and Weight Optimization Complete.")

if __name__ == "__main__":
    os.makedirs("Python/models", exist_ok=True)
    AutonomousOptimizer().run_weekend_optimization()
