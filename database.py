"""SQLite Database Manager for Portfolio ML Predictions"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class PortfolioDB:
    """Manages SQLite database for storing prediction history"""
    
    def __init__(self, db_path: str = "portfolio_predictions.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_db()
    
    def get_connection(self):
        """Get database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def initialize_db(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                risk_score INTEGER,
                cost_variance REAL,
                success_probability REAL,
                priority_score INTEGER,
                model_version TEXT DEFAULT 'v1.0',
                processing_time_ms INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Model accuracy tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_accuracy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                model_name TEXT NOT NULL,
                accuracy REAL NOT NULL,
                predictions_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Portfolio health snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                health_score REAL NOT NULL,
                success_rate REAL NOT NULL,
                avg_risk_score REAL,
                high_risk_count INTEGER,
                total_projects INTEGER,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Activity log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                event_type TEXT NOT NULL,
                project_id TEXT,
                description TEXT,
                severity TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_project 
            ON predictions(project_id, timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
            ON predictions(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_accuracy_timestamp 
            ON model_accuracy(timestamp DESC)
        """)
        
        conn.commit()
        print(f"✅ Database initialized: {self.db_path}")
    
    def store_prediction(self, 
                        project_id: str,
                        risk_score: int,
                        cost_variance: float,
                        success_probability: float = None,
                        priority_score: int = None,
                        processing_time_ms: int = None):
        """Store a new prediction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO predictions 
            (project_id, timestamp, risk_score, cost_variance, 
             success_probability, priority_score, processing_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            datetime.now(),
            risk_score,
            cost_variance,
            success_probability,
            priority_score,
            processing_time_ms
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def store_accuracy(self, model_name: str, accuracy: float, predictions_count: int = 0):
        """Store model accuracy measurement"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO model_accuracy (timestamp, model_name, accuracy, predictions_count)
            VALUES (?, ?, ?, ?)
        """, (datetime.now(), model_name, accuracy, predictions_count))
        
        conn.commit()
        return cursor.lastrowid
    
    def store_portfolio_health(self,
                               health_score: float,
                               success_rate: float,
                               avg_risk_score: float = None,
                               high_risk_count: int = 0,
                               total_projects: int = 0,
                               metadata: dict = None):
        """Store portfolio health snapshot"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO portfolio_health 
            (timestamp, health_score, success_rate, avg_risk_score, 
             high_risk_count, total_projects, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(),
            health_score,
            success_rate,
            avg_risk_score,
            high_risk_count,
            total_projects,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def log_activity(self,
                    event_type: str,
                    description: str,
                    project_id: str = None,
                    severity: str = "INFO",
                    metadata: dict = None):
        """Log an activity event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO activity_log 
            (timestamp, event_type, project_id, description, severity, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(),
            event_type,
            project_id,
            description,
            severity,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_predictions(self, 
                       project_id: str = None,
                       hours: int = 24,
                       limit: int = 100) -> List[Dict]:
        """Get predictions, optionally filtered by project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if project_id:
            cursor.execute("""
                SELECT * FROM predictions
                WHERE project_id = ?
                  AND timestamp > datetime('now', ? || ' hours')
                ORDER BY timestamp DESC
                LIMIT ?
            """, (project_id, -hours, limit))
        else:
            cursor.execute("""
                SELECT * FROM predictions
                WHERE timestamp > datetime('now', ? || ' hours')
                ORDER BY timestamp DESC
                LIMIT ?
            """, (-hours, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_accuracy_history(self, 
                            model_name: str = None,
                            hours: int = 24,
                            limit: int = 100) -> List[Dict]:
        """Get model accuracy history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if model_name:
            cursor.execute("""
                SELECT * FROM model_accuracy
                WHERE model_name = ?
                  AND timestamp > datetime('now', ? || ' hours')
                ORDER BY timestamp DESC
                LIMIT ?
            """, (model_name, -hours, limit))
        else:
            cursor.execute("""
                SELECT * FROM model_accuracy
                WHERE timestamp > datetime('now', ? || ' hours')
                ORDER BY timestamp DESC
                LIMIT ?
            """, (-hours, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_portfolio_health_history(self, hours: int = 24) -> List[Dict]:
        """Get portfolio health snapshots"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM portfolio_health
            WHERE timestamp > datetime('now', ? || ' hours')
            ORDER BY timestamp DESC
        """, (-hours,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_activity_log(self, 
                        project_id: str = None,
                        event_type: str = None,
                        hours: int = 24,
                        limit: int = 50) -> List[Dict]:
        """Get activity log entries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM activity_log WHERE timestamp > datetime('now', ? || ' hours')"
        params = [-hours]
        
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_project_risk_trend(self, project_id: str, days: int = 30) -> List[Dict]:
        """Get risk score trend for a specific project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                timestamp,
                risk_score,
                cost_variance,
                success_probability
            FROM predictions
            WHERE project_id = ?
              AND timestamp > datetime('now', ? || ' days')
            ORDER BY timestamp ASC
        """, (project_id, -days))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Get overall database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total predictions
        cursor.execute("SELECT COUNT(*) as count FROM predictions")
        stats['total_predictions'] = cursor.fetchone()['count']
        
        # Predictions today
        cursor.execute("""
            SELECT COUNT(*) as count FROM predictions
            WHERE DATE(timestamp) = DATE('now')
        """)
        stats['predictions_today'] = cursor.fetchone()['count']
        
        # Unique projects
        cursor.execute("SELECT COUNT(DISTINCT project_id) as count FROM predictions")
        stats['unique_projects'] = cursor.fetchone()['count']
        
        # Average risk score (last 24h)
        cursor.execute("""
            SELECT AVG(risk_score) as avg_risk FROM predictions
            WHERE timestamp > datetime('now', '-24 hours')
        """)
        result = cursor.fetchone()
        stats['avg_risk_24h'] = result['avg_risk'] if result['avg_risk'] else 0
        
        # High risk count (last 24h)
        cursor.execute("""
            SELECT COUNT(*) as count FROM predictions
            WHERE timestamp > datetime('now', '-24 hours')
              AND risk_score > 70
        """)
        stats['high_risk_count_24h'] = cursor.fetchone()['count']
        
        return stats
    
    def cleanup_old_data(self, days: int = 90):
        """Delete data older than specified days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Delete old predictions
        cursor.execute("""
            DELETE FROM predictions
            WHERE timestamp < ?
        """, (cutoff_date,))
        predictions_deleted = cursor.rowcount
        
        # Delete old accuracy records
        cursor.execute("""
            DELETE FROM model_accuracy
            WHERE timestamp < ?
        """, (cutoff_date,))
        accuracy_deleted = cursor.rowcount
        
        # Delete old activity logs
        cursor.execute("""
            DELETE FROM activity_log
            WHERE timestamp < ?
        """, (cutoff_date,))
        activity_deleted = cursor.rowcount
        
        conn.commit()
        
        return {
            'predictions_deleted': predictions_deleted,
            'accuracy_deleted': accuracy_deleted,
            'activity_deleted': activity_deleted
        }
    
    def export_to_csv(self, table_name: str, output_file: str):
        """Export table data to CSV"""
        import csv
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No data to export from {table_name}")
            return
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([description[0] for description in cursor.description])
            # Write data
            writer.writerows(rows)
        
        print(f"✅ Exported {len(rows)} rows to {output_file}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

# Convenience functions
def get_db(db_path: str = "portfolio_predictions.db") -> PortfolioDB:
    """Get database instance"""
    return PortfolioDB(db_path)

if __name__ == "__main__":
    # Test the database
    db = PortfolioDB("test_portfolio.db")
    
    print("\n📊 Testing Database Operations...")
    
    # Store some test data
    print("\n1. Storing predictions...")
    for i in range(5):
        db.store_prediction(
            project_id=f"PROJ-{i:03d}",
            risk_score=50 + i * 10,
            cost_variance=5.0 + i * 2,
            success_probability=0.7 + i * 0.05,
            priority_score=70 + i * 5
        )
    
    # Store accuracy
    print("2. Storing accuracy...")
    db.store_accuracy("PRM", 89.5, 150)
    db.store_accuracy("COP", 82.3, 150)
    
    # Store portfolio health
    print("3. Storing portfolio health...")
    db.store_portfolio_health(
        health_score=85.0,
        success_rate=87.5,
        avg_risk_score=55.0,
        high_risk_count=12,
        total_projects=50
    )
    
    # Log activity
    print("4. Logging activity...")
    db.log_activity(
        event_type="RISK_ALERT",
        description="High risk detected",
        project_id="PROJ-001",
        severity="HIGH"
    )
    
    # Query data
    print("\n5. Querying data...")
    predictions = db.get_predictions(limit=5)
    print(f"   Found {len(predictions)} predictions")
    
    # Get statistics
    print("\n6. Database statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Database test completed!")
    
    db.close()
