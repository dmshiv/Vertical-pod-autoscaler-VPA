# Vertical Pod Autoscaler (VPA) Demo

## What is VPA?

Vertical Pod Autoscaler (VPA) automatically adjusts CPU and memory requests for your containers based on actual usage patterns. Unlike HPA which scales the number of pods horizontally, VPA scales resources vertically within pods.

## VPA Components

VPA consists of three components working together:

### 1. **vpa-recommender** 
The analyzer that watches your pods and says "Based on what I'm seeing, this container should have X CPU and Y memory"

### 2. **vpa-admission-controller**
The gatekeeper that intercepts new pods being created and injects the recommended resources before they start running

### 3. **vpa-updater**
The enforcer that evicts (kills) existing pods when their current resources are too far off from recommendations, forcing Kubernetes to recreate them with updated values

**Think of it like a restaurant:**
- **Recommender** = Chef analyzing customer appetites and suggesting portion sizes
- **Admission Controller** = Server plating food with the right portions for new customers
- **Updater** = Manager who asks customers to move tables if their current setup isn't working well

## Installation

```bash
# Clone the autoscaler repository
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler

# Install VPA
./hack/vpa-up.sh

# Verify VPA components are running
kubectl get pods -n kube-system | grep vpa
```

Expected output:
```
vpa-admission-controller-795598f856-mbkwv   1/1     Running   0              3m4s
vpa-recommender-5689665744-r8bs7            1/1     Running   0              3m5s
vpa-updater-6cf6bc7ff8-9cl92                1/1     Running   0              3m5s
```

## Demo Setup

1. **Apply the deployment:**
```bash
kubectl apply -f demo-deployment.yaml
```

2. **Apply the VPA resource:**
```bash
kubectl apply -f vpa.yaml
```

3. **Apply the service:**
```bash
kubectl apply -f service.yaml
```

4. **Generate load (optional):**
```bash
kubectl apply -f loadd-gen.yaml
```

## Troubleshooting & Monitoring

### Check VPA Recommendations

```bash
# Watch VPA recommendations in real-time
watch -n 2 'kubectl get vpa nginx-vpa -o yaml | grep -A 20 recommendation'
```

Expected output:
```yaml
recommendation:
    containerRecommendations:
    - containerName: nginx
      lowerBound:
        cpu: 25m
        memory: 250Mi
      target:
        cpu: 25m
        memory: 250Mi
      uncappedTarget:
        cpu: 25m
        memory: 250Mi
      upperBound:
        cpu: 147m
        memory: 250Mi
```

**Understanding the values:**
- **Target**: What VPA thinks your container should have
- **Lower Bound**: Minimum resources needed
- **Upper Bound**: Maximum it might need during peak
- **Uncapped Target**: Target without any policy constraints

### Quick VPA Status Check

```bash
kubectl get vpa nginx-vpa
```

Output:
```
NAME        MODE   CPU   MEM     PROVIDED   AGE
nginx-vpa   Auto   35m   250Mi   True       3h54m
```

### Verify Pod Resources Match VPA Recommendations

```bash
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].resources.requests}'
```

The CPU and memory values should match the VPA target values (e.g., cpu: 35m, memory: 250Mi)

### Monitor All Pods with Resources

```bash
watch -n 1 'kubectl get pods -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,CPU:.spec.containers[*].resources.requests.cpu,MEMORY:.spec.containers[*].resources.requests.memory'
```

Example output:
```
NAME                              STATUS    CPU    MEMORY
load-generator                    Running   100m   64Mi
nginx-vpa-demo-67d7b668f7-2k55n   Running   49m    250Mi
nginx-vpa-demo-67d7b668f7-6pf85   Running   49m    250Mi
```

## 🚨 IMPORTANT: VPA and Resource Limits

### VPA Does NOT Respect Deployment Limits!

If you set limits in your deployment YAML like this:

```yaml
resources:
  requests:
    cpu: 500m
    memory: 256Mi
  limits:
    cpu: 1000m      # VPA ignores this!
    memory: 512Mi   # VPA ignores this!
```

**VPA will:**
- ✅ Modify requests freely (can go above or below your original requests)
- ❌ Ignore limits from your deployment YAML
- ❌ Only respect limits if you set them in the VPA spec itself using `maxAllowed`

**VPA can set resources way above your deployment limits:**

```yaml
requests:
  cpu: 2000m    # Way above your limit of 1000m!
  memory: 1Gi   # Way above your limit of 512Mi!
```

### How to Set Limits for VPA

**❌ Wrong:** Setting limits in deployment YAML (VPA ignores these)

**✅ Correct:** Set `maxAllowed` in the VPA YAML file:

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: nginx-vpa-demo
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: nginx
      maxAllowed:
        cpu: 1000m      # VPA won't go above this
        memory: 512Mi
      minAllowed:
        cpu: 10m        # VPA won't go below this
        memory: 10Mi
```

## VPA Update Modes

- **Auto**: VPA evicts pods when needed and injects new resource recommendations
- **Recreate**: VPA evicts pods to apply new recommendations (same as Auto in practice)
- **Initial**: VPA only sets resources when pods are first created (no eviction)
- **Off**: VPA only provides recommendations, doesn't change anything

## Common Issues

### Pods Not Being Recreated?
VPA doesn't always recreate pods. If pods are already running with VPA-recommended resources (injected by admission controller during creation), there's no need to evict them.

### Multiple Containers Confusing?
If you have sidecars (like Istio), use container-specific commands to check resources:
```bash
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[?(@.name=="nginx")].resources.requests}'
```

### VPA Recommendations Too High/Low?
Adjust the `resourcePolicy` in `vpa.yaml` with `maxAllowed` and `minAllowed` constraints.

## Resources

- [Kubernetes Autoscaler GitHub](https://github.com/kubernetes/autoscaler)
- [VPA Documentation](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
