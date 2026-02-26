"""
Live Attack Simulation Engine — Security Breach Simulator
State-machine driven attack simulator that produces realistic SIEM-style events.
States: DORMANT → INITIAL_ACCESS → PERSISTENCE → LATERAL_MOVEMENT → EXFILTRATION → IMPACT
"""
from __future__ import annotations

import json
import hashlib
import random
import time
import threading
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable

ROOT_DIR = Path(__file__).resolve().parents[2]
LOGS_DIR = ROOT_DIR / ".simulation_logs"
LOGS_DIR.mkdir(exist_ok=True)

# ─── ANSI Colors ──────────────────────────────────────────────────────────────
R = "\033[91m"; Y = "\033[93m"; G = "\033[92m"; C = "\033[96m"
B = "\033[94m"; DIM = "\033[2m"; BOLD = "\033[1m"; RST = "\033[0m"


class AttackState(Enum):
    DORMANT         = auto()
    INITIAL_ACCESS  = auto()
    PERSISTENCE     = auto()
    LATERAL_MOVEMENT = auto()
    EXFILTRATION    = auto()
    IMPACT          = auto()
    CONTAINED       = auto()


STATE_COLORS = {
    AttackState.DORMANT:          DIM + "●" + RST,
    AttackState.INITIAL_ACCESS:   Y + "●" + RST,
    AttackState.PERSISTENCE:      Y + BOLD + "●" + RST,
    AttackState.LATERAL_MOVEMENT: R + "●" + RST,
    AttackState.EXFILTRATION:     R + BOLD + "●" + RST,
    AttackState.IMPACT:           R + BOLD + "██" + RST,
    AttackState.CONTAINED:        G + "●" + RST,
}

# ─── Realistic Data Pools ─────────────────────────────────────────────────────
_HOSTS = [
    "CORP-WS-001","CORP-WS-007","CORP-WS-019","MAIL-SRV-01",
    "FILE-SRV-03","DB-SRV-PROD","DC-CORP-01","JUMP-01",
    "DEV-BOX-12","HR-LAPTOP-08",
]
_USERS = [
    "jsmith","mwilliams","rjones","agarcia","lthompson",
    "bpatel","clee","nkumar","dchen","skhalid",
]
_IPS_INTERNAL = [f"192.168.{r}.{h}" for r in [1,2,10,20] for h in [5,12,23,45,67,89,101]]
_IPS_EXTERNAL = ["185.234.219.44","91.108.4.203","45.142.212.100","194.165.16.77"]
_PROCESSES = ["powershell.exe","cmd.exe","wmic.exe","mshta.exe","regsvr32.exe",
               "svchost.exe","lsass.exe","rundll32.exe","cscript.exe"]

def _rand_hash(length: int = 32) -> str:
    return hashlib.md5(str(random.random()).encode()).hexdigest()[:length]

def _rand_ip(external: bool = False) -> str:
    pool = _IPS_EXTERNAL if external else _IPS_INTERNAL
    return random.choice(pool)

def _rand_host() -> str: return random.choice(_HOSTS)
def _rand_user() -> str: return random.choice(_USERS)
def _rand_proc() -> str: return random.choice(_PROCESSES)

def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─── Event Templates per State ────────────────────────────────────────────────

def _events_initial_access() -> list[dict[str, Any]]:
    user = _rand_user()
    host = _rand_host()
    ext_ip = _rand_ip(external=True)
    return [
        {"event_id": 4625, "source": host, "user": f"CORP\\{user}",
         "ip": ext_ip, "event": "Failed logon", "count": random.randint(8,25),
         "detail": "Account logon failure — unknown username or bad password"},
        {"event_id": 4624, "source": host, "user": f"CORP\\{user}",
         "ip": ext_ip, "event": "Successful logon", "logon_type": 3,
         "detail": "Network logon succeeded after previous failures — possible credential stuffing"},
        {"event_id": 1102, "source": "DC-CORP-01", "user": f"CORP\\{user}",
         "ip": _rand_ip(), "event": "Audit log cleared",
         "detail": "Security audit log was cleared — evasion attempt"},
    ]

def _events_persistence() -> list[dict[str, Any]]:
    host = _rand_host()
    user = _rand_user()
    return [
        {"event_id": 4698, "source": host, "user": f"CORP\\{user}",
         "event": "Scheduled task created",
         "task_name": "\\Microsoft\\Windows\\Maintenance\\SysCheck",
         "command": f"C:\\Users\\Public\\{_rand_hash(8)}.exe",
         "detail": "Suspicious scheduled task using randomized binary name"},
        {"event_id": 4720, "source": "DC-CORP-01", "user": "CORP\\Administrator",
         "new_account": f"CORP\\svc_{_rand_hash(6)}",
         "event": "User account created",
         "detail": "Service account created outside change-management window"},
        {"event_id": 13, "source": host, "process": _rand_proc(),
         "registry_key": "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
         "value": _rand_hash(12) + ".dll",
         "event": "Registry value set (Run key)",
         "detail": "Persistence via registry Run key — common malware technique"},
    ]

