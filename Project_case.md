💼 What's Already Happening
The implications shook the Dutch media landscape—but they shouldn't have surprised anyone. The disruption was already underway.

During the same segment, Klopping shared data from conversations with industry leaders that painted a stark picture:

Agency Workforce Collapse:
One Dutch advertising agency downsized from 290 copywriters to 20 after implementing AI systems
Photography budgets at major agencies dropped 90%—from €10 million to €1 million—as AI-generated imagery replaced commissioned shoots
A Dutch insurance company reports that all damage claims are now processed by AI agents, with no human review required
Global Data Confirms the Trend:
A 2025 analysis of 180 million job postings revealed the acceleration:

Copywriters: Down 28% year-over-year (two consecutive years of decline)
Photographers: Down 28% (matching the copywriter decline)
Computer graphic artists: Down 33% (including 3D artists, VFX specialists, technical artists)
Marketing coordinators: Roles becoming "extinct" as AI generates marketing plans with superior analytics
Forrester Research projects 15% of advertising agency jobs will be eliminated in 2026—pulling forward their original 2030 predictions by four years. One global holding company CEO stated on record: "By 2028, we'll double profits and halve the people."

The roles most at risk? Administrative (28% of losses), sales (22%), and market research (18%). But here's the twist: creative roles like senior writers and strategists remain stable. AI doesn't replace creativity—it replaces execution. Agencies are becoming smaller teams of high-level decision-makers managing AI workforces.

🎯 Your Challenge
Most AI systems are single-agent architectures: one LLM, one prompt, one output. But real work doesn't happen that way. Marketing campaigns require research, strategy, copywriting, design, and quality control. Complex problems demand specialization, collaboration, and orchestration.

What if your AI system wasn't one generalist assistant but a team of specialists that could delegate tasks, share context, critique each other's work, and iterate toward better outcomes?

The big question: How do we build multi-agent systems where specialized AI agents collaborate effectively to solve complex problems—producing results that exceed what any single agent could achieve alone?

🎲 Assignment
Challenge: Build Your Own Multi-Agent Marketing Team
Recreate what Reclamebureau Eva is doing.

Build a multi-agent system that takes a product description (book, startup feature, service) and produces a complete marketing campaign in 10-20 minutes. Your input is product information—text, PDFs, or natural language descriptions. Your output is a professional marketing campaign: target audience definition, positioning strategy, key messages, channel-specific copy, and creative concepts. The quality bar? Someone should be able to use this campaign professionally without extensive revision.

The technical challenges are substantial. How do you design agents that genuinely specialize rather than just having different prompts? How do you structure communication so agents collaborate effectively without endless back-and-forth? What triggers one agent to seek input from teammates versus making autonomous decisions? How do you prevent one agent from dominating while others become passive? When does collaboration enhance output quality, and when does coordination overhead outweigh the benefits? And critically, how do you make the collaboration itself visible so you can debug, evaluate, and improve the system?

Success means: Taking a product description and producing a complete marketing campaign (audience, strategy, copy, concepts) in 10-20 minutes, with visible agent collaboration that shows genuine teamwork, specialized agent contributions that reflect distinct expertise, and professional output quality that marketers would actually use.

Your research territory: Multi-agent architectures, agent communication protocols, workflow orchestration, task decomposition, role specialization, emergent collaboration patterns.

⚖️ Ethics & Responsibility
Multi-agent systems amplify both the power and the risks of AI. When a team of AI agents produces a marketing campaign in ten minutes, what happens to the marketers whose work that replaces? Between 2024 and 2025, copywriter positions declined 28% globally. Graphic artist roles dropped 33%. One Dutch agency went from 290 copywriters to 20. These aren't projections—they're documented workforce reductions happening right now.

Your decision log must grapple with this reality: What ethical responsibility do you have when building systems that demonstrably eliminate middle-class jobs? The counterargument matters too—creative leadership roles are growing, and small teams of highly-skilled humans managing AI systems may be more sustainable than bloated agencies doing repetitive work manually. But that restructuring creates winners and losers. Who benefits from this transition, and who gets left behind?

Accountability in Distributed Systems: When agents communicate with each other, errors can cascade—one agent's hallucination becomes another's input, compounding mistakes across the system. If your multi-agent system produces harmful, biased, or incorrect content, who's accountable? The developer who built the orchestration? The person who triggered the workflow? The AI companies that provided the models? How do you design responsibility into systems where no single component "decides" the outcome?

