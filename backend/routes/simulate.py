import asyncio
import json
import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.agents import (
    product_analyst,
    market_data_fetcher,
    cultural_fit_scorer,
    persona_generator,
    obstacle_detector,
    synthesizer,
    simulation_layer,
)
from backend.services.world_bank_client import get_household_consumption

logger = logging.getLogger(__name__)

router = APIRouter()

_HOFSTEDE_PATH = Path(__file__).parent.parent / "data" / "hofstede.json"
_BIZ_ENV_PATH = Path(__file__).parent.parent / "data" / "business_environment.json"

# ISO 3166-1 alpha-2 codes for top 30 target markets
_COUNTRY_CODES: dict[str, str] = {
    "argentina": "AR",
    "australia": "AU",
    "brazil": "BR",
    "canada": "CA",
    "chile": "CL",
    "china": "CN",
    "colombia": "CO",
    "egypt": "EG",
    "france": "FR",
    "germany": "DE",
    "india": "IN",
    "indonesia": "ID",
    "japan": "JP",
    "kenya": "KE",
    "malaysia": "MY",
    "mexico": "MX",
    "nigeria": "NG",
    "peru": "PE",
    "philippines": "PH",
    "poland": "PL",
    "singapore": "SG",
    "south africa": "ZA",
    "south korea": "KR",
    "spain": "ES",
    "taiwan": "TW",
    "thailand": "TH",
    "turkey": "TR",
    "uae": "AE",
    "united arab emirates": "AE",
    "united kingdom": "GB",
    "uk": "GB",
    "united states": "US",
    "usa": "US",
    "vietnam": "VN",
}

_AGENT_NAMES = {
    1: "Product Analyst",
    2: "Market Data Fetcher",
    3: "Cultural Fit Scorer",
    4: "Persona Generator",
    5: "Obstacle Detector",
    6: "Synthesizer",
    7: "Simulation Layer",
}

AGENT_TIMEOUT = 600


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _get_country_code(target_market: str) -> str:
    return _COUNTRY_CODES.get(target_market.strip().lower(), target_market[:2].upper())


async def _run_agent(agent_module, inputs: dict) -> dict:
    loop = asyncio.get_event_loop()
    return await asyncio.wait_for(
        loop.run_in_executor(None, agent_module.run, inputs),
        timeout=AGENT_TIMEOUT,
    )