def _events_lateral_movement() -> list[dict[str, Any]]:
    src = _rand_host(); dst = _rand_host()
    while dst == src: dst = _rand_host()
    user = _rand_user()
    return [
        {"event_id": 4648, "source": src, "target": dst,
         "user": f"CORP\\{user}", "ip": _rand_ip(),
         "event": "Logon with explicit credentials (Pass-the-Hash indicator)",
         "detail": "Explicit credential logon across hosts — lateral movement via PtH suspected"},
        {"event_id": 4688, "source": src, "process": "wmic.exe",
         "parent": "powershell.exe",
         "cmdline": f"wmic /node:{dst} process call create 'cmd.exe /c whoami'",
         "event": "Process creation — remote WMI execution",
         "detail": "WMI used for remote code execution — common living-off-the-land technique"},
        {"event_id": 5145, "source": dst,
         "share": "\\\\ADMIN$", "user": f"CORP\\{user}",
         "access": "ReadData/WriteData",
         "event": "Network share accessed (ADMIN$)",
         "detail": "Admin share access — SMB lateral movement or ransomware staging"},
    ]

def _events_exfiltration() -> list[dict[str, Any]]:
    host = _rand_host(); user = _rand_user()
    size_mb = random.randint(200, 2000)
    return [
        {"event_id": 5156, "source": host,
         "dst_ip": _rand_ip(external=True), "dst_port": 443,
         "bytes_out": size_mb * 1024 * 1024,
         "process": "svchost.exe",
         "event": f"Outbound data transfer — {size_mb}MB to external IP",
         "detail": "Large encrypted outbound transfer to unknown IP — possible exfiltration"},
        {"event_id": 4663, "source": host, "user": f"CORP\\{user}",
         "object": "C:\\Users\\Finance\\Q4_Reports\\",
         "accesses": "ReadData (or ListDirectory)",
         "event": "Filesystem object access — bulk file read",
         "detail": "Mass file access in sensitive directory — staging for exfiltration"},
        {"event_id": 4104, "source": host,
         "script_block": "Compress-Archive -Path C:\\staging\\ -DestinationPath C:\\Windows\\Temp\\backup.zip",
         "event": "PowerShell script block — archive creation",
         "detail": "PowerShell archiving sensitive files before transfer"},
    ]

def _events_impact() -> list[dict[str, Any]]:
    hosts = random.sample(_HOSTS, min(4, len(_HOSTS)))
    return [
        {"event_id": 4663, "source": h,
         "event": "Mass file modification detected",
         "extension_change": ".encrypted",
         "files_affected": random.randint(500, 5000),
         "detail": "File encryption in progress — ransomware IOC"}
        for h in hosts
    ] + [
        {"event_id": 7045, "source": "DC-CORP-01",
         "service_name": "Shadow Copy Delete Service",
         "binary": "cmd.exe /c vssadmin delete shadows /all /quiet",
         "event": "Service installed — shadow copy deletion",
         "detail": "VSS deletion prevents recovery — ransomware finalisation"}
    ]


STATE_EVENT_GENERATORS: dict[AttackState, Callable[[], list[dict[str, Any]]]] = {
    AttackState.INITIAL_ACCESS:    _events_initial_access,
    AttackState.PERSISTENCE:       _events_persistence,
    AttackState.LATERAL_MOVEMENT:  _events_lateral_movement,
    AttackState.EXFILTRATION:      _events_exfiltration,
    AttackState.IMPACT:            _events_impact,
}

STATE_LABELS = {
    AttackState.INITIAL_ACCESS:    "INITIAL ACCESS",
    AttackState.PERSISTENCE:       "PERSISTENCE",
    AttackState.LATERAL_MOVEMENT:  "LATERAL MOVEMENT",
    AttackState.EXFILTRATION:      "EXFILTRATION",
    AttackState.IMPACT:            "IMPACT",
    AttackState.CONTAINED:         "CONTAINED",
}


