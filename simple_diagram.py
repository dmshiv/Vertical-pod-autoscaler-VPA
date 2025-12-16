from diagrams import Diagram, Cluster, Edge
from diagrams.k8s.compute import Pod, Deploy
from diagrams.k8s.ecosystem import Helm

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5"
}

with Diagram("HPA vs VPA", 
             show=False, 
             direction="LR",
             graph_attr=graph_attr,
             filename="hpa_vs_vpa_simple"):
    
    with Cluster("HPA\n(Horizontal Pod Autoscaler)\nScales NUMBER of Pods"):
        hpa = Helm("HPA")
        with Cluster("Low Traffic"):
            hpa_before = [Pod("Pod\n1 CPU\n512Mi")]
        
        with Cluster("High Traffic"):
            hpa_after = [
                Pod("Pod\n1 CPU\n512Mi"),
                Pod("Pod\n1 CPU\n512Mi"),
                Pod("Pod\n1 CPU\n512Mi")
            ]
        
        hpa >> Edge(label="Adds More Pods →", color="blue", style="bold") >> hpa_after[0]
    
    with Cluster("VPA\n(Vertical Pod Autoscaler)\nScales RESOURCES per Pod"):
        vpa = Helm("VPA")
        with Cluster("Before"):
            vpa_before = Pod("Pod\n100m CPU\n50Mi")
        
        with Cluster("After"):
            vpa_after = Pod("Pod\n500m CPU\n250Mi")
        
        vpa >> Edge(label="Increases Resources →", color="green", style="bold") >> vpa_after

print("✅ HPA vs VPA diagram generated: hpa_vs_vpa_simple.png")