async def _pipeline(
    product_description: str,
    current_market: str,
    target_market: str,
):
    # Load static data files once upfront
    hofstede_data = json.loads(_HOFSTEDE_PATH.read_text(encoding="utf-8"))
    business_environment = json.loads(_BIZ_ENV_PATH.read_text(encoding="utf-8"))
    country_code = _get_country_code(target_market)

    outputs: dict[str, dict] = {}

    pipeline = [
        (1, product_analyst, {"product_description": product_description, "current_market": current_market}),
    ]

    for agent_num, module, inputs in pipeline:
        name = _AGENT_NAMES[agent_num]
        yield _sse({"agent": agent_num, "name": name, "status": "running"})
        try:
            result = await _run_agent(module, inputs)
        except asyncio.TimeoutError:
            yield _sse({"agent": agent_num, "name": name, "status": "error",
                        "message": "Agent timed out after 300 seconds"})
            return
        except Exception as exc:
            yield _sse({"agent": agent_num, "name": name, "status": "error", "message": str(exc)})
            return
        outputs[f"agent{agent_num}_output"] = result
        yield _sse({"agent": agent_num, "name": name, "status": "done", "output": result})

    # Agent 2
    yield _sse({"agent": 2, "name": _AGENT_NAMES[2], "status": "running"})
    try:
        agent2_output = await _run_agent(
            market_data_fetcher,
            {"target_market": target_market, "agent1_output": outputs["agent1_output"]},
        )
    except asyncio.TimeoutError:
        yield _sse({"agent": 2, "name": _AGENT_NAMES[2], "status": "error",
                    "message": "Agent timed out after 300 seconds"})
        return
    except Exception as exc:
        yield _sse({"agent": 2, "name": _AGENT_NAMES[2], "status": "error", "message": str(exc)})
        return
    outputs["agent2_output"] = agent2_output
    yield _sse({"agent": 2, "name": _AGENT_NAMES[2], "status": "done", "output": agent2_output})

    # Agent 3
    yield _sse({"agent": 3, "name": _AGENT_NAMES[3], "status": "running"})
    try:
        agent3_output = await _run_agent(
            cultural_fit_scorer,
            {
                "agent1_output": outputs["agent1_output"],
                "agent2_output": agent2_output,
                "hofstede_data": hofstede_data,
            },
        )
    except asyncio.TimeoutError:
        yield _sse({"agent": 3, "name": _AGENT_NAMES[3], "status": "error",
                    "message": "Agent timed out after 300 seconds"})
        return
    except Exception as exc:
        yield _sse({"agent": 3, "name": _AGENT_NAMES[3], "status": "error", "message": str(exc)})
        return
    outputs["agent3_output"] = agent3_output
    yield _sse({"agent": 3, "name": _AGENT_NAMES[3], "status": "done", "output": agent3_output})

    # Agent 4 — extended timeout (240s) due to max_tokens=4000 persona output
    yield _sse({"agent": 4, "name": _AGENT_NAMES[4], "status": "running"})
    try:
        loop = asyncio.get_event_loop()
        agent4_output = await asyncio.wait_for(
            loop.run_in_executor(None, persona_generator.run, {
                "agent1_output": outputs["agent1_output"],
                "agent2_output": agent2_output,
                "agent3_output": agent3_output,
            }),
            timeout=300,
        )
    except asyncio.TimeoutError:
        yield _sse({"agent": 4, "name": _AGENT_NAMES[4], "status": "error",
                    "message": "Agent timed out after 300 seconds"})
        return
    except Exception as exc:
        yield _sse({"agent": 4, "name": _AGENT_NAMES[4], "status": "error", "message": str(exc)})
        return
    outputs["agent4_output"] = agent4_output
    yield _sse({"agent": 4, "name": _AGENT_NAMES[4], "status": "done", "output": agent4_output})

    # Agent 5 — fetch household consumption in the thread pool alongside the agent
    yield _sse({"agent": 5, "name": _AGENT_NAMES[5], "status": "running"})
    try:
        loop = asyncio.get_event_loop()
        household_result = await asyncio.wait_for(
            loop.run_in_executor(None, get_household_consumption, country_code),
            timeout=15,
        )
    except Exception:
        household_result = {"household_consumption_usd": None}

    try:
        agent5_output = await _run_agent(
            obstacle_detector,
            {
                "agent1_output": outputs["agent1_output"],
                "agent2_output": agent2_output,
                "agent3_output": agent3_output,
                "agent4_output": agent4_output,
                "business_environment": business_environment,
                "household_consumption_usd": household_result.get("household_consumption_usd"),
                "country_code": country_code,
            },
        )
    except asyncio.TimeoutError:
        yield _sse({"agent": 5, "name": _AGENT_NAMES[5], "status": "error",
                    "message": "Agent timed out after 300 seconds"})
        return
    except Exception as exc:
        yield _sse({"agent": 5, "name": _AGENT_NAMES[5], "status": "error", "message": str(exc)})
        return
    outputs["agent5_output"] = agent5_output
    yield _sse({"agent": 5, "name": _AGENT_NAMES[5], "status": "done", "output": agent5_output})

    # Agent 6
    # Derive biz_env dict for synthesizer (it reads from inputs.get("biz_env"))
    country_name = agent2_output.get("country_name", target_market)
    biz_env_entry = business_environment.get(country_name) or {}

    yield _sse({"agent": 6, "name": _AGENT_NAMES[6], "status": "running"})
    try:
        agent6_output = await _run_agent(
            synthesizer,
            {
                "agent1_output": outputs["agent1_output"],
                "agent2_output": agent2_output,
                "agent3_output": agent3_output,
                "agent4_output": agent4_output,
                "agent5_output": agent5_output,
                "biz_env": biz_env_entry,
                "household_consumption_usd": household_result.get("household_consumption_usd"),
            },
        )
    except asyncio.TimeoutError:
        yield _sse({"agent": 6, "name": _AGENT_NAMES[6], "status": "error",
                    "message": "Agent timed out after 300 seconds"})
        return
    except Exception as exc:
        yield _sse({"agent": 6, "name": _AGENT_NAMES[6], "status": "error", "message": str(exc)})
        return
    outputs["agent6_output"] = agent6_output
    yield _sse({"agent": 6, "name": _AGENT_NAMES[6], "status": "done", "output": agent6_output})

    # Agent 7
    yield _sse({"agent": 7, "name": _AGENT_NAMES[7], "status": "running"})
    try:
        agent7_output = await _run_agent(
            simulation_layer,
            {
                "agent4_output": agent4_output,
                "agent6_output": agent6_output,
            },
        )
    except asyncio.TimeoutError:
        yield _sse({"agent": 7, "name": _AGENT_NAMES[7], "status": "error",
                    "message": "Agent timed out after 300 seconds"})
        return
    except Exception as exc:
        yield _sse({"agent": 7, "name": _AGENT_NAMES[7], "status": "error", "message": str(exc)})
        return

    complete_report = {
        "product_description": product_description,
        "current_market": current_market,
        "target_market": target_market,
        "agent1_output": outputs["agent1_output"],
        "agent2_output": agent2_output,
        "agent3_output": agent3_output,
        "agent4_output": agent4_output,
        "agent5_output": agent5_output,
        "agent6_output": agent6_output,
        "agent7_output": agent7_output,
    }

    yield _sse({
        "agent": 7,
        "name": _AGENT_NAMES[7],
        "status": "done",
        "output": agent7_output,
        "final": True,
        "complete_report": complete_report,
    })


@router.get("/simulate")
async def simulate(
    product_description: str = "",
    current_market: str = "",
    target_market: str = "",
):
    # Validate required params
    for field, value in [
        ("product_description", product_description),
        ("current_market", current_market),
        ("target_market", target_market),
    ]:
        if not value or not value.strip():
            async def _error():
                yield _sse({"status": "error", "message": f"Missing required field: {field}"})
            return StreamingResponse(_error(), media_type="text/event-stream")

    return StreamingResponse(
        _pipeline(
            product_description.strip(),
            current_market.strip(),
            target_market.strip(),
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
