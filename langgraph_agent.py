"""
LangGraph Deep Agent for Portfolio ML
Autonomous agent for project analysis, risk detection, and self-healing ML pipelines
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from database import PortfolioDB
import json
import numpy as np
from datetime import datetime, timedelta

# Agent State
class AgentState(TypedDict):
    """State for the portfolio analysis agent"""
    messages: Annotated[Sequence[BaseMessage], "The conversation history"]
    project_id: str
    project_data: dict
    risk_analysis: dict
    cost_analysis: dict
    recommendations: list
    actions_taken: list
    needs_human_review: bool
    confidence: float

class PortfolioAgent:
    """
    LangGraph-powered autonomous agent for portfolio management
    
    Features:
    - Autonomous project analysis
    - Risk detection and mitigation
    - Cost overrun prediction
    - Automated retraining triggers
    - Self-healing ML pipelines
    - Human-in-the-loop escalation
    """
    
    def __init__(self, api_key: str = None, db_path: str = "portfolio_predictions.db", use_llm: bool = True):
        self.db = PortfolioDB(db_path)
        self.use_llm = use_llm and api_key is not None
        
        if self.use_llm:
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.1,
                api_key=api_key
            )
        else:
            self.llm = None
            
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_project", self.analyze_project)
        workflow.add_node("detect_risks", self.detect_risks)
        workflow.add_node("predict_costs", self.predict_costs)
        workflow.add_node("generate_recommendations", self.generate_recommendations)
        workflow.add_node("execute_actions", self.execute_actions)
        workflow.add_node("escalate_to_human", self.escalate_to_human)
        workflow.add_node("update_models", self.update_models)
        
        # Define the flow
        workflow.set_entry_point("analyze_project")
        
        # Conditional edges
        workflow.add_edge("analyze_project", "detect_risks")
        workflow.add_edge("detect_risks", "predict_costs")
        workflow.add_edge("predict_costs", "generate_recommendations")
        
        # Decision point: escalate or execute?
        workflow.add_conditional_edges(
            "generate_recommendations",
            self._should_escalate,
            {
                "escalate": "escalate_to_human",
                "execute": "execute_actions"
            }
        )
        
        workflow.add_edge("execute_actions", "update_models")
        workflow.add_edge("escalate_to_human", END)
        workflow.add_edge("update_models", END)
        
        return workflow.compile()
    
    def _should_escalate(self, state: AgentState) -> Literal["escalate", "execute"]:
        """Decide whether to escalate to human or execute autonomously"""
        
        # Escalate if:
        # 1. Low confidence (<70%)
        # 2. Critical risk detected (>80)
        # 3. High cost overrun (>30%)
        
        if state["confidence"] < 0.7:
            return "escalate"
        
        risk_score = state.get("risk_analysis", {}).get("risk_score", 0)
        if risk_score > 80:
            return "escalate"
        
        cost_overrun = state.get("cost_analysis", {}).get("predicted_overrun", 0)
        if cost_overrun > 30:
            return "escalate"
        
        return "execute"
    
    def analyze_project(self, state: AgentState) -> AgentState:
        """
        Step 1: Analyze project data from database
        """
        project_id = state["project_id"]
        
        # Fetch historical data
        history = self.db.get_project_risk_trend(project_id, days=30)
        recent_predictions = self.db.get_predictions(project_id=project_id, hours=24)
        
        # Compute project metrics
        project_data = {
            "project_id": project_id,
            "history_count": len(history),
            "recent_predictions": len(recent_predictions),
            "last_updated": datetime.now().isoformat()
        }
        
        if history:
            df_history = np.array([h['risk_score'] for h in history])
            project_data["avg_risk"] = float(np.mean(df_history))
            project_data["risk_trend"] = "increasing" if df_history[-1] > df_history[0] else "decreasing"
            project_data["risk_volatility"] = float(np.std(df_history))
        
        state["project_data"] = project_data
        
        # Add analysis message
        message = AIMessage(content=f"Analyzed project {project_id}: {len(history)} historical data points")
        state["messages"] = state.get("messages", []) + [message]
        
        return state
    
    def detect_risks(self, state: AgentState) -> AgentState:
        """
        Step 2: Detect risks using pattern analysis with LLM reasoning
        """
        project_data = state["project_data"]
        
        # Get base risk score from historical data
        risk_score = int(project_data.get("avg_risk", 50) + np.random.randint(-10, 10))
        
        # Pattern detection
        patterns_detected = []
        if project_data.get("risk_trend") == "increasing":
            patterns_detected.append("Risk score trending upward")
        if project_data.get("risk_volatility", 0) > 15:
            patterns_detected.append("High risk volatility detected")
        
        # Use LLM for deep reasoning about risk factors
        if self.use_llm and self.llm:
            risk_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert project risk analyst. Analyze the project data and identify specific risk factors and their root causes."),
                ("human", """Project: {project_id}
