from typing import List, Dict, Any

# Curated, professional question bank mapped by role, category, and difficulty
FALLBACK_QUESTIONS: List[Dict[str, Any]] = [
    # Full Stack / Web Developer
    {
        "role": "Full Stack Developer",
        "category": "technical",
        "difficulty": "beginner",
        "skill_tag": "JavaScript",
        "question_text": "Explain the difference between '==' and '===' in JavaScript, and how type coercion works under the hood.",
        "expected_points": [
            "Explain loose equality (==) performs type coercion vs strict equality (===) which checks both type and value.",
            "Mention example: '5' == 5 is true, '5' === 5 is false.",
            "Explain why strict equality is best practice to avoid unpredictable bugs.",
            "Explain object reference comparison behavior in JavaScript."
        ],
        "sample_good_answer": "In JavaScript, '==' performs type coercion before comparison if operands have different types, whereas '===' strictly checks both value and type without coercion. For instance, '5' == 5 evaluates to true because the string is converted to a number, but '5' === 5 is false. In modern development, '===' is standard practice to prevent subtle coercion bugs."
    },
    {
        "role": "Full Stack Developer",
        "category": "technical",
        "difficulty": "intermediate",
        "skill_tag": "React",
        "question_text": "How does the React Virtual DOM diffing algorithm work, and why are 'key' props essential when rendering lists?",
        "expected_points": [
            "Virtual DOM is an in-memory representation of real DOM.",
            "Reconciliation uses heuristic O(n) algorithm comparing element types and keys.",
            "Keys allow React to identify which items have changed, been added, or removed across renders.",
            "Using array indexes as keys causes bugs when items are reordered or filtered."
        ],
        "sample_good_answer": "React maintains an in-memory Virtual DOM. During reconciliation, it compares the previous tree with the new tree using an O(n) heuristic algorithm. Keys give elements persistent identity across renders, allowing React to minimize expensive DOM mutations by reordering existing nodes rather than re-creating them from scratch."
    },
    {
        "role": "Full Stack Developer",
        "category": "technical",
        "difficulty": "advanced",
        "skill_tag": "System Design",
        "question_text": "Design a high-throughput URL shortening service (like Bitly). How would you handle unique ID generation, caching, and database read/write bottlenecks?",
        "expected_points": [
            "Estimate scale (reads vs writes, e.g. 100:1 read-heavy ratio).",
            "Unique ID generation using Base62 encoding with distributed sequence generators or Snowflake IDs.",
            "Caching hot URLs using Redis with LRU eviction.",
            "Database sharding or NoSQL for horizontal scalability, read replicas for high read throughput."
        ],
        "sample_good_answer": "A URL shortener is heavily read-intensive. I would generate unique short codes using Base62 encoding combined with a distributed ID generator like Twitter Snowflake or pre-allocated ZooKeeper ranges to avoid collisions. I would place Redis in front of the database using LRU eviction to cache top 20% URLs serving 80% traffic, and horizontally shard PostgreSQL or MongoDB with read replicas."
    },
    {
        "role": "Full Stack Developer",
        "category": "project",
        "difficulty": "intermediate",
        "skill_tag": "Architecture",
        "question_text": "Walk me through the architecture of a major web application you built. What was the toughest technical bottleneck you encountered, and how did you resolve it?",
        "expected_points": [
            "Clear overview of client, server, and database layers.",
            "Identification of a real bottleneck (e.g. database query latency, state synchronization, memory leak, or API rate limit).",
            "Measurable optimization approach and verified metric improvement."
        ],
        "sample_good_answer": "In my e-commerce application, the backend was built with FastAPI, PostgreSQL, and Redis, while the frontend used React. When concurrent checkout requests spiked, database locking on product stock queries caused response latency to climb over 2.5 seconds. I resolved this by decoupling stock checks with an optimistic concurrency control mechanism and caching product details in Redis, reducing checkout latency to under 180ms."
    },
    # Python & Backend Developer
    {
        "role": "Backend Engineer",
        "category": "technical",
        "difficulty": "beginner",
        "skill_tag": "Python",
        "question_text": "Explain Python's memory management, including reference counting and the garbage collection of cyclic references.",
        "expected_points": [
            "Python manages memory via private heap and reference counting.",
            "Every object has an ob_refcnt counter incremented on assignment and decremented on dereference.",
            "Cyclic references (A points to B and B points to A) cannot be freed by ref count alone.",
            "Generational garbage collector detects and cleans cyclic references."
        ],
        "sample_good_answer": "Python uses reference counting as its primary memory management mechanism. Each object tracks how many references point to it. When an object's reference count drops to zero, its memory is deallocated immediately. For cyclic references where objects point to each other, Python's cyclic generational garbage collector periodically inspects isolated reference islands and reclaims them."
    },
    {
        "role": "Backend Engineer",
        "category": "technical",
        "difficulty": "intermediate",
        "skill_tag": "SQL",
        "question_text": "What is the difference between clustered and non-clustered indexes in relational databases, and what are the trade-offs of adding too many indexes?",
        "expected_points": [
            "Clustered index defines physical storage order of rows on disk; only 1 per table.",
            "Non-clustered index creates a separate B-tree pointer structure referencing table rows.",
            "Trade-offs: indexes drastically speed up SELECT queries but slow down INSERT/UPDATE/DELETE because index trees must be updated.",
            "Increased disk storage overhead."
        ],
        "sample_good_answer": "A clustered index determines the physical on-disk sequence of rows in a table; hence, a table can have only one clustered index (typically the Primary Key). A non-clustered index is a secondary B-tree structure holding key columns and row locators. While indexes accelerate read queries, adding too many degrades write performance (INSERT/UPDATE/DELETE) and inflates storage consumption."
    },
    {
        "role": "Backend Engineer",
        "category": "technical",
        "difficulty": "advanced",
        "skill_tag": "Concurrency",
        "question_text": "Explain how Python's AsyncIO event loop handles concurrency compared to multithreading and multiprocessing, especially with CPU-bound vs I/O-bound tasks.",
        "expected_points": [
            "AsyncIO uses single-threaded cooperative multitasking with an event loop, ideal for I/O-bound operations.",
            "Python's GIL (Global Interpreter Lock) restricts multithreading from executing parallel CPU bytecodes.",
            "For CPU-bound operations, multiprocessing spawns independent processes with separate memory spaces to achieve true multi-core parallelism."
        ],
        "sample_good_answer": "AsyncIO is single-threaded cooperative multitasking where non-blocking tasks yield execution back to an event loop during I/O waits, making it exceptionally lightweight for thousands of concurrent network connections. However, because of Python's GIL, multithreading cannot achieve true CPU parallelism. For CPU-bound tasks like image processing or ML inference, multiprocessing is necessary to utilize multiple CPU cores."
    },
    # Behavioral & HR
    {
        "role": "General",
        "category": "behavioral",
        "difficulty": "intermediate",
        "skill_tag": "Collaboration",
        "question_text": "Describe a scenario where you had a strong technical disagreement with a team member or mentor. How did you handle the situation and what was the outcome?",
        "expected_points": [
            "Use STAR method (Situation, Task, Action, Result).",
            "Professional, objective communication without personal conflict.",
            "Gathering empirical evidence, benchmarks, or prototypes to evaluate options.",
            "Constructive compromise aligned with project goals."
        ],
        "sample_good_answer": "During our capstone project, a peer wanted to implement MongoDB while I advocated for PostgreSQL. Rather than debating theoretically, I scheduled a focused benchmarking session where we outlined our access patterns—which required complex relational joins between orders and users. By demonstrating foreign key integrity and running a quick prototype, we collaboratively agreed that PostgreSQL offered better consistency, resulting in zero schema corruption incidents during deployment."
    },
    {
        "role": "General",
        "category": "behavioral",
        "difficulty": "intermediate",
        "skill_tag": "Adaptability",
        "question_text": "Tell me about a time when a critical production bug occurred or a project deadline was suddenly moved forward. How did you prioritize your actions?",
        "expected_points": [
            "Calm, structured incident response.",
            "Root-cause analysis and immediate mitigation before permanent fix.",
            "Transparent stakeholder communication.",
            "Post-incident retrospective or regression testing to prevent recurrence."
        ],
        "sample_good_answer": "During an internship demo, our authentication token validation began failing for users on Safari due to third-party cookie restrictions. I first rolled back to the prior stable release to unblock live users, then isolated the issue using browser dev tools. I migrated our token storage from cross-domain cookies to same-site headers, wrote automated regression tests, and delivered the fix within 3 hours."
    },
    {
        "role": "General",
        "category": "hr",
        "difficulty": "beginner",
        "skill_tag": "Career Alignment",
        "question_text": "Why are you interested in this specific role and domain, and how do your technical background and career aspirations align with our engineering culture?",
        "expected_points": [
            "Demonstrates knowledge of target role domain.",
            "Connects candidate's skills and projects to the company's work.",
            "Expresses enthusiasm for continuous learning and engineering rigor."
        ],
        "sample_good_answer": "I have spent the past two years building full-stack web applications and deep-diving into backend API performance. I admire how your engineering team prioritizes developer autonomy and scalable system architecture. This role offers an ideal environment where I can apply my foundation in FastAPI, React, and database design while expanding my expertise in high-availability distributed systems."
    }
]


