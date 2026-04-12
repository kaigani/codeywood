import random

CONCEPTS_BY_LEVEL = {
    1: [
        "Love", "Action", "Hope", "Fear", "Joy", "Pain", "Trust", "Anger", "Peace", "Change",
        "Family", "Friendship", "Work", "Play", "Home", "Travel", "Music", "Art", "Food", "Sleep",
        "Health", "Money", "Time", "Choice", "Habit", "Learning", "Memory", "Dream", "Goal", "Effort",
        "Success", "Failure", "Courage", "Kindness", "Honesty", "Patience", "Sharing", "Listening", "Helping", "Respect",
        "Curiosity", "Wonder", "Nature", "Weather", "Fire", "Water", "Earth", "Air", "Light", "Shadow",
        "Story", "Game", "Team", "Leader", "Rule", "Order", "Chaos", "Beauty", "Balance", "Growth",
        "Loss", "Victory", "Challenge", "Skill", "Practice", "Focus", "Calm", "Energy", "Motion", "Rest",
        "Morning", "Night", "Season", "Color", "Shape", "Sound", "Voice", "Touch", "Taste", "Smell",
        "Question", "Answer", "Problem", "Solution", "Beginning", "Ending", "Journey", "Path", "Bridge", "Door",
        "Gift", "Promise", "Secret", "Smile", "Tear", "Risk", "Safety", "Need", "Want", "Value"
    ],
    2: [
        "Affection", "Conflict", "Purpose", "Identity", "Belonging", "Responsibility", "Discipline", "Motivation", "Commitment", "Forgiveness",
        "Empathy", "Loyalty", "Jealousy", "Gratitude", "Resilience", "Humility", "Ambition", "Independence", "Dependence", "Cooperation",
        "Competition", "Routine", "Creativity", "Observation", "Reflection", "Conversation", "Influence", "Reputation", "Tradition", "Innovation",
        "Community", "Culture", "Language", "Symbol", "Metaphor", "Humor", "Sincerity", "Doubt", "Faith", "Expectation",
        "Preparation", "Adaptation", "Recovery", "Healing", "Nutrition", "Exercise", "Exhaustion", "Productivity", "Efficiency", "Attention",
        "Distraction", "Planning", "Priority", "Deadline", "Opportunity", "Constraint", "Leadership", "Negotiation", "Persuasion", "Celebration",
        "Grief", "Regret", "Relief", "Temptation", "Moderation", "Impulse", "Consequence", "Justice", "Fairness", "Ownership",
        "Exchange", "Craft", "Design", "Pattern", "Contrast", "Rhythm", "Composition", "Perspective", "Discovery", "Exploration",
        "Navigation", "Environment", "Sustainability", "Scarcity", "Abundance", "Security", "Vulnerability", "Stability", "Transformation", "Continuity",
        "Legacy", "Obligation", "Service", "Maturity", "Character", "Temperament", "Sensitivity", "Boundaries", "Stewardship", "Credibility"
    ],
    3: [
        "Attachment", "Agency", "Reciprocity", "Interdependence", "Selfhood", "Alienation", "Authenticity", "Cognition", "Bias", "Heuristic",
        "Emotion", "Perception", "Intuition", "Narrative", "Representation", "Institution", "Normativity", "Legitimacy", "Authority", "Consent",
        "Accountability", "Coordination", "Incentive", "Externality", "Governance", "Pluralism", "Ideology", "Ritual", "Mythology", "Semiotics",
        "Aesthetics", "Irony", "Ambiguity", "Paradox", "Tension", "Subtext", "Framing", "Context", "Salience", "Signal",
        "Noise", "Abstraction", "Complexity", "Emergence", "Feedback", "Adaptability", "Optimization", "Tradeoff", "Uncertainty", "Probability",
        "Causality", "Correlation", "Variance", "Constraint", "Leverage", "Fragility", "Robustness", "Redundancy", "Optionality", "Conviction",
        "Reflection", "Deliberation", "Mediation", "Arbitration", "Restoration", "Equilibrium", "Asymmetry", "Symmetry", "Threshold", "Trajectory",
        "Momentum", "Drift", "Convergence", "Divergence", "Continuum", "Taxonomy", "Ontology", "Epistemology", "Phenomenon", "Mechanism",
        "Structure", "Function", "Dynamics", "Interpretation", "Embodiment", "Mimesis", "Canon", "Discourse", "Dialectic", "Temporality",
        "Memoryscape", "Morality", "Intention", "Volition", "Attention economy", "Social capital", "Collective action", "Identity formation", "Value system", "Worldview"
    ],
    4: [
        "Phenomenology", "Hermeneutics", "Teleology", "Deontology", "Utilitarianism", "Virtue ethics", "Structuralism", "Poststructuralism", "Existentialism", "Pragmatism",
        "Constructivism", "Determinism", "Compatibilism", "Dualism", "Monism", "Materialism", "Idealism", "Reductionism", "Holism", "Functionalism",
        "Behaviorism", "Connectionism", "Computationalism", "Symbol grounding", "Embodied cognition", "Situated learning", "Game theory", "Mechanism design", "Principal-agent problem", "Path dependence",
        "Collective intentionality", "Social contract", "Distributive justice", "Procedural justice", "Restorative justice", "Moral hazard", "Adverse selection", "Comparative advantage", "Network effects", "Public goods",
        "Tragedy of the commons", "Information asymmetry", "Counterfactual", "Bayesian inference", "Decision theory", "Prospect theory", "Cognitive dissonance", "Attribution error", "Metacognition", "Reflective equilibrium",
        "Intertextuality", "Metanarrative", "Subalternity", "Hegemony", "Biopower", "Disciplinary society", "Habitus", "Cultural capital", "Communicative action", "Speech act",
        "Performativity", "Liminality", "Rationality", "Ecological niche", "Systems thinking", "Second-order effects", "Nonlinearity", "Dynamical system", "Homeostasis", "Autopoiesis",
        "Cybernetics", "Attractor state", "State space", "Phase transition", "Complex adaptive systems", "Self-organization", "Antifragility", "Moral luck", "Identity politics", "Intersectionality",
        "Secularization", "Modernity", "Postmodernity", "Reflexivity", "Social reproduction", "Collective memory", "Mediatization", "Affective labor", "Epigenetics", "Gene-culture coevolution",
        "Nash equilibrium", "Pareto efficiency", "Cultural evolution", "Institutional isomorphism", "Semantic drift", "Conceptual blending", "Distributed cognition", "Adaptive expertise", "Critical realism", "Moral particularism"
    ],
    5: [
        "Anomie", "Reification", "Subsumption", "Hyperreality", "Deterritorialization", "Reterritorialization", "Rhizome", "Haecceity", "Transvaluation", "Apperception",
        "Intentionality", "Noema", "Noesis", "Being-in-the-world", "Thrownness", "Facticity", "Bad faith", "Negative capability", "Dialectical materialism", "Historical materialism",
        "Commodity fetishism", "Surplus value", "Alienated labor", "Instrumental reason", "Negative dialectics", "Genealogy", "Archaeology of knowledge", "Différance", "Simulacrum", "Hyperobject",
        "Actor-network theory", "Assemblage", "Memetics", "Niche construction", "Morphogenesis", "Teleonomy", "Enactivism", "Predictive processing", "Free energy principle", "Active inference",
        "Counterfactual regret", "Expected utility", "Bounded rationality", "Satisficing", "Preference falsification", "Signaling theory", "Costly signaling", "Mechanistic interpretability", "Goodhart's law", "Campbell's law",
        "Ergodicity", "Path integral intuition", "Attractor basin", "Hysteresis", "Criticality", "Percolation", "Scale invariance", "Renormalization intuition", "Entropy", "Negentropy",
        "Algorithmic bias", "Epistemic injustice", "Testimonial injustice", "Hermeneutical injustice", "Underdetermination", "Theory-ladenness", "Falsifiability", "Inference to best explanation", "Undecidability", "Reflexive modernization",
        "Decommodification", "Governmentality", "Social imaginary", "Episteme", "Discursive formation", "Interpellation", "Overdetermination", "Punctuated equilibrium", "Evolutionarily stable strategy", "Multilevel selection",
        "Neutral theory", "Drift diffusion", "Bayes-optimality", "Latent variable", "Manifold hypothesis", "Nonconvexity", "Identifiability", "Causal graph", "Do-calculus", "Mediating variable",
        "Instrumental variable", "Selection effect", "Collider bias", "Recursive self-improvement", "Mesa-optimization", "Inner alignment", "Outer alignment", "Speciation", "Ecosystem engineering", "Phenotypic plasticity"
    ],
    6: [
        "Ontic structural realism", "Epiphenomenalism", "Anomalous monism", "Panpsychism", "Neutral monism", "Process ontology", "Modal realism", "Counterpart theory", "Supervenience", "Multiple realizability",
        "Nonreductive physicalism", "Inferential role semantics", "Externalism", "Internalism", "Teleosemantics", "Truthmaker theory", "Mereology", "Mereotopology", "Essentialism", "Anti-essentialism",
        "Paraconsistent logic", "Modal logic", "De re modality", "De dicto modality", "Kripke semantics", "Proof theory", "Model theory", "Category mistake", "Quinean indispensability", "Hanlon-Bennett effect",
        "Mechanistic explanation", "Causal emergence", "Downward causation", "Computational irreducibility", "Logical depth", "Kolmogorov complexity", "Algorithmic information", "Minimum description length", "Shannon channel capacity", "Error-correcting code",
        "Topological data analysis", "Phase portrait", "Lyapunov function", "Bifurcation", "Chaos synchronization", "Stochastic resonance", "Metastability", "Order parameter", "Universality class", "Finite-size scaling",
        "Bayesian nonparametrics", "Variational inference", "Markov blanket", "Exchangeability", "Identifiability conditions", "Posterior consistency", "Regularization path", "Structural causal model", "Causal sufficiency", "Invariant risk minimization",
        "Equifinality", "Multicollinearity", "Heteroskedasticity", "Endogeneity", "General equilibrium", "Mechanism robustness", "Common knowledge", "Higher-order belief", "Information cascade", "Preference aggregation",
        "Arrow impossibility", "Median voter theorem", "Polycentric governance", "Institutional emergence", "Allostatic load", "Neuroplasticity", "Hebbian learning", "Predictive coding", "Global workspace", "Integrated information",
        "Self-model theory", "Embodied simulation", "Affordance landscape", "Participatory sense-making", "Biosemiotics", "Autocatalytic set", "Major transitions", "Multilevel governance", "Reflexive control", "Sociotechnical imaginary",
        "Path-specific effect", "Moral uncertainty", "Value pluralism", "Normative underdetermination", "Reflective endorsement", "Diachronic identity", "Semantic externality", "Latent confounder", "Partial observability", "Recursive utility"
    ],
    7: [
        "Homotopy type theory", "Dependent type theory", "Curry-Howard correspondence", "Gödel incompleteness", "Löwenheim-Skolem phenomenon", "Tarski undefinability", "Forcing independence", "Large cardinal axiom", "Topos theory", "Higher category theory",
        "Derived functor", "Adjointness", "Monoidal category", "Sheaf cohomology", "Spectral sequence", "Morphism", "Natural transformation", "Functoriality", "Yoneda lemma", "∞-groupoid",
        "Noncommutative geometry", "Operator algebra", "Hilbert space formalism", "Measure concentration", "Ergodic decomposition", "Martingale convergence", "Stochastic differential equation", "Ito calculus", "Fokker-Planck dynamics", "Renormalization group",
        "Spontaneous symmetry breaking", "Gauge invariance", "Path dependence in phase space", "Noetherian symmetry", "Topological defect", "Holographic duality", "Effective field theory", "Spacetime curvature", "Quantum decoherence", "Entanglement entropy",
        "Counterdiabatic driving", "Quantum error correction", "Tensor network", "Variational principle", "Manifold learning", "Representation theorem", "PAC-Bayes bound", "Statistical learning theory", "VC dimension", "Rademacher complexity",
        "Identifiability theorem", "Causal mediation analysis", "Counterfactual fairness", "Distribution shift", "Out-of-distribution generalization", "Domain adaptation", "Algorithmic recourse", "Mechanistic transparency", "Feature superposition", "Sparse autoencoder",
        "Gradient descent implicit bias", "Scaling law", "Loss landscape", "Grokking", "Phase retrieval", "Latent diffusion", "Score matching", "Energy-based modeling", "Normalizing flow", "Self-supervised objective",
        "Institutional epistemology", "Deliberative democracy", "Constitutional political economy", "Epistemic virtue", "Conceptual engineering", "Metaethics", "Error theory", "Expressivism", "Constructive empiricism", "Scientific realism",
        "Anthropocene governance", "Planetary boundaries", "Ecological resilience", "Regime shift", "Polyvagal theory", "Free-energy minimization", "Metastable cognition", "Enactive phenomenology", "Neural manifold", "Multiscale causation",
        "Selection theorem", "Hypergraph dynamics", "Perverse instantiation", "Value loading", "Corrigibility", "Mesa-objective", "Specification gaming", "Interpretability tax", "Shard theory", "Constitutional AI"
    ],
    8: [
        "Anabelian geometry", "Étale cohomology", "Motivic homotopy", "Perfectoid space", "p-adic Hodge theory", "Langlands correspondence", "Geometric Langlands", "Derived algebraic geometry", "Stacks", "∞-category",
        "Model category", "Higher topos theory", "Operad", "Factorization homology", "Microlocal analysis", "Pseudodifferential operator", "Calabi-Yau manifold", "Mirror symmetry", "Floer homology", "Symplectic reduction",
        "Ricci flow", "Geometric measure theory", "Nonlinear elliptic regularity", "Weak solution framework", "Navier-Stokes regularity", "Mean-field game", "Stochastic control", "Optimal transport", "Wasserstein gradient flow", "Concentration inequality",
        "Spin glass", "Replica symmetry breaking", "Conformal bootstrap", "Asymptotic freedom", "Gauge/gravity duality", "Topological quantum field theory", "AdS/CFT intuition", "Quantum chromodynamics vacuum", "Decoherent histories", "Resource theory of entanglement",
        "Fault-tolerant threshold", "Surface code", "Magic state distillation", "Quantum supremacy critique", "Lie group representation", "Tensor category", "Operator-valued distribution", "Tomita-Takesaki theory", "C*-algebra", "von Neumann algebra",
        "Semiparametric efficiency", "Double machine learning", "Causal discovery", "Invariant causal prediction", "Transportability", "Partial identification", "Sensitivity analysis", "Bayesian model averaging", "Diffusion probabilistic model", "Schrödinger bridge",
        "Rate-distortion theory", "Information bottleneck", "Kolmogorov-Arnold representation", "Neural tangent kernel", "Mean-field limit", "Lottery ticket hypothesis", "Circuit complexity", "Proof-carrying code", "Abstract interpretation", "Program synthesis",
        "Self-reference in formal systems", "Normative realism", "Constitutivism", "Reasons fundamentalism", "Parfitian reductionism", "Temporal discounting anomaly", "Collective epistemology", "Social choice impossibility", "Moral aggregation", "Population ethics",
        "Longtermism", "Existential risk", "Anthropic reasoning", "Observer selection effect", "Simulation argument", "Acausal coordination", "Decision instability", "Tiling agents", "Reflective oracle", "Logical induction",
        "Embedded agency", "Naturalized epistemology", "Dynamical isometry", "Representational geometry", "Neural collapse", "Category-theoretic semantics", "Metalogic", "Proof-theoretic ordinal", "Ordinal analysis", "Epistemic structural realism"
    ],
    9: [
        "Quasi-category straightening", "Derived deformation theory", "Spectral algebraic stack", "Motivic Galois group", "Topological modular forms", "Chromatic homotopy", "Stable ∞-category", "Condensed mathematics", "Prismatic cohomology", "Anabelian reconstruction",
        "Geometric Satake equivalence", "Perverse sheaf", "D-module", "Microlocal sheaf theory", "Arithmetic duality", "Iwasawa theory", "Automorphic representation", "Functorial lift", "Trace formula", "L-function special value",
        "Nonperturbative renormalization", "Lattice gauge confinement", "Conformal anomaly", "Topological order", "Anyonic braiding", "Fractional quantum Hall state", "Many-body localization", "Eigenstate thermalization", "Algebraic quantum field theory", "Modular tensor category",
        "Quantum Bayesianism", "Consistent histories", "Decoherence functional", "Operator K-theory", "Subfactor index", "Free probability", "Voiculescu entropy", "Rough path theory", "Malliavin calculus", "Large deviations principle",
        "McKean-Vlasov dynamics", "Mean curvature flow singularity", "Monge-Ampère regularity", "KAM stability", "Hamiltonian chaos", "Nonlinear dispersive PDE", "Weak KAM theory", "Geometric quantization", "Symplectic field theory", "Floquet engineering",
        "Counterfactual identifiability", "D-separation completeness", "Front-door criterion", "Proximal causal inference", "Targeted maximum likelihood", "M-estimation asymptotics", "Conformal prediction", "Distributional robustness", "Minimax lower bound", "Fisher information geometry",
        "Neural scaling phase transition", "In-context meta-learning", "Mechanistic feature circuit", "Superposition polytope", "Polysemantic neuron", "OOD calibration", "Truthfulness under distribution shift", "Interpretability faithfulness", "ELK problem", "Scalable oversight",
        "Deontic uncertainty", "Metaethical quietism", "Non-naturalist realism", "Normative functionalism", "Epistemic consequentialism", "Hinge epistemology", "Inferentialism", "Transcendental argument", "Neo-Aristotelian essentialism", "Substance dual-aspect theory",
        "Anthropic shadow", "Updateless decision theory", "Functional decision theory", "Logical counterfactual", "Reflective consistency", "Vingean reflection", "Embedded world-model", "Cartesian boundary problem", "Natural abstraction", "Ontology identification",
        "Mesa-search dynamics", "Concept extrapolation", "Shard consolidation", "Utility indifference", "Infra-Bayesianism", "Learning-theoretic alignment", "Agent foundations", "Doomsday argument variants", "Computational phenomenology", "Axiological cluelessness"
    ],
    10: [
        "Higher-order unification", "Proof-relevant parametricity", "Cubical type theory", "Univalent foundations", "Synthetic ∞-topos", "Motivic spectral sequence", "Derived stack descent", "Prismatic F-crystal", "Perfectoid tilting equivalence", "Anabelioid geometry",
        "p-adic Simpson correspondence", "Categorified Hall algebra", "Cohesive homotopy type theory", "Factorization algebra", "Topological recursion", "Geometric representation categorification", "Tensor triangular geometry", "Stable motivic stem", "Chromatic redshift", "Topological cyclic homology",
        "Microlocal perverse schober", "Noncommutative motive", "Index theorem on singular spaces", "Ricci flow surgery analysis", "Mean-field control with common noise", "Hypoelliptic diffusion semigroup", "Measure-valued solution concept", "Geometric Langlands duality", "Trace formula stabilization", "Relative trace formula",
        "Algebraic quantum field net", "Constructive gauge theory", "Entanglement wedge reconstruction", "Modular bootstrap", "Conformal defect operator", "Anyonic topological quantum computer", "Fault-tolerant lattice surgery", "Tensor-network holography", "Quantum resource monotone", "Operator-algebraic entropy",
        "Semiparametric efficiency bound", "Pathwise differentiability", "Double robustness", "Orthogonal score construction", "Proximal identification strategy", "Counterfactual transportability", "Selection diagram calculus", "Invariant causal mechanism", "Distributionally robust optimization", "Bayesian posterior contraction",
        "Nonasymptotic concentration regime", "PAC-Bayesian flat minima", "Neural tangent feature map", "Mechanistic superposition basis", "Sparse feature dictionary", "Circuit-level interpretability", "Representation engineering", "OOD epistemic calibration", "Scalable oversight decomposition", "ELK latent knowledge",
        "Corrigibility under self-modification", "Acausal bargaining equilibrium", "Reflective oracle fixed point", "Logical induction criterion", "Updateless policy selection", "Infra-Bayesian physicalism", "Natural abstraction hypothesis", "Embedded agency paradox", "Decision theory under logical uncertainty", "Ontology identification problem",
        "Population ethics repugnance", "Person-affecting restriction", "Axiological uncertainty", "Metaethical constructivist realism", "Normative underdetermination thesis", "Moral parliament formalism", "Epistemic permissivism", "Hinge commitment structure", "Predictive processing formalism", "Free-energy variational bound",
        "Integrated information exclusion", "Global neuronal workspace ignition", "Active inference policy prior", "Morphogenetic developmental system", "Niche-construction feedback loop", "Autocatalytic closure criterion", "Major evolutionary transition logic", "Multilevel selection partition", "Regime-shift hysteresis", "Planetary boundary transgression",
        "Causal emergence formalism", "Topological defect fusion", "Renormalization fixed point", "Category-theoretic compositionality", "Proof-theoretic ordinal collapse", "Constructive empiricist underdetermination", "Epistemic structural realism debate", "Phenomenal intentionality thesis", "Semantic externalism about content", "Diachronic personal identity reduction"
    ]
}