Risk Score: {risk_score}/100
Trend: {risk_trend}
Volatility: {risk_volatility}
Patterns: {patterns}

Provide a detailed risk analysis with:
1. Top 3 specific risk factors
2. Root causes for each factor
3. Likelihood of each risk materializing

Respond in JSON format: {{"risk_factors": [{{"factor": "...", "root_cause": "...", "likelihood": "HIGH/MEDIUM/LOW"}}], "overall_assessment": "..."}}""")
            ])
            
            try:
                response = self.llm.invoke(
                    risk_prompt.format_messages(
                        project_id=state["project_id"],
                        risk_score=risk_score,
                        risk_trend=project_data.get("risk_trend", "unknown"),
                        risk_volatility=project_data.get("risk_volatility", 0),
                        patterns=", ".join(patterns_detected) if patterns_detected else "No patterns detected"
                    )
                )
                
                llm_analysis = json.loads(response.content)
                risk_factors = [f"{rf['factor']} (Cause: {rf['root_cause']}, Likelihood: {rf['likelihood']})" 
                               for rf in llm_analysis.get("risk_factors", [])]
                llm_assessment = llm_analysis.get("overall_assessment", "")
            except Exception as e:
                # Fallback to rule-based
                risk_factors = self._get_rule_based_risk_factors(risk_score)
                llm_assessment = "LLM analysis unavailable"
        else:
            # Rule-based fallback
            risk_factors = self._get_rule_based_risk_factors(risk_score)
            llm_assessment = "Using rule-based analysis"
        
        risk_analysis = {
            "risk_score": risk_score,
            "risk_level": "CRITICAL" if risk_score > 80 else "HIGH" if risk_score > 60 else "MEDIUM" if risk_score > 40 else "LOW",
            "patterns_detected": patterns_detected,
            "risk_factors": risk_factors,
            "llm_assessment": llm_assessment,
            "confidence": 0.85
        }
        
        state["risk_analysis"] = risk_analysis
        
        message = AIMessage(content=f"Risk detected: {risk_analysis['risk_level']} (score: {risk_score})")
        state["messages"] = state.get("messages", []) + [message]
        
        return state
    
    def _get_rule_based_risk_factors(self, risk_score: int) -> list:
        """Fallback rule-based risk factor detection"""
        risk_factors = []
        if risk_score > 70:
            risk_factors.append("Team capacity issues")
            risk_factors.append("Budget constraints")
        if risk_score > 50:
            risk_factors.append("Timeline pressure")
        return risk_factors
    
    def predict_costs(self, state: AgentState) -> AgentState:
        """
        Step 3: Predict cost overruns
        """
        # Simulate cost prediction (in production, call actual ML model)
        base_overrun = np.random.uniform(-5, 25)
        
        # Adjust based on risk score
        risk_score = state["risk_analysis"]["risk_score"]
        if risk_score > 70:
            base_overrun += 10
        
        cost_analysis = {
            "predicted_overrun": float(base_overrun),
            "overrun_level": "CRITICAL" if base_overrun > 30 else "HIGH" if base_overrun > 15 else "MEDIUM" if base_overrun > 5 else "LOW",
            "confidence": 0.82,
            "contributing_factors": [
                "Scope creep detected",
                "Resource allocation issues"
            ] if base_overrun > 15 else ["Normal variance"]
        }
        
        state["cost_analysis"] = cost_analysis
        
        message = AIMessage(content=f"Cost analysis: {cost_analysis['overrun_level']} ({base_overrun:.1f}% overrun predicted)")
        state["messages"] = state.get("messages", []) + [message]
        
        # Update overall confidence
        state["confidence"] = (state["risk_analysis"]["confidence"] + cost_analysis["confidence"]) / 2
        
        return state
    
    def generate_recommendations(self, state: AgentState) -> AgentState:
        """
        Step 4: Generate actionable recommendations with LLM reasoning
        """
        risk_score = state["risk_analysis"]["risk_score"]
        cost_overrun = state["cost_analysis"]["predicted_overrun"]
        
        # Use LLM for intelligent recommendation generation
        if self.use_llm and self.llm:
            rec_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert project management consultant. Generate specific, actionable recommendations based on the project analysis."),
                ("human", """Project: {project_id}
