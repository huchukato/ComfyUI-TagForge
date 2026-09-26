import pathlib
import threading
import urllib.request

from .py import endpoints, wildcard_processor


NODE_CLASS_MAPPINGS = {
    "WildcardProcessor": wildcard_processor.WildcardProcessorNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "WildcardProcessor": "🃏 Wildcard Processor",
}
WEB_DIRECTORY = "./web"


# Garage is the source of truth for the bundled pmp wildcards — sync them on
# every ComfyUI start so prompt updates ship without waiting for a node release.
_GARAGE_WILDCARDS_URL = "https://github.com/huchukato/ComfyUI-Garage/raw/master/wildcards"
_GARAGE_WILDCARDS = (
    "pmp/act.yaml",
    "pmp/actff.yaml",
    "pmp/actffm.yaml",
    "pmp/actmmf.yaml",
    "pmp/actsolo.yaml",
    "pmp/blwjob.yaml",
    "pmp/prmpt.yaml",
    "pmp/qwen21.yaml",
    "pmp/prmpt/acc.yaml",
    "pmp/prmpt/char.yaml",
    "pmp/prmpt/clths.yaml",
    "pmp/prmpt/exprss.yaml",
    "pmp/prmpt/hair.yaml",
    "pmp/prmpt/imgcmp.yaml",
    "pmp/prmpt/lctns.yaml",
    "pmp/prmpt/light.yaml",
    "pmp/prmpt/pose.yaml",
    "pmp/prmpt/styles.yaml",
    "vid/act.yaml",
)


def _sync_garage_wildcards():
    root = pathlib.Path(__file__).resolve().parent / "wildcards"
    updated = False
    for rel in _GARAGE_WILDCARDS:
        try:
            data = urllib.request.urlopen(f"{_GARAGE_WILDCARDS_URL}/{rel}", timeout=10).read()
            dest = root / rel
            if dest.exists() and dest.read_bytes() == data:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            updated = True
            print(f"[TagForge] wildcard updated from Garage: {rel}")
        except Exception as exc:
            print(f"[TagForge] wildcard sync skipped {rel}: {exc}")
    if updated:
        try:
            wildcard_processor.WildcardLoader.refresh()
        except Exception:
            pass


threading.Thread(target=_sync_garage_wildcards, daemon=True).start()

