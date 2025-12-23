import os
import json
import asyncio
import subprocess


class RemotionRenderer:
    def __init__(self, frontend_dir: str = "../frontend"):
        self.frontend_dir = os.path.abspath(frontend_dir)

    async def render_video(
        self,
        template_id: str,
        output_path: str,
        audio_path: str,
        text: str,
        duration_in_frames: int,
        scenes: list | None = None,
    ) -> str | dict:
        """
        PRODUCTION-READY Remotion renderer with comprehensive error handling.

        ✔ Captures stdout/stderr for debugging
        ✔ Returns detailed error info instead of None
        ✔ Timeout protection for low-CPU environments
        ✔ Full command output on failure
        
        Returns:
            str: Output path on success
            dict: {"error": "message"} on failure
        """

        from core.config import settings

        scenes = scenes or []
        
        print("\n" + "=" * 60)
        print("REMOTION RENDER START")
        print("=" * 60)

        # ----------------------------
        # 1. Validate audio location
        # ----------------------------
        gen_dir = os.path.abspath(settings.GENERATED_DIR)
        audio_abs = os.path.abspath(audio_path)

        print(f"[REMOTION] GEN DIR = {gen_dir}")
        print(f"[REMOTION] AUDIO   = {audio_abs}")

        if not audio_abs.startswith(gen_dir):
            error_msg = "Audio must be inside GENERATED_DIR"
            print(f"[REMOTION ERROR] {error_msg}")
            return {"error": error_msg}

        rel_path = audio_abs[len(gen_dir):].lstrip("\\/")
        port = os.environ.get("PORT", "8000")
        audio_url = (
            f"http://127.0.0.1:{port}/generated/"
            + rel_path.replace(os.sep, "/")
        )

        print(f"[REMOTION] AUDIO URL = {audio_url}")

        # ----------------------------
        # 2. Write props to JSON FILE
        # ----------------------------
        props = {
            "text": text,
            "audioSrc": audio_url,
            "scenes": scenes,
            "durationInFrames": duration_in_frames,
        }

        props_path = os.path.join(
            os.path.dirname(output_path),
            "remotion_props.json",
        )

        with open(props_path, "w", encoding="utf-8") as f:
            json.dump(props, f, ensure_ascii=False)

        print(f"[REMOTION] PROPS FILE = {props_path}")
        print(f"[REMOTION] DURATION_IN_FRAMES = {duration_in_frames}")

        # ----------------------------
        # 3. Build command
        # ----------------------------
        npx_cmd = "npx.cmd" if os.name == "nt" else "npx"

        # Use pre-built bundle if available (Docker/Production)
        bundle_path = os.path.join(self.frontend_dir, "dist-bundle")
        if os.path.exists(bundle_path) and os.path.isdir(bundle_path):
            print(f"[REMOTION] Using Pre-built Bundle: {bundle_path}")
            entry_point = "dist-bundle"
        else:
            print("[REMOTION] Using Source (Runtime Bundling)")
            entry_point = "src/remotion/index.ts"

        cmd = [
            npx_cmd,
            "--yes",
            "remotion",
            "render",
            entry_point,
            template_id,
            output_path,
            f"--props={props_path}",
            f"--duration-in-frames={duration_in_frames}",
            "--log=verbose",
        ]

        print("[REMOTION] Command:", " ".join(cmd))
        print(f"[REMOTION] CWD: {self.frontend_dir}")

        # ----------------------------
        # 4. Execute with timeout & capture
        # ----------------------------
        # Production timeout: 10 minutes max
        RENDER_TIMEOUT = int(os.environ.get("RENDER_TIMEOUT", "600"))
        
        print(f"[REMOTION] Starting render (timeout: {RENDER_TIMEOUT}s)...")

        try:
            # Run subprocess with output capture
            def run_subprocess():
                return subprocess.run(
                    cmd,
                    cwd=self.frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=RENDER_TIMEOUT,
                )

            result = await asyncio.wait_for(
                asyncio.to_thread(run_subprocess),
                timeout=RENDER_TIMEOUT + 30  # Extra buffer for asyncio
            )

            # Check return code
            if result.returncode == 0:
                print(f"[REMOTION] ✓ Render Success: {output_path}")
                # Log last 500 chars of stdout for debugging
                if result.stdout:
                    print(f"[REMOTION] STDOUT (last 500):\n{result.stdout[-500:]}")
                return output_path
            else:
                # Non-zero return code - capture the error
                error_details = result.stderr or result.stdout or "No output captured"
                # Truncate for logging but keep enough for diagnosis
                error_truncated = error_details[:1000] if len(error_details) > 1000 else error_details
                
                error_msg = f"Remotion exited with code {result.returncode}"
                print(f"[REMOTION ERROR] {error_msg}")
                print(f"[REMOTION STDERR]:\n{error_truncated}")
                
                return {"error": f"{error_msg}: {error_truncated}"}

        except subprocess.TimeoutExpired as e:
            error_msg = f"Render timeout after {RENDER_TIMEOUT}s (low CPU environment?)"
            print(f"[REMOTION ERROR] {error_msg}")
            # Try to capture any partial output
            if hasattr(e, 'stdout') and e.stdout:
                print(f"[REMOTION PARTIAL STDOUT]: {e.stdout[:500]}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"[REMOTION PARTIAL STDERR]: {e.stderr[:500]}")
            return {"error": error_msg}

        except asyncio.TimeoutError:
            error_msg = f"Async timeout after {RENDER_TIMEOUT + 30}s - render hung"
            print(f"[REMOTION ERROR] {error_msg}")
            return {"error": error_msg}

        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
            print(f"[REMOTION ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            return {"error": error_msg}
        
        finally:
            print("=" * 60)
            print("REMOTION RENDER END")
            print("=" * 60 + "\n")