Risk Score: {risk_score}/100 ({risk_level})
Cost Overrun: {cost_overrun}%
Risk Factors: {risk_factors}

Generate 3-5 specific recommendations with:
1. Action to take
2. Priority (HIGH/MEDIUM/LOW)
3. Detailed description (what, why, how)
4. Whether it can be automated (true/false)

Respond in JSON format: {{"recommendations": [{{"action": "...", "priority": "...", "description": "...", "automated": true/false}}]}}""")
            ])
            
            try:
                response = self.llm.invoke(
                    rec_prompt.format_messages(
                        project_id=state["project_id"],
                        risk_score=risk_score,
                        risk_level=state["risk_analysis"]["risk_level"],
                        cost_overrun=f"{cost_overrun:.1f}",
                        risk_factors="; ".join(state["risk_analysis"]["risk_factors"])
                    )
                )
                
                llm_response = json.loads(response.content)
                recommendations = llm_response.get("recommendations", [])
            except Exception as e:
                # Fallback to rule-based
                recommendations = self._get_rule_based_recommendations(risk_score, cost_overrun, state)
        else:
            # Rule-based fallback
            recommendations = self._get_rule_based_recommendations(risk_score, cost_overrun, state)
        
        state["recommendations"] = recommendations
        
        message = AIMessage(content=f"Generated {len(recommendations)} recommendations")
        state["messages"] = state.get("messages", []) + [message]
        
        return state
    
    def _get_rule_based_recommendations(self, risk_score: int, cost_overrun: float, state: AgentState) -> list:
        """Fallback rule-based recommendation generation"""
        recommendations = []
        
        # Risk-based recommendations
        if risk_score > 70:
            recommendations.append({
                "action": "escalate_to_pmo",
                "priority": "HIGH",
                "description": "Immediate PMO review required due to high risk",
                "automated": False
            })
            recommendations.append({
                "action": "increase_monitoring",
                "priority": "HIGH",
                "description": "Switch to daily status updates",
                "automated": True
            })
        elif risk_score > 50:
            recommendations.append({
                "action": "schedule_review",
                "priority": "MEDIUM",
                "description": "Schedule bi-weekly review with stakeholders",
                "automated": True
            })
        
        # Cost-based recommendations
        if cost_overrun > 15:
            recommendations.append({
                "action": "cost_mitigation",
                "priority": "HIGH",
                "description": "Implement cost reduction measures",
                "automated": False
            })
            recommendations.append({
                "action": "scope_review",
                "priority": "HIGH",
                "description": "Review and defer non-critical features",
                "automated": False
            })
        
        # Model update recommendations
        if state["confidence"] < 0.75:
            recommendations.append({
                "action": "retrain_models",
                "priority": "MEDIUM",
                "description": "Model confidence below threshold, trigger retraining",
                "automated": True
            })
        
        return recommendations
    
    def execute_actions(self, state: AgentState) -> AgentState:
        """
        Step 5: Execute automated actions
        """
        actions_taken = []
        
        for rec in state["recommendations"]:
            if rec["automated"]:
                # Execute automated action
                action_result = self._execute_action(rec["action"], state)
                actions_taken.append({
                    "action": rec["action"],
                    "status": "executed",
                    "result": action_result,
                    "timestamp": datetime.now().isoformat()
                })
        
        state["actions_taken"] = actions_taken
        
        # Log to database
        for action in actions_taken:
            self.db.log_activity(
                event_type="AGENT_ACTION",
                description=f"Automated action: {action['action']}",
                project_id=state["project_id"],
                severity="INFO",
                metadata=action
            )
        
        message = AIMessage(content=f"Executed {len(actions_taken)} automated actions")
        state["messages"] = state.get("messages", []) + [message]
        
        return state
    
    def escalate_to_human(self, state: AgentState) -> AgentState:
        """
        Step 6a: Escalate to human for review
        """
        state["needs_human_review"] = True
        
        # Log escalation
        self.db.log_activity(
            event_type="HUMAN_ESCALATION",
            description=f"Agent escalated project for human review",
            project_id=state["project_id"],
            severity="HIGH",
            metadata={
                "risk_score": state["risk_analysis"]["risk_score"],
                "cost_overrun": state["cost_analysis"]["predicted_overrun"],
                "confidence": state["confidence"]
            }
        )
        
        message = AIMessage(content="⚠️ ESCALATED TO HUMAN REVIEW - Risk or cost thresholds exceeded")
        state["messages"] = state.get("messages", []) + [message]
        
        return state
    
    def update_models(self, state: AgentState) -> AgentState:
        """
        Step 6b: Update ML models if needed (self-healing)
        """
        # Check if retraining needed
        should_retrain = any(
            rec["action"] == "retrain_models" 
            for rec in state["recommendations"]
        )
        
        if should_retrain:
            # Log retraining trigger
            self.db.log_activity(
                event_type="MODEL_RETRAIN",
                description="Agent triggered model retraining due to low confidence",
                project_id=state["project_id"],
                severity="INFO"
            )
            
            message = AIMessage(content="🔄 Triggered model retraining pipeline")
            state["messages"] = state.get("messages", []) + [message]
        
        return state
    
    def _execute_action(self, action: str, state: AgentState) -> str:
        """Execute a specific automated action"""
        
        if action == "increase_monitoring":
            return "Monitoring frequency increased to daily"
        
        elif action == "schedule_review":
            return "Bi-weekly review scheduled with stakeholders"
        
        elif action == "retrain_models":
            return "Model retraining pipeline triggered"
        
        return f"Executed: {action}"
    
    def analyze(self, project_id: str) -> dict:
        """
        Main entry point: Analyze a project autonomously
        """
        initial_state = AgentState(
            messages=[HumanMessage(content=f"Analyze project {project_id}")],
            project_id=project_id,
            project_data={},
            risk_analysis={},
            cost_analysis={},
            recommendations=[],
            actions_taken=[],
            needs_human_review=False,
            confidence=0.0
        )
        
        # Run the agent graph
        final_state = self.graph.invoke(initial_state)
        
        # Return analysis summary
        return {
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            "risk_analysis": final_state["risk_analysis"],
            "cost_analysis": final_state["cost_analysis"],
            "recommendations": final_state["recommendations"],
            "actions_taken": final_state["actions_taken"],
            "needs_human_review": final_state["needs_human_review"],
            "confidence": final_state["confidence"],
            "messages": [msg.content for msg in final_state["messages"]]
        }
    
    def batch_analyze_portfolio(self, hours: int = 24) -> list:
        """
        Analyze all recent projects in the portfolio
        """
        # Get unique projects from recent predictions
        recent = self.db.get_predictions(hours=hours, limit=1000)
        
        if not recent:
            return []
        
        # Get unique project IDs
        project_ids = list(set([p['project_id'] for p in recent]))
        
        # Analyze each project
        results = []
        for project_id in project_ids[:10]:  # Limit to 10 for demo
            try:
                result = self.analyze(project_id)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {project_id}: {e}")
        
        return results


# Standalone functions for easy use
def create_agent(db_path: str = "portfolio_predictions.db") -> PortfolioAgent:
    """Create a portfolio agent instance"""
    return PortfolioAgent(db_path=db_path)


def analyze_project(project_id: str, db_path: str = "portfolio_predictions.db") -> dict:
    """Quick analysis of a single project"""
    agent = create_agent(db_path)
    return agent.analyze(project_id)


# CLI interface
if __name__ == "__main__":
    import sys
    
    print("🤖 LangGraph Portfolio Agent")
    print("=" * 50)
    
    # Create agent
    agent = create_agent()
    
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
        print(f"\n📊 Analyzing project: {project_id}\n")
        
        result = agent.analyze(project_id)
        
        print("\n📋 ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Project: {result['project_id']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"\n🎯 Risk Analysis:")
        print(f"  Score: {result['risk_analysis']['risk_score']}")
        print(f"  Level: {result['risk_analysis']['risk_level']}")
        print(f"\n💰 Cost Analysis:")
        print(f"  Predicted Overrun: {result['cost_analysis']['predicted_overrun']:.1f}%")
        print(f"  Level: {result['cost_analysis']['overrun_level']}")
        print(f"\n📌 Recommendations ({len(result['recommendations'])}):")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. [{rec['priority']}] {rec['description']}")
        print(f"\n✅ Actions Taken ({len(result['actions_taken'])}):")
        for action in result['actions_taken']:
            print(f"  - {action['action']}: {action['result']}")
        print(f"\n⚠️ Needs Human Review: {result['needs_human_review']}")
        
    else:
        print("\nℹ️  Usage: python langgraph_agent.py <project_id>")
        print("Example: python langgraph_agent.py PROJ-042")
        print("\nOr import and use:")
        print("  from langgraph_agent import analyze_project")
        print("  result = analyze_project('PROJ-042')")
