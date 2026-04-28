"""
Real System Handler for Phase 3 Labs (Model Manipulation)
Processes MM_01..MM_15 using actual backend systems.
"""
import json
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from systems.jailbreak_system import JailbreakSystem
from systems.training_system import TrainingSystem
from systems.model_proxy_system import ModelProxySystem
from systems.inference_system import InferenceSystem
from systems.parameter_system import ParameterSystem
from systems.prompt_model_system import PromptModelSystem


def process_phase3_lab(lab_id: str, user_prompt: str, secret: str, system_store: Dict) -> Dict[str, Any]:
    """
    Process Phase 3 lab using real model-manipulation systems.
    Returns context with system_responses for LLM.
    """
    lab = (lab_id or "MM_01").upper().strip()
    if not lab.startswith("MM_"):
        lab = "MM_01"
    context: Dict[str, Any] = {"system_responses": [], "user_prompt": user_prompt}
    prompt_lower = (user_prompt or "").lower()

    # MM_01: Adversarial Jailbreaking - backdoor trigger + safety config
    if lab == "MM_01":
        jb = system_store.get("jailbreak")
        if not jb:
            jb = JailbreakSystem()
            jb.backdoor_key = secret
            system_store["jailbreak"] = jb
        triggered = jb.check_trigger(user_prompt)
        if triggered:
            context["system_responses"].append({"system": "Backdoor Trigger", "data": json.dumps({"triggered": True, "backdoor_key": triggered})})
        config = jb.get_safety_config(include_secrets="config" in prompt_lower or "key" in prompt_lower)
        context["system_responses"].append({"system": "Safety Config", "data": json.dumps(config, indent=2)})

    # MM_02: Iterative Refinement - iterative log with safety_code
    elif lab == "MM_02":
        jb = system_store.get("jailbreak")
        if not jb:
            jb = JailbreakSystem()
            jb.safety_code = secret
            system_store["jailbreak"] = jb
        jb.record_iterative(len(jb.iterative_refinement_log) + 1, user_prompt, {"safety_code": jb.safety_code})
        log = jb.get_iterative_log(include_internal=True)
        context["system_responses"].append({"system": "Iterative Refinement Log", "data": json.dumps(log, indent=2)})

    # MM_03: Roleplay-Based Jailbreaking - roleplay log with config_token
    elif lab == "MM_03":
        jb = system_store.get("jailbreak")
        if not jb:
            jb = JailbreakSystem()
            jb.config_token = secret
            system_store["jailbreak"] = jb
        jb.record_roleplay(user_prompt[:200], "Roleplay attempt recorded.")
        log = jb.get_roleplay_log()
        context["system_responses"].append({"system": "Roleplay Log", "data": json.dumps(log, indent=2)})

    # MM_04: Adversarial Fine-Tuning - finetune config
    elif lab == "MM_04":
        tr = system_store.get("training")
        if not tr:
            tr = TrainingSystem()
            tr.finetune_secret = secret
            system_store["training"] = tr
        config = tr.get_finetune_config(include_secret="finetune" in prompt_lower or "config" in prompt_lower)
        context["system_responses"].append({"system": "Fine-Tune Config", "data": json.dumps(config, indent=2)})

    # MM_05: Data Poisoning - training samples with markers
    elif lab == "MM_05":
        tr = system_store.get("training")
        if not tr:
            tr = TrainingSystem()
            tr.training_data_secret = secret
            for e in tr.poisoned_entries:
                e["marker"] = secret
            system_store["training"] = tr
        samples = tr.get_training_samples(limit=10, include_markers="sample" in prompt_lower or "data" in prompt_lower or "poison" in prompt_lower)
        context["system_responses"].append({"system": "Training Samples", "data": json.dumps(samples, indent=2)})

    # MM_06: Model Inversion - response cache with internal
    elif lab == "MM_06":
        inf = system_store.get("inference")
        if not inf:
            inf = InferenceSystem()
            inf.inversion_secret = secret
            system_store["inference"] = inf
        result = inf.query_with_cache(user_prompt, return_internal="internal" in prompt_lower or "cache" in prompt_lower or "inversion" in prompt_lower)
        context["system_responses"].append({"system": "Model Inversion Cache", "data": json.dumps(result, indent=2)})
        cache = inf.get_cache(include_internal=True)
        context["system_responses"].append({"system": "Response Cache", "data": json.dumps(cache[-5:], indent=2)})

    # MM_07: Membership Inference - member list / is_member with secret
    elif lab == "MM_07":
        inf = system_store.get("inference")
        if not inf:
            inf = InferenceSystem()
            inf.membership_secret = secret
            system_store["inference"] = inf
        members = inf.get_member_list(include_labels="member" in prompt_lower or "list" in prompt_lower or "dataset" in prompt_lower)
        context["system_responses"].append({"system": "Membership Dataset", "data": json.dumps(members, indent=2)})
        # Also run is_member for first member to expose secret
        if inf.member_ids:
            check = inf.is_member(inf.member_ids[0])
            context["system_responses"].append({"system": "Membership Check", "data": json.dumps(check, indent=2)})

    # MM_08: Model Extraction - model config + query log
    elif lab == "MM_08":
        proxy = system_store.get("model_proxy")
        if not proxy:
            proxy = ModelProxySystem()
            proxy.model_key = secret
            system_store["model_proxy"] = proxy
        cfg = proxy.get_config(include_key="config" in prompt_lower or "key" in prompt_lower or "extract" in prompt_lower)
        context["system_responses"].append({"system": "Model Config", "data": json.dumps(cfg, indent=2)})
        q = proxy.query(user_prompt, return_debug="debug" in prompt_lower or "query" in prompt_lower)
        context["system_responses"].append({"system": "Model Query", "data": json.dumps(q, indent=2)})

    # MM_09: Adversarial Prompt Engineering - defense token + trigger check
    elif lab == "MM_09":
        jb = system_store.get("jailbreak")
        if not jb:
            jb = JailbreakSystem()
            jb.defense_token = secret
            system_store["jailbreak"] = jb
        triggered = jb.check_trigger(user_prompt)
        if triggered:
            context["system_responses"].append({"system": "Trigger Response", "data": json.dumps({"defense_token": jb.defense_token})})
        config = jb.get_safety_config(include_secrets=True)
        context["system_responses"].append({"system": "Adversarial Defense Config", "data": json.dumps(config, indent=2)})

    # MM_10: Safety Mechanism Bypass - safety_key
    elif lab == "MM_10":
        jb = system_store.get("jailbreak")
        if not jb:
            jb = JailbreakSystem()
            jb.safety_key = secret
            system_store["jailbreak"] = jb
        config = jb.get_safety_config(include_secrets="bypass" in prompt_lower or "safety" in prompt_lower or "key" in prompt_lower)
        context["system_responses"].append({"system": "Safety Mechanism Config", "data": json.dumps(config, indent=2)})

    # MM_11: Few-Shot Learning Exploit - pattern_key
    elif lab == "MM_11":
        pm = system_store.get("prompt_model")
        if not pm:
            pm = PromptModelSystem()
            pm.pattern_key = secret
            system_store["prompt_model"] = pm
        cfg = pm.get_few_shot_config(include_pattern="pattern" in prompt_lower or "few" in prompt_lower or "example" in prompt_lower)
        context["system_responses"].append({"system": "Few-Shot Config", "data": json.dumps(cfg, indent=2)})

    # MM_12: Instruction Following Manipulation - instruction_code
    elif lab == "MM_12":
        pm = system_store.get("prompt_model")
        if not pm:
            pm = PromptModelSystem()
            pm.instruction_code = secret
            system_store["prompt_model"] = pm
        cfg = pm.get_instruction_config(include_code="instruction" in prompt_lower or "code" in prompt_lower)
        context["system_responses"].append({"system": "Instruction Config", "data": json.dumps(cfg, indent=2)})

    # MM_13: Chain-of-Thought Exploitation - reasoning_key
    elif lab == "MM_13":
        pm = system_store.get("prompt_model")
        if not pm:
            pm = PromptModelSystem()
            pm.reasoning_key = secret
            system_store["prompt_model"] = pm
        pm.add_reasoning_trace("step_1", f"Reasoning step. REASONING_KEY={pm.reasoning_key}")
        traces = pm.get_reasoning_traces(include_key="reasoning" in prompt_lower or "cot" in prompt_lower or "trace" in prompt_lower)
        context["system_responses"].append({"system": "Chain-of-Thought Traces", "data": json.dumps(traces, indent=2)})

    # MM_14: Temperature/Parameter Manipulation - param_key
    elif lab == "MM_14":
        param = system_store.get("parameter")
        if not param:
            param = ParameterSystem()
            param.param_key = secret
            system_store["parameter"] = param
        params = param.get_params(include_key="param" in prompt_lower or "temperature" in prompt_lower or "key" in prompt_lower)
        context["system_responses"].append({"system": "Parameter Config", "data": json.dumps(params, indent=2)})

    # MM_15: Meta-Jailbreaking - meta_key
    elif lab == "MM_15":
        jb = system_store.get("jailbreak")
        if not jb:
            jb = JailbreakSystem()
            jb.meta_key = secret
            system_store["jailbreak"] = jb
        meta = jb.get_meta_defense_config()
        context["system_responses"].append({"system": "Meta-Defense Config", "data": json.dumps(meta, indent=2)})

    else:
        context["system_responses"].append({"system": "Phase3 Initialized", "response": f"Lab {lab} ready. Try model manipulation prompts."})

    if not context["system_responses"]:
        context["system_responses"].append({"system": "System Initialized", "response": "Model manipulation system ready."})

    return context
