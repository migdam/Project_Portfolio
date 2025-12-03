"""
Data Lineage Tracking
Track data flow from source to predictions for compliance
"""
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class LineageNode:
    """Represents a node in the data lineage graph"""
    node_id: str
    node_type: str  # source, transformation, model, prediction
    name: str
    timestamp: str
    metadata: Dict
    inputs: List[str]  # IDs of input nodes


class DataLineageTracker:
    """Tracks end-to-end data lineage"""
    
    def __init__(self, storage_path: str = "data/lineage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.lineage_graph: Dict[str, LineageNode] = {}
    
    def record_data_source(
        self,
        source_id: str,
        source_name: str,
        source_type: str,
        metadata: Dict = None
    ) -> str:
        """Record data source"""
        node = LineageNode(
            node_id=source_id,
            node_type="source",
            name=source_name,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata or {"type": source_type},
            inputs=[]
        )
        self.lineage_graph[source_id] = node
        self._persist_node(node)
        return source_id
    
    def record_transformation(
        self,
        transformation_id: str,
        transformation_name: str,
        input_ids: List[str],
        transformation_code: str = None,
        metadata: Dict = None
    ) -> str:
        """Record data transformation"""
        node = LineageNode(
            node_id=transformation_id,
            node_type="transformation",
            name=transformation_name,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata or {"code": transformation_code},
            inputs=input_ids
        )
        self.lineage_graph[transformation_id] = node
        self._persist_node(node)
        return transformation_id
    
    def record_model_training(
        self,
        model_id: str,
        model_name: str,
        training_data_ids: List[str],
        hyperparameters: Dict,
        metrics: Dict
    ) -> str:
        """Record model training event"""
        node = LineageNode(
            node_id=model_id,
            node_type="model",
            name=model_name,
            timestamp=datetime.utcnow().isoformat(),
            metadata={
                "hyperparameters": hyperparameters,
                "metrics": metrics
            },
            inputs=training_data_ids
        )
        self.lineage_graph[model_id] = node
        self._persist_node(node)
        return model_id
    
    def record_prediction(
        self,
        prediction_id: str,
        model_id: str,
        input_data_id: str,
        prediction_value: float,
        confidence: float
    ) -> str:
        """Record prediction event"""
        node = LineageNode(
            node_id=prediction_id,
            node_type="prediction",
            name=f"prediction_{prediction_id}",
            timestamp=datetime.utcnow().isoformat(),
            metadata={
                "prediction_value": prediction_value,
                "confidence": confidence
            },
            inputs=[model_id, input_data_id]
        )
        self.lineage_graph[prediction_id] = node
        self._persist_node(node)
        return prediction_id
    
    def get_lineage(self, node_id: str) -> Dict:
        """Get full lineage for a node"""
        if node_id not in self.lineage_graph:
            return None
        
        lineage = {"node": asdict(self.lineage_graph[node_id]), "ancestors": []}
        
        # Recursively get ancestors
        def get_ancestors(nid):
            node = self.lineage_graph.get(nid)
            if not node:
                return []
            ancestors = []
            for input_id in node.inputs:
                ancestors.append(asdict(self.lineage_graph[input_id]))
                ancestors.extend(get_ancestors(input_id))
            return ancestors
        
        lineage["ancestors"] = get_ancestors(node_id)
        return lineage
    
    def _persist_node(self, node: LineageNode):
        """Persist lineage node to disk"""
        date_str = datetime.utcnow().strftime("%Y%m%d")
        lineage_file = self.storage_path / f"lineage_{date_str}.jsonl"
        with open(lineage_file, 'a') as f:
            f.write(json.dumps(asdict(node)) + '\\n')
