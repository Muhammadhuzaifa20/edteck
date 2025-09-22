from typing import TypedDict, List, Dict, Optional, Any
from langgraph.graph import StateGraph, END
import requests

# ===== REASONER API CLIENT =====
class ReasonerAPI:
    """API client for the reasoner service"""

    BASE_URL = "http://localhost:5000"  # Local reasoner service

    @staticmethod
    def fetch_context(student_id: str) -> Dict[str, Any]:
        response = requests.post(
            f"{ReasonerAPI.BASE_URL}/context",
            json={"student_id": student_id},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def recommend_template(context: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{ReasonerAPI.BASE_URL}/template/recommend",
            json=context,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def fetch_template(template_name: str) -> Dict[str, Any]:
        """API call to fetch template definition (stages, metadata)"""
        response = requests.get(
            f"{ReasonerAPI.BASE_URL}/templates/{template_name.lower()}",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def propose_activities(stage: str, context: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{ReasonerAPI.BASE_URL}/activities/propose",
            json={"stage": stage, "context": context},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


# ===== STATE DEFINITION =====
class State(TypedDict, total=False):
    student_id: str
    student_info: Dict[str, Any]
    grade: str
    subject: str
    slos: List[str]
    pre_slos: List[str]

    template_options: List[str]
    chosen_template: Optional[str]
    template_recommendation: Optional[Dict[str, Any]]
    template_stages: List[str]

    template_approved: Optional[bool]
    template_adjustments: List[str]
    current_stage: Optional[str]

    stage_activities: Dict[str, List[Dict[str, Any]]]
    is_complete: bool
    final_output: Optional[Dict[str, Any]]


# ===== STAGE 1 =====
def stage1_fetch_context(state: State) -> State:
    print("\n=== STAGE 1: FETCHING CONTEXT ===")
    try:
        context = ReasonerAPI.fetch_context(state["student_id"])
        return {
            **state,
            "student_info": context.get("student_info", {}),
            "grade": context.get("grade", ""),
            "subject": context.get("subject", ""),
            "slos": context.get("slos", []),
            "pre_slos": context.get("pre_slos", []),
            "template_options": ["5E", "7E", "PBL", "Dynamic"],  # Placeholder
        }
    except Exception as e:
        print(f"Error fetching context: {e}")
        return {**state, "template_options": ["5E", "7E", "PBL", "Dynamic"]}


def stage1_recommend_template(state: State) -> State:
    print("\n=== GETTING TEMPLATE RECOMMENDATION ===")
    try:
        context = {
            "grade": state.get("grade", ""),
            "subject": state.get("subject", ""),
            "slos": state.get("slos", []),
            "pre_slos": state.get("pre_slos", []),
            "student_info": state.get("student_info", {}),
        }
        recommendation = ReasonerAPI.recommend_template(context)
        return {**state, "template_recommendation": recommendation}
    except Exception as e:
        print(f"Error getting template recommendation: {e}")
        return {**state, "template_recommendation": {"template": "5E", "confidence": 0}}


def stage1_choose_template(state: State) -> State:
    """HITL chooses template with CLI prompt"""
    rec = state.get("template_recommendation", {})
    print("\n=== CHOOSING TEMPLATE ===")
    print(f"Recommended: {rec.get('template', 'Unknown')} (confidence={rec.get('confidence', 0)})")
    print(f"Rationale: {rec.get('rationale', 'N/A')}")

    chosen = input(f"Enter template to use (default={rec.get('template','5E')}): ").strip() or rec.get("template", "5E")
    chosen = chosen.upper()
    if chosen not in {"5E", "7E", "PBL", "DYNAMIC"}:
        print(f"Unknown template '{chosen}', defaulting to 5E.")
        chosen = "5E"
    return {**state, "chosen_template": chosen}


# ===== TEMPLATE INIT (via API) =====
def init_template(state: State) -> State:
    """Fetch template definition via API"""
    template = state.get("chosen_template", "5E")
    print(f"\n=== INIT TEMPLATE: {template} ===")
    try:
        definition = ReasonerAPI.fetch_template(template)
        stages = definition.get("stages", [])
    except Exception as e:
        print(f"Error fetching template definition: {e}")
        # Fallback hardcoded defaults
        if template == "5E":
            stages = ["Engage", "Explore", "Explain", "Elaborate", "Evaluate"]
        elif template == "7E":
            stages = ["Elicit", "Engage", "Explore", "Explain", "Elaborate", "Evaluate", "Extend"]
        elif template == "PBL":
            stages = ["Challenge", "Investigate", "Create", "Debrief"]
        else:
            stages = []

    return {**state, "template_stages": stages}


# ===== STAGE 2 =====
def stage2_template_approval(state: State) -> State:
    print("\n=== TEMPLATE APPROVAL ===")
    print(f"Chosen template: {state.get('chosen_template')}")
    print(f"Stages: {state.get('template_stages', [])}")
    ans = input("Approve template? (y/n) [y]: ").strip().lower()
    approved = (ans != "n")
    return {**state, "template_approved": approved}


def stage2_template_adjustment(state: State) -> State:
    print("\n=== TEMPLATE ADJUSTMENT ===")
    stages = state.get("template_stages", [])
    print(f"Current stages: {stages}")
    ans = input("Would you like to add/remove stages? (y/n) [n]: ").strip().lower()
    adjustments: List[str] = []
    if ans == "y":
        new_stages = input("Enter comma-separated list of stages: ").split(",")
        new_stages = [s.strip() for s in new_stages if s.strip()]
        adjustments = new_stages
        return {**state, "template_stages": new_stages, "template_adjustments": adjustments}
    return {**state, "template_adjustments": adjustments}


def stage2_prepare_stages(state: State) -> State:
    stages = state.get("template_stages", [])
    return {**state, "current_stage": stages[0] if stages else None, "stage_activities": state.get("stage_activities", {})}


def stage2_populate_stage(state: State) -> State:
    current_stage = state.get("current_stage")
    if not current_stage:
        return state
    print(f"\n=== POPULATING STAGE: {current_stage} ===")

    context = {
        "stage": current_stage,
        "grade": state.get("grade", ""),
        "subject": state.get("subject", ""),
        "slos": state.get("slos", []),
        "pre_slos": state.get("pre_slos", []),
        "student_info": state.get("student_info", {}),
    }

    try:
        response = ReasonerAPI.propose_activities(current_stage, context)
        activities = response.get("activities", [])
    except Exception as e:
        print(f"Error fetching activities: {e}")
        activities = [{"type": "discussion", "title": f"Default activity for {current_stage}"}]

    approved = []
    for activity in activities:
        print(f"- {activity.get('type', 'Unknown')}: {activity.get('title', 'No title')}")
        ans = input("Approve this activity? (y/n) [y]: ").strip().lower()
        if ans != "n":
            approved.append(activity)

    current_activities = dict(state.get("stage_activities", {}))
    current_activities[current_stage] = approved
    return {**state, "stage_activities": current_activities}


def stage2_next_stage(state: State) -> State:
    stages = state.get("template_stages", [])
    current_stage = state.get("current_stage")
    if current_stage and current_stage in stages:
        idx = stages.index(current_stage)
        if idx < len(stages) - 1:
            return {**state, "current_stage": stages[idx + 1]}
    return {**state, "current_stage": None}
 
 
# ===== STAGE 3 =====
def stage3_check_completion(state: State) -> State:
    stages = state.get("template_stages", [])
    activities = state.get("stage_activities", {})
    complete = bool(stages) and all(stage in activities and activities[stage] for stage in stages)
    return {**state, "is_complete": complete}


def stage3_generate_output(state: State) -> State:
    print("\n=== GENERATING FINAL OUTPUT ===")
    output = {
        "template": state.get("chosen_template"),
        "stages": [{"name": stage, "activities": state.get("stage_activities", {}).get(stage, [])}
                   for stage in state.get("template_stages", [])],
        "metadata": {
            "student_id": state.get("student_id"),
            "grade": state.get("grade"),
            "subject": state.get("subject"),
            "slos": state.get("slos"),
        },
    }
    return {**state, "final_output": output}


# ===== BUILD WORKFLOW =====
def create_main_workflow():
    builder = StateGraph(State)

    # Stage 1
    builder.add_node("stage1_fetch_context", stage1_fetch_context)
    builder.add_node("stage1_recommend_template", stage1_recommend_template)
    builder.add_node("stage1_choose_template", stage1_choose_template)

    # Template init
    builder.add_node("init_template", init_template)

    # Stage 2
    builder.add_node("stage2_template_approval", stage2_template_approval)
    builder.add_node("stage2_template_adjustment", stage2_template_adjustment)
    builder.add_node("stage2_prepare_stages", stage2_prepare_stages)
    builder.add_node("stage2_populate_stage", stage2_populate_stage)
    builder.add_node("stage2_next_stage", stage2_next_stage)

    # Stage 3
    builder.add_node("stage3_check_completion", stage3_check_completion)
    builder.add_node("stage3_generate_output", stage3_generate_output)

    # Edges
    builder.add_edge("stage1_fetch_context", "stage1_recommend_template")
    builder.add_edge("stage1_recommend_template", "stage1_choose_template")
    builder.add_edge("stage1_choose_template", "init_template")

    builder.add_edge("init_template", "stage2_template_approval")
    builder.add_edge("stage2_template_approval", "stage2_template_adjustment")
    builder.add_edge("stage2_template_adjustment", "stage2_prepare_stages")
    builder.add_edge("stage2_prepare_stages", "stage2_populate_stage")
    builder.add_edge("stage2_populate_stage", "stage2_next_stage")

    def should_continue_stages(state: State) -> str:
        return "continue" if state.get("current_stage") else "complete"

    builder.add_conditional_edges(
        "stage2_next_stage",
        should_continue_stages,
        {"continue": "stage2_populate_stage", "complete": "stage3_check_completion"},
    )

    builder.add_edge("stage3_check_completion", "stage3_generate_output")
    builder.add_edge("stage3_generate_output", END)

    builder.set_entry_point("stage1_fetch_context")
    return builder.compile()


# ===== RUN =====
if __name__ == "__main__":
    workflow = create_main_workflow()

    initial_state: State = {
        "student_id": "student_123",
        "student_info": {},
        "grade": "",
        "subject": "",
        "slos": [],
        "pre_slos": [],
        "template_options": [],
        "chosen_template": None,
        "template_recommendation": None,
        "template_stages": [],
        "template_approved": None,
        "template_adjustments": [],
        "current_stage": None,
        "stage_activities": {},
        "is_complete": False,
        "final_output": None,
    }

    result = workflow.invoke(initial_state)
    print("\nWorkflow completed!")
    print("Final output:", result["final_output"])