The Black Box Within a Black Box: Individual LLM decisions are already opaque. Multi-agent interactions create emergent behaviors that weren't explicitly programmed. How do you explain why the system reached a particular conclusion when it emerged from collaborative reasoning? How do you debug a system where Agent C's output depends on conversations between Agents A, B, and D that you can barely trace? What does transparency mean when the system itself doesn't know exactly how it arrived at a decision?

Bias Amplification: If your agents are trained on similar data, they might reinforce each other's biases rather than providing diverse perspectives. When all seven agents agree on a campaign strategy, is that consensus or confirmation bias? How do you ensure your "team" actually benefits from specialization rather than creating an echo chamber of similar viewpoints?

Resource Intensity at Scale: Multi-agent systems run multiple LLMs simultaneously, each processing inputs and generating outputs. If every marketing agency, software company, and research organization deploys multi-agent systems, what's the aggregate environmental cost? What's the financial cost? Are these systems sustainable at scale, or do they only make sense for high-value use cases?

🧠 Why This Matters
We're witnessing the industrialization of knowledge work. Just as assembly lines broke manufacturing into specialized tasks, multi-agent systems are decomposing intellectual labor into AI-executable roles. Reclamebureau Eva wasn't a gimmick—it was a proof of concept that knowledge work can be automated through agent orchestration.

The technical architecture is increasingly accessible: workflow platforms are low-code, LLM APIs are widely available, and frameworks abstract the complexity. The barrier to entry is lower than ever. This isn't emerging technology—it's deployable infrastructure.

This shift has profound implications for the future of work. If AI agents can collaborate like human teams, what roles remain uniquely human? The data suggests an answer: strategic thinking, creative direction, and quality judgment remain valuable. Junior execution roles are being automated rapidly. Senior leadership positions that make high-level decisions, provide creative vision, and exercise nuanced judgment are growing.

What does "managing" a team of AI agents look like? How do organizations restructure when some departments become fully autonomous AI systems? These aren't hypothetical questions—they're operational challenges facing businesses right now.

Understanding how to design, orchestrate, and control multi-agent systems gives you a critical skill for the next decade. Whether you're building automation tools, consulting on AI transformation, or defending human roles in knowledge work, you need to understand how specialized AI teams function—and what happens to human workers in the process.

The skills you'll develop:
Multi-agent system architecture and design patterns
Workflow orchestration and task delegation strategies
Agent communication protocols and message passing
Role specialization and capability differentiation
Quality control mechanisms for collaborative AI systems
Debugging emergent behaviors in team-based systems
Cost and resource management for multi-agent deployments
Workforce impact analysis and ethical AI deployment
🚀 Getting Started
Start by studying the reference. Watch the full Jinek segment (the Reclamebureau Eva demo starts around 18:30), read Sjoerd's technical breakdown, understand how agents were designed with distinct roles and how communication was structured. Pay attention to what made collaboration effective versus just parallel work. What does genuine agent cooperation look like?

Think deeply about agent design before writing code. What makes a good team in the real world? Complementary skills, clear responsibilities, mutual respect, effective communication. How do you translate these human team dynamics into AI agent interactions? What does it mean for an AI agent to have a "role" versus just a different prompt?

Build incrementally and test relentlessly. Start with two agents to validate basic communication patterns. Does adding a second agent actually improve output quality, or just add coordination overhead? Measure impact before adding complexity. Reclamebureau Eva succeeded because each agent added clear value—if your agents duplicate work or create confusion, simplify.

Test with real products. Don't use toy examples—find an actual book that needs marketing, a startup's new feature, a local business looking for campaigns. Real-world ambiguity will expose weaknesses that clean test cases hide. Can your agents handle uncertainty? Do they ask clarifying questions when needed? Can they adapt strategy based on what they discover?

Document every architectural decision in your decision log. Why did you choose this communication pattern? How do agents decide when to collaborate versus work independently? What mechanisms prevent circular conversations or deadlocks? How do you measure whether collaboration is genuinely happening? Focus on the hard problems: coordinating without micromanaging, specializing without fragmenting, collaborating without endless debate.