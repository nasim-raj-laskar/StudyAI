# StudyAI: GenAI-Powered Educational Infrastructure 📚

StudyAI is a cloud-native platform engineered to automate the ingestion and synthesis of educational content. Built on a modular architecture, the system utilizes Large Language Models (LLMs) to perform content summarization, flashcard extraction, and dynamic evaluation generation.

---

## 🏗️ Technical Architecture

### Cloud Ecosystem (AWS)

The infrastructure is provisioned as Immutable Infrastructure via Terraform, deployed within a highly available VPC architecture in the `ap-south-1` region.

```mermaid
graph TD
    %% Define Nodes
    User([External User])
    IGW[Internet Gateway]
    ALB[Application Load Balancer]
    NAT[NAT Gateway]

    subgraph VPC [AWS VPC: 10.0.0.0/16]
        subgraph PublicSubnets [Public Subnets]
            ALB
            IGW
        end

        subgraph PrivateSubnets [Private Subnets]
            NAT
            subgraph EKS [EKS Cluster: study-cluster]
                direction TB
                subgraph NodeGroup [Managed Node Group: SPOT]
                    Node1[t3.micro Node]
                    Node2[t3.micro Node]

                    subgraph K8sPods [Kubernetes Pods]
                        Pod1[study-app Deployment]
                        Pod2[study-app Deployment]
                    end
                end
            end
        end

        ECR[(Amazon ECR)]
    end

    %% Define Flows
    User --> IGW
    IGW --> ALB
    ALB --> Pod1
    ALB --> Pod2
    Pod1 & Pod2 -- Egress via NAT --> GroqAPI[[Groq Cloud API]]
    ECR -- Image Pull --> NodeGroup
```

### CI/CD Pipeline Logic

The deployment workflow implements an automated build-test-deploy cycle triggered by VCS events.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GHA as GitHub Actions
    participant ECR as AWS ECR
    participant EKS as AWS EKS

    Dev->>GHA: Git Push (main branch)

    rect rgb(255, 255, 255)
        Note right of GHA: Pipeline Stage: Build & Unit Test
        GHA->>GHA: Pytest / Flake8 Validation
    end

    rect rgb(255, 255, 255)
        Note right of GHA: Pipeline Stage: Containerization
        GHA->>ECR: Docker Login
        GHA->>GHA: Docker Build (multistage)
        GHA->>ECR: Push Image (SHA tag + latest)
    end

    rect rgb(255, 255, 255)
        Note right of GHA: Pipeline Stage: K8s Orchestration
        GHA->>EKS: Update Kubeconfig
        GHA->>EKS: patch image deployment/study-app
        GHA->>EKS: rollout status --timeout=5m
    end

    EKS-->>Dev: Cluster State Updated
```

---

## 🛠️ System Components

### 1. Application Layer (Frontend & Proxy)

- **Framework**: Streamlit (Python-based reactive UI)
- **Containerization**: Docker (Alpine/Slim base images for optimized footprint)
- **Connectivity**: Service exposure via AWS Load Balancer Controller (ALB)

### 2. GenAI Tier (Orchestration & Inference)

- **Orchestration**: LangChain (Chains for Summarization, Flashcard extraction, and Quiz generation)
- **Inference Engine**: Llama-3 (70B/8B Parameter Models) via Groq Cloud for low-latency inference.
- **Data Ingestion**: PyPDF2 for structured document parsing and text extraction.

### 3. Infrastructure Tier (IaC & Orchestration)

- **Provisioning**: Terraform utilizing official `terraform-aws-modules` (VPC, EKS).
- **Orchestration**: Amazon EKS (Kubernetes 1.29) with managed node groups.
- **Networking**: Dual-subnet topology (Public/Private), NAT Gateway for secure egress.
- **Compute**: Spot Capacity (`t3.micro`) to optimize cost in dev environments.

---

## ⚙️ Configuration & Deployment

### Local Development Runtime

1. **Environment Configuration**:

   ```bash
   cat <<EOF > .env
   GROQ_API_KEY=your_api_key
   EOF
   ```

2. **Dependency Management**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Execution**:
   ```bash
   streamlit run app.py
   ```

### Infrastructure Provisioning

```bash
cd terraform
terraform init
terraform apply -auto-approve
```

### GitOps Workflow

The system relies on GitHub Actions (`.github/workflows/deploy.yml`) for continuous deployment. Required secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

---

## 📈 Monitoring & Scalability

- **Horizontal Pod Autoscaling**: Configured via Kubernetes manifests.
- **Rollout Strategy**: `Recreate` strategy utilized for resource-constrained (Free Tier) environments to prevent deployment deadlocks.
- **Observability**: Integration with CloudWatch Container Insights planned for production metrics.
