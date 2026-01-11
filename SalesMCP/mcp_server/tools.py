import json
from datetime import date

class MCPTools:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_sales_pipeline_summary(self):
        """Returns a high-level summary of the entire sales pipeline."""
        sql = """
            SELECT stage, COUNT(*) as count, SUM(deal_value) as total_value 
            FROM deals 
            GROUP BY stage
        """
        results = self.db.query(sql)
        return {
            "summary": results,
            "metadata": {"data_source": "deals", "timestamp": str(date.today())}
        }

    def get_deals_by_owner(self, owner_name):
        """Returns all deals owned by a specific sales representative."""
        sql = """
            SELECT d.id, c.name as customer_name, d.deal_value, d.stage, d.probability, d.expected_close_date
            FROM deals d
            JOIN users u ON d.owner_id = u.id
            JOIN customers c ON d.customer_id = c.id
            WHERE u.name ILIKE %s
        """
        results = self.db.query(sql, (f"%{owner_name}%",))
        return {
            "owner": owner_name,
            "deals": results,
            "metadata": {"query_param": owner_name}
        }

    def get_customer_profile(self, customer_id):
        """Returns detailed information about a customer and their relationship health."""
        sql = """
            SELECT * FROM customers WHERE id = %s
        """
        customer = self.db.query(sql, (customer_id,))
        if not customer:
            return {"error": "Customer not found"}
        
        # Get recent activities
        activities = self.db.query(
            "SELECT * FROM activities a JOIN deals d ON a.deal_id = d.id WHERE d.customer_id = %s ORDER BY activity_date DESC LIMIT 5",
            (customer_id,)
        )
        
        return {
            "profile": customer[0],
            "recent_activities": activities,
            "metadata": {"customer_id": customer_id}
        }

    def get_stalled_deals(self):
        """Identifies deals that haven't had activity in over 7 days."""
        sql = """
            SELECT d.id, c.name as customer_name, d.deal_value, d.last_activity
            FROM deals d
            JOIN customers c ON d.customer_id = c.id
            WHERE d.last_activity < CURRENT_DATE - INTERVAL '7 days'
            AND d.stage NOT IN ('Closed Won', 'Closed Lost')
        """
        results = self.db.query(sql)
        return {
            "stalled_deals": results,
            "metadata": {"criteria": "no activity > 7 days"}
        }

    def evaluate_deal_risk(self, deal_id):
        """Reasoning capability: Assesses if a deal is at risk based on customer health and probability."""
        sql = """
            SELECT d.*, c.risk_score as customer_risk
            FROM deals d
            JOIN customers c ON d.customer_id = c.id
            WHERE d.id = %s
        """
        deal = self.db.query(sql, (deal_id,))
        if not deal:
            return {"error": "Deal not found"}
        
        deal_data = deal[0]
        is_risky = deal_data['customer_risk'] > 0.6 or (deal_data['probability'] < 0.3 and deal_data['stage'] == 'Closing')
        
        return {
            "deal_id": deal_id,
            "risk_assessment": "High Risk" if is_risky else "Healthy",
            "reasoning": "Determined by customer risk score and deal progression probability.",
            "evidence": deal_data,
            "metadata": {"logic": "risk_thresholds_v1"}
        }

    def prioritize_deals_for_today(self, owner_id):
        """Reasoning capability: Suggests which deals to focus on based on value and closing date."""
        sql = """
            SELECT d.id, c.name as customer_name, d.deal_value, d.expected_close_date
            FROM deals d
            JOIN customers c ON d.customer_id = c.id
            WHERE d.owner_id = %s AND d.stage NOT IN ('Closed Won', 'Closed Lost')
            ORDER BY d.deal_value DESC, d.expected_close_date ASC
            LIMIT 3
        """
        results = self.db.query(sql, (owner_id,))
        return {
            "priorities": results,
            "reasoning": "Prioritized by highest value and nearest close date.",
            "metadata": {"owner_id": owner_id}
        }

    def check_sales_policy(self, policy_name):
        """Policy capability: Returns the rule for a specific sales policy."""
        result = self.db.query("SELECT rule FROM policies WHERE policy_name ILIKE %s", (f"%{policy_name}%",))
        return {
            "policy": policy_name,
            "rule": result[0]['rule'] if result else "Policy not found",
            "metadata": {"source": "policies_table"}
        }

    def log_agent_decision(self, data):
        """Write capability: Logs an agent's reasoning into the audit table."""
        sql = """
            INSERT INTO agent_decisions (agent_name, input_question, recommendation, confidence, evidence)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        res = self.db.query(sql, (
            data.get('agent_name'),
            data.get('input_question'),
            data.get('recommendation'),
            data.get('confidence'),
            json.dumps(data.get('evidence'))
        ))
        return {"status": "success", "decision_id": res[0]['id']}
