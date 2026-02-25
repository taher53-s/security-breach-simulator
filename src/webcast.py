"""
Webcast System for Security Breach Simulator
Streams scenario events in real-time using Server-Sent Events (SSE)
"""
from __future__ import annotations

import json
import time
import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator
from dataclasses import dataclass, asdict


@dataclass
class WebcastEvent:
    """A real-time event in the webcast stream"""
    event_type: str  # "stage", "indicator", "action", "alert", "complete"
    stage: int
    timestamp: float
    data: dict[str, Any]
    
    def to_sse(self) -> str:
        """Convert to SSE format"""
        return f"event: {self.event_type}\ndata: {json.dumps(self.to_dict())}\n\n"
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ScenarioWebcaster:
    """Streams scenario events in real-time using SSE"""
    
    def __init__(self, scenario_id: str, seed: int | None = None) -> None:
        self.scenario_id = scenario_id
        self.seed = seed
        self.events: list[WebcastEvent] = []
        self._start_time: float | None = None
    
    async def stream_events(self) -> AsyncGenerator[WebcastEvent, None]:
        """Stream events as they would occur in real-time"""
        # Import here to avoid circular imports
        from generators.sample_breach import BreachGenerator
        
        generator = BreachGenerator(seed=self.seed)
        scenario = generator.generate(self.scenario_id)
        
        self._start_time = time.time()
        
        # Stream scenario metadata
        yield WebcastEvent(
            event_type="start",
            stage=0,
            timestamp=0,
            data={
                "scenario_id": scenario["scenario"]["scenario_id"],
                "name": scenario["scenario"]["name"],
                "severity": scenario["scenario"]["get"]("severity", "unknown"),
                "total_duration": scenario["total_duration_minutes"]
            }
        )
        
        # Stream each stage
        for stage in scenario.get("timeline", []):
            stage_num = stage.get("stage", 1)
            elapsed = stage.get("time_offset", "+0m")
            
            # Stage start event
            yield WebcastEvent(
                event_type="stage",
                stage=stage_num,
                timestamp=time.time() - self._start_time,
                data={
                    "name": stage.get("name"),
                    "description": stage.get("description"),
                    "time_offset": elapsed
                }
            )
            
            # Indicator events
            for indicator in stage.get("indicators", [])[:3]:
                yield WebcastEvent(
                    event_type="indicator",
                    stage=stage_num,
                    timestamp=time.time() - self._start_time,
                    data={"description": indicator}
                )
            
            # Simulate real-time delay between stages
            await asyncio.sleep(0.1)
        
        # Completion event
        yield WebcastEvent(
            event_type="complete",
            stage=0,
            timestamp=time.time() - self._start_time,
            data={
                "total_events": len(scenario.get("timeline", [])),
                "scenario_id": scenario_id
            }
        )
    
    def get_sse_stream(self) -> str:
        """Get SSE stream as string (for non-async usage)"""
        # This is a sync wrapper that returns the full stream
        from generators.sample_breach import BreachGenerator
        
        generator = BreachGenerator(seed=self.seed)
        scenario = generator.generate(self.scenario_id)
        
        output = ""
        current_time = 0
        
        # Start event
        start_data = {
            "scenario_id": scenario["scenario"]["scenario_id"],
            "name": scenario["scenario"]["name"],
            "severity": scenario["scenario"].get("severity", "unknown"),
            "total_duration": scenario["total_duration_minutes"]
        }
        output += f"event: start\ndata: {json.dumps(start_data)}\n\n"
        
        for stage in scenario.get("timeline", []):
            stage_num = stage.get("stage", 1)
            
            # Stage event
            stage_data = {
                "name": stage.get("name"),
                "description": stage.get("description"),
                "time_offset": stage.get("time_offset")
            }
            output += f"event: stage\ndata: {json.dumps(stage_data)}\n\n"
            
            # Indicator events
            for indicator in stage.get("indicators", [])[:3]:
                indicator_data = {"description": indicator}
                output += f"event: indicator\ndata: {json.dumps(indicator_data)}\n\n"
            
            current_time += 5  # Assume 5 min per stage
        
        # Complete event
        complete_data = {
            "total_events": len(scenario.get("timeline", [])),
            "scenario_id": self.scenario_id
        }
        output += f"event: complete\ndata: {json.dumps(complete_data)}\n\n"
        
        return output


def create_webcast_handler(scenario_id: str, seed: int | None = None):
    """Create an ASGI handler for SSE webcast"""
    from generators.sample_breach import BreachGenerator
    
    async def handle(scope, receive, send):
        # SSE headers
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/event-stream"],
                [b"cache-control", b"no-cache"],
                [b"connection", b"keep-alive"],
            ],
        })
        
        webcaster = ScenarioWebcaster(scenario_id, seed)
        
        async for event in webcaster.stream_events():
            await send({
                "type": "http.response.body",
                "body": event.to_sse().encode("utf-8"),
            })
    
    return handle


if __name__ == "__main__":
    # Demo webcast
    webcaster = ScenarioWebcaster("ransomware_attack", seed=42)
    print(webcaster.get_sse_stream())