def flatten_concepts(concepts_by_level: dict[int, list[str]]) -> dict[str, int]:
    """
    Returns a flat dictionary:
    {
        "Love": 1,
        "Action": 1,
        ...
        "Geometric Langlands duality": 10
    }
    """
    flat = {}
    for level, concepts in concepts_by_level.items():
        for concept in concepts:
            flat[concept] = level
    return flat


def generate_weighted_concepts(
    concepts_by_level: dict[int, list[str]],
    count: int = 10,
    min_weight: int = 0,
    max_weight: int = 100
) -> list[tuple[str, int]]:
    """
    Randomly selects `count` unique concepts from the full 1000
    and assigns each a random integer weight between min_weight and max_weight.
    """
    flat_dict = flatten_concepts(concepts_by_level)
    all_concepts = list(flat_dict.keys())

    if count > len(all_concepts):
        raise ValueError("count cannot be larger than the total number of concepts.")

    chosen = random.sample(all_concepts, count)
    return [(concept, random.randint(min_weight, max_weight)) for concept in chosen]


def main():
    flat_dict = flatten_concepts(CONCEPTS_BY_LEVEL)

    print(f"Total levels: {len(CONCEPTS_BY_LEVEL)}")
    print(f"Total concepts: {len(flat_dict)}")
    print("\nRandom weighted concept list:\n")

    weighted_list = generate_weighted_concepts(CONCEPTS_BY_LEVEL, count=10)

    for concept, weight in weighted_list:
        print(f"{concept}: {weight}")


if __name__ == "__main__":
    main()