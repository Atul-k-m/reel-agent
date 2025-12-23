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
    ):
        """
        SAFE Remotion renderer for Windows/Linux

        ✔ avoids command-line length limit
        ✔ never passes inline JSON
        ✔ uses HTTP-served audio
        """

        from core.config import settings

        scenes = scenes or []

        # ----------------------------
        # 1. Validate audio location
        # ----------------------------
        gen_dir = os.path.abspath(settings.GENERATED_DIR)
        audio_abs = os.path.abspath(audio_path)

        print("GEN DIR =", gen_dir)
        print("AUDIO   =", audio_abs)

        if not audio_abs.startswith(gen_dir):
            raise RuntimeError("Audio must be inside GENERATED_DIR")

        rel_path = audio_abs[len(gen_dir):].lstrip("\\/")
        port = os.environ.get("PORT", "8000")
        audio_url = (
            f"http://127.0.0.1:{port}/generated/"
            + rel_path.replace(os.sep, "/")
        )

        print("AUDIO URL =", audio_url)

        # ----------------------------
        # 2. Write props to JSON FILE
        # ----------------------------
        props = {
            "text": text,
            "audioSrc": audio_url,
            "scenes": scenes,
            "durationInFrames": duration_in_frames,  # 🔑 Required for calculateMetadata
        }

        props_path = os.path.join(
            os.path.dirname(output_path),
            "remotion_props.json",
        )

        with open(props_path, "w", encoding="utf-8") as f:
            json.dump(props, f, ensure_ascii=False)

        print("PROPS FILE =", props_path)
        print(f">>> DURATION_IN_FRAMES = {duration_in_frames} <<<")

        # ----------------------------
        # 3. Build command (SHORT!)
        # ----------------------------
        npx_cmd = "npx.cmd" if os.name == "nt" else "npx"

        cmd = [
            npx_cmd,
            "--yes",
            "remotion",
            "render",
            "src/remotion/index.ts",
            template_id,
            output_path,
            f"--props={props_path}",
            f"--duration-in-frames={duration_in_frames}",
            "--log=verbose",
        ]

        print("REMOTION CMD:")
        print(" ".join(cmd))
        print("CWD:", self.frontend_dir)

        # ----------------------------
        # 4. Execute
        # ----------------------------
        try:
            await asyncio.to_thread(
                subprocess.run,
                cmd,
                cwd=self.frontend_dir,
                check=True,
            )
            print("Render Success:", output_path)
            return output_path

        except subprocess.CalledProcessError as e:
            print("Render Failed:", e)
            return None
