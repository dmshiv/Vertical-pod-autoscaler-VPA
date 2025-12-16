from diagrams import Diagram, Cluster, Edge
from diagrams.k8s.compute import Pod, Deployment
from diagrams.k8s.controlplane import APIServer
from diagrams.k8s.ecosystem import Helm
from diagrams.onprem.monitoring import Prometheus
from diagrams.custom import Custom
import os

# Create custom icons directory if it doesn't exist
os.makedirs("custom_icons", exist_ok=True)

graph_attr = {
    "fontsize": "16",
    "bgcolor": "white",
    "pad": "0.5",
    "ranksep": "1.0",
    "nodesep": "0.8"
}

with Diagram("Kubernetes VPA Architecture", 
             show=False, 
             direction="TB",
             graph_attr=graph_attr,
             filename="vpa_architecture"):
    
    with Cluster("Kubernetes Control Plane"):
        api = APIServer("API Server")
    
    with Cluster("VPA Components (kube-system)"):
        with Cluster("VPA Recommender"):
            recommender = Prometheus("Recommender\n(Analyzes Usage &\nProvides Recommendations)")
        
        with Cluster("VPA Admission Controller"):
            admission = Helm("Admission Controller\n(Intercepts Pod Creation &\nInjects Resources)")
        
        with Cluster("VPA Updater"):
            updater = Helm("Updater\n(Evicts Pods When\nResources Drift)")
    
    with Cluster("Your Namespace"):
        vpa_resource = Helm("VPA Resource\n(nginx-vpa)\nMode: Auto")
        
        with Cluster("Deployment: nginx-vpa-demo"):
            pods = [
                Pod("Pod 1\nCPU: 49m\nMem: 250Mi"),
                Pod("Pod 2\nCPU: 49m\nMem: 250Mi")
            ]
    
    # Metrics flow
    pods[0] >> Edge(label="Usage Metrics", style="dashed", color="blue") >> api
    pods[1] >> Edge(label="Usage Metrics", style="dashed", color="blue") >> api
    
    # Recommender watches metrics
    api >> Edge(label="Watch Metrics", color="green") >> recommender
    
    # Recommender provides recommendations to VPA resource
    recommender >> Edge(label="Target: 25m CPU\n250Mi Memory", color="orange") >> vpa_resource
    
    # VPA resource communicates with API
    vpa_resource >> Edge(label="VPA Status", style="dotted") >> api
    
    # Admission controller intercepts new pods
    api >> Edge(label="New Pod Request", color="purple") >> admission
    admission >> Edge(label="Inject Resources\n(25m CPU, 250Mi Mem)", color="purple") >> api
    
    # Updater evicts pods when needed
    vpa_resource >> Edge(label="Resource Drift\nDetected", color="red", style="dashed") >> updater
    updater >> Edge(label="Evict Pod", color="red") >> api
    api >> Edge(label="Delete Pod", color="red") >> pods[0]
    
    # New pod creation after eviction
    api >> Edge(label="Recreate with\nNew Resources", color="purple", style="bold") >> pods[1]

print("✅ VPA architecture diagram generated: vpa_architecture.png")