class SimulationEngine:
    """State-machine driven live attack simulator."""

    FLOW: list[AttackState] = [
        AttackState.INITIAL_ACCESS,
        AttackState.PERSISTENCE,
        AttackState.LATERAL_MOVEMENT,
        AttackState.EXFILTRATION,
        AttackState.IMPACT,
    ]

    def __init__(self, scenario_id: str, speed: float = 1.0, blue_team_mode: bool = False) -> None:
        self.scenario_id = scenario_id
        self.speed = speed
        self.blue_team_mode = blue_team_mode
        self.state = AttackState.DORMANT
        self.events_log: list[dict[str, Any]] = []
        self._log_file = LOGS_DIR / f"{scenario_id}_{int(time.time())}.jsonl"
        self._paused = threading.Event()
        self._paused.set()  # start unpaused

    def _transition(self, new_state: AttackState) -> None:
        self.state = new_state

    def _emit(self, event: dict[str, Any]) -> dict[str, Any]:
        event["timestamp"] = _ts()
        event["scenario"] = self.scenario_id
        event["state"] = self.state.name
        self.events_log.append(event)
        with open(self._log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
        return event

    def _sleep(self, seconds: float) -> None:
        time.sleep(seconds / self.speed)

    def _print_event(self, event: dict[str, Any]) -> None:
        eid = event.get("event_id", "????")
        msg = event.get("event", "unknown event")
        detail = event.get("detail", "")
        ts = event.get("timestamp", "")[:19]
        src = event.get("source", "?")

        severity_color = R if self.state in (AttackState.IMPACT, AttackState.EXFILTRATION) else Y
        print(f"  {DIM}{ts}{RST}  {severity_color}[{eid:>4}]{RST}  "
              f"{BOLD}{src:<15}{RST}  {msg}")
        if detail:
            print(f"  {DIM}{'':>22}↳ {detail}{RST}")

    def _print_state_banner(self) -> None:
        label = STATE_LABELS.get(self.state, self.state.name)
        icon = STATE_COLORS.get(self.state, "●")
        width = 60
        print(f"\n  {'─'*width}")
        print(f"  {icon}  {BOLD}{label}{RST}")
        print(f"  {'─'*width}")

    def _blue_team_prompt(self) -> bool:
        """Pause and ask user for correct response. Returns True if correct."""
        prompts = {
            AttackState.INITIAL_ACCESS:    ("Block the external IP and force MFA reset", "block-ip"),
            AttackState.PERSISTENCE:       ("Delete the scheduled task and revoke the new account", "delete-task"),
            AttackState.LATERAL_MOVEMENT:  ("Isolate the source host from the network", "isolate-host"),
            AttackState.EXFILTRATION:      ("Block outbound traffic to the destination IP", "block-egress"),
            AttackState.IMPACT:            ("Activate incident response plan and restore from backup", "ir-plan"),
        }
        if self.state not in prompts:
            return True

        correct_label, correct_key = prompts[self.state]
        options = [
            ("1", "Investigate further (collect more logs)", "investigate"),
            ("2", correct_label, correct_key),
            ("3", "Notify management only", "notify"),
            ("4", "Reboot the affected host", "reboot"),
        ]
        random.shuffle(options)

        print(f"\n  {C}╔══ BLUE TEAM DECISION REQUIRED ═══════════════════════╗{RST}")
        print(f"  {C}║{RST}  What is the correct response to this attack stage?  {C}║{RST}")
        for num, label, _ in options:
            print(f"  {C}║{RST}  [{num}] {label:<50}{C}║{RST}")
        print(f"  {C}╚═══════════════════════════════════════════════════════╝{RST}")

        try:
            choice = input(f"  {BOLD}Your choice: {RST}").strip()
            selected = next((key for num, _, key in options if num == choice), None)
            if selected == correct_key:
                print(f"  {G}✓ CORRECT! +150 XP — attack progression slowed.{RST}\n")
                return True
            else:
                print(f"  {R}✗ WRONG. The attacker advances unchecked. -50 XP.{RST}")
                print(f"  {DIM}Correct answer: {correct_label}{RST}\n")
                return False
        except (EOFError, KeyboardInterrupt):
            return True

    def run(self) -> list[dict[str, Any]]:
        """Run the full simulation, printing live events."""
        print(f"\n  {BOLD}{'═'*60}{RST}")
        print(f"  {R}{BOLD}  ⚠  LIVE ATTACK SIMULATION — {self.scenario_id.upper()}{RST}")
        print(f"  {BOLD}{'═'*60}{RST}")
        print(f"  {DIM}Speed: {self.speed}x | Blue Team Mode: {self.blue_team_mode} | "
              f"Log: {self._log_file.name}{RST}\n")
        print(f"  {'TIMESTAMP':<22}{'EVENT_ID':<10}{'SOURCE':<17}DESCRIPTION")
        print(f"  {'─'*70}")

        for state in self.FLOW:
            self._transition(state)
            self._print_state_banner()

            gen = STATE_EVENT_GENERATORS.get(state)
            if gen:
                for event in gen():
                    self._emit(event)
                    self._print_event(event)
                    self._sleep(random.uniform(0.3, 0.8))

            if self.blue_team_mode:
                self._blue_team_prompt()

            self._sleep(random.uniform(1.0, 2.0))

        self._transition(AttackState.IMPACT)
        print(f"\n  {R}{BOLD}{'█'*60}{RST}")
        print(f"  {R}{BOLD}  SIMULATION COMPLETE — ATTACK SUCCEEDED{RST}")
        print(f"  {R}{BOLD}{'█'*60}{RST}")
        print(f"  {DIM}Total events logged: {len(self.events_log)}{RST}")
        print(f"  {DIM}Log saved: {self._log_file}{RST}\n")

        return self.events_log

    def run_blind_challenge(self) -> str:
        """Run simulation silently, return raw logs for challenge mode."""
        for state in self.FLOW:
            self._transition(state)
            gen = STATE_EVENT_GENERATORS.get(state)
            if gen:
                for event in gen():
                    self._emit(event)
        return self._log_file.read_text()


def run_simulation(scenario_id: str, speed: float = 1.0, blue_team: bool = False) -> None:
    engine = SimulationEngine(scenario_id, speed=speed, blue_team_mode=blue_team)
    engine.run()


if __name__ == "__main__":
    run_simulation("ransomware_attack", speed=3.0, blue_team=False)
