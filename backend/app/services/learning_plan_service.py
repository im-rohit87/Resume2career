from typing import List, Dict, Any


class LearningPlanService:
    @classmethod
    def generate_plan(
        cls,
        duration_days: int,
        target_role: str,
        missing_skills: List[str] = None,
        weak_rubrics: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Generates a structured, actionable day-by-day learning plan."""
        if missing_skills is None:
            missing_skills = []
        if weak_rubrics is None:
            weak_rubrics = []

        # If no missing skills specified, use standard core competencies for the role
        if not missing_skills:
            if "frontend" in target_role.lower():
                missing_skills = ["TypeScript", "State Management", "Performance Optimization", "Web Accessibility", "Testing"]
            elif "data" in target_role.lower() or "ml" in target_role.lower():
                missing_skills = ["Data Pipelines", "SQL Optimization", "Model Evaluation", "Docker", "Feature Engineering"]
            else:
                missing_skills = ["FastAPI/Django", "PostgreSQL Indexing", "Docker Containers", "System Design", "Redis Caching"]

        milestones: List[Dict[str, Any]] = []

        # Curriculum blueprint modules
        core_curriculum = [
            {
                "topic": "Core Fundamentals & Architectural Patterns",
                "objectives": [
                    "Review memory management and execution lifecycle",
                    "Understand synchronous vs asynchronous concurrency trade-offs",
                    "Design clean separation of concerns using clean architecture layers"
                ],
                "challenge": "Refactor a monolithic script into modular controller-service-repository patterns with unit tests.",
                "resources": ["Mozilla Developer Network (MDN)", "FastAPI / Django Official Documentation"]
            },
            {
                "topic": "Data Modeling, Indexing & Query Optimization",
                "objectives": [
                    "Master B-tree vs Hash indexing mechanics",
                    "Analyze query execution plans using EXPLAIN ANALYZE",
                    "Prevent N+1 query antipatterns with eager loading"
                ],
                "challenge": "Write a schema migration adding compound indexes on a 100k-row table and measure query latency drop.",
                "resources": ["Use The Index, Luke (Guide to Database Performance)", "PostgreSQL Documentation"]
            },
            {
                "topic": "API Design & Resilient Client Communication",
                "objectives": [
                    "Design idempotent RESTful endpoints and HTTP status contracts",
                    "Implement rate limiting, backoff retries, and circuit breakers",
                    "Secure APIs with JWT expiration, refresh rotation, and CORS"
                ],
                "challenge": "Build a secure endpoint with token validation, payload validation, and custom exception middleware.",
                "resources": ["RESTful API Guidelines (Zalando / GitHub)", "RFC 7519 JWT Specification"]
            },
            {
                "topic": "Caching Strategies & Performance Tuning",
                "objectives": [
                    "Implement Cache-Aside vs Write-Through patterns with Redis",
                    "Establish TTL policies to eliminate stale cache reads",
                    "Mitigate cache stampede and avalanche risks"
                ],
                "challenge": "Deploy a Redis cache decorator caching repeated expensive database aggregations.",
                "resources": ["Redis University Free Courses", "System Design Primer Caching Guide"]
            },
            {
                "topic": "Containerization, Microservices & CI/CD",
                "objectives": [
                    "Build minimal, secure multi-stage Dockerfiles",
                    "Configure Docker Compose for full-stack local orchestration",
                    "Automate testing and linting pipelines with GitHub Actions"
                ],
                "challenge": "Create a multi-stage Docker build reducing an image footprint to under 120MB with zero root vulnerabilities.",
                "resources": ["Docker Official Best Practices", "GitHub Actions Documentation"]
            },
            {
                "topic": "System Design: Scalability & High Availability",
                "objectives": [
                    "Estimate capacity (QPS, storage, bandwidth)",
                    "Select appropriate load balancing algorithms (Round Robin, Least Connections)",
                    "Design for eventual consistency and partition tolerance (CAP Theorem)"
                ],
                "challenge": "Whiteboard an end-to-end distributed notifications service delivering 100k push messages/sec.",
                "resources": ["System Design Primer by Donne Martin", "Designing Data-Intensive Applications (DDIA Notes)"]
            },
            {
                "topic": "Mock Interview Simulation & Behavioral Mastery",
                "objectives": [
                    "Master STAR storytelling for conflict, ownership, and failure scenarios",
                    "Practice verbalizing technical trade-offs before typing code",
                    "Prepare 5 insightful questions to ask the hiring engineering team"
                ],
                "challenge": "Complete a full 5-question Adaptive Mock Interview on Resume2Interview AI with audio or typed timer enabled.",
                "resources": ["Resume2Interview AI Mock Interview Hub", "Pragmatic Engineer Interview Guide"]
            }
        ]

        # Interpolate based on requested duration (7, 15, or 30 days)
        for day in range(1, duration_days + 1):
            curr_idx = (day - 1) % len(core_curriculum)
            base_module = core_curriculum[curr_idx]

            # Injected skill gap focus
            injected_skill = missing_skills[(day - 1) % len(missing_skills)] if missing_skills else "System Design"

            milestones.append({
                "day": day,
                "focus_topic": f"Day {day}: {base_module['topic']} (Special Focus: {injected_skill})",
                "learning_objectives": [
                    f"Deep dive into practical use cases of {injected_skill}",
                    base_module["objectives"][0],
                    base_module["objectives"][1]
                ],
                "practice_challenge": f"Hands-on with {injected_skill}: {base_module['challenge']}",
                "recommended_resources": base_module["resources"] + [f"{injected_skill} Documentation and Practical Guides"]
            })

        return milestones