def get_fallback_questions(
    role: str,
    target_skills: List[str] = None,
    difficulty: str = "intermediate",
    count: int = 5
) -> List[Dict[str, Any]]:
    """Returns curated fallback questions tailored to role, skills, and requested difficulty."""
    if target_skills is None:
        target_skills = []

    skills_lower = [s.lower() for s in target_skills]
    
    # 1. Collect candidate questions
    matched = []
    general = []

    for q in FALLBACK_QUESTIONS:
        q_role = q["role"].lower()
        q_skill = q["skill_tag"].lower()
        q_diff = q["difficulty"]

        # Check if skill matches
        is_skill_match = any(s in q_skill or q_skill in s for s in skills_lower)
        is_role_match = (role.lower() in q_role) or (q_role in role.lower()) or (q_role == "general")

        if is_skill_match or is_role_match:
            matched.append(q)
        else:
            general.append(q)

    # Prioritize balanced mix: 1 HR, 1 Behavioral, 1 Project, 2 Technical
    selected = []
    
    # Try to grab one from each category
    for cat in ["technical", "project", "behavioral", "hr"]:
        cat_candidates = [q for q in matched if q["category"] == cat]
        if not cat_candidates:
            cat_candidates = [q for q in general if q["category"] == cat]
        
        if cat_candidates:
            # Prefer matching requested difficulty if specified and not adaptive
            diff_match = [q for q in cat_candidates if q["difficulty"] == difficulty]
            chosen = diff_match[0] if diff_match else cat_candidates[0]
            if chosen not in selected:
                selected.append(chosen)

    # Fill remaining count
    for q in (matched + general):
        if len(selected) >= count:
            break
        if q not in selected:
            selected.append(q)

    return selected[:count]
