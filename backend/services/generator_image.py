import os
import time
import random
import requests
import urllib.parse
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from core.config import settings

def generate_image_hf(prompt: str, output_path: str):
    """Using HuggingFace Inference API - FREE models only"""
    models = [
        "runwayml/stable-diffusion-v1-5",      # Reliable, usually free
        "stabilityai/stable-diffusion-2-1",    # Reliable
        "prompthero/openjourney",              # Styled
        "black-forest-labs/FLUX.1-schnell",    # Great but often gated/busy
    ]
    
    headers = {}
    if hasattr(settings, 'HF_TOKEN') and settings.HF_TOKEN:
        headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"}
    
    for model in models:
        try:
            # Revert to router as requested by API error message
            API_URL = f"https://router.huggingface.co/models/{model}"
            payload = {"inputs": prompt}
            
            print(f"Attempting HuggingFace ({model.split('/')[-1]})... url: {API_URL}")
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                # Check if we actually got an image
                if 'application/json' in response.headers.get('Content-Type', ''):
                    print(f"HF returned JSON instead of image: {response.text[:100]}")
                    continue

                img = Image.open(BytesIO(response.content))
                # Ensure correct size
                if img.size != (1080, 1920):
                    img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                img.save(output_path, quality=95)
                print(f"✓ HF Image saved: {output_path}")
                return output_path
            
            elif response.status_code == 503:
                # Model is loading
                estimated_time = 20
                try:
                    data = response.json()
                    estimated_time = data.get('estimated_time', 20)
                except:
                    pass
                
                print(f"Model loading, waiting {estimated_time}s...")
                time.sleep(estimated_time + 2) # Wait a bit extra
                
                # Retry once
                response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    if img.size != (1080, 1920):
                        img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                    img.save(output_path, quality=95)
                    print(f"✓ HF Image saved: {output_path}")
                    return output_path
                continue
            else:
                print(f"HF Error {response.status_code} for {model}: {response.text[:200]}")
                
        except Exception as e:
            print(f"HF {model} error: {e}")
            continue
    
    return None


def generate_image_hf_spaces(prompt: str, output_path: str):
    """Using HuggingFace Spaces - Fallback to standard HF if spaces fail"""
    # Just redirecting to the standard HF function as the "Spaces" direct URL was just a router anyway
    # and likely same/similar to Inference API.
    return generate_image_hf(prompt, output_path)


def generate_image_replicate(prompt: str, output_path: str):
    """Using Replicate API"""
    if not hasattr(settings, 'REPLICATE_API_TOKEN') or not settings.REPLICATE_API_TOKEN:
        return None
    
    try:
        import replicate
        
        print("Attempting Replicate (FLUX)...")
        # Using FLUX.1-schnell on Replicate (fast and good)
        output = replicate.run(
            "black-forest-labs/flux-schnell", 
            input={
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "9:16",
                "output_format": "jpg",
                "output_quality": 95
            }
        )
        
        # Download image
        img_url = output[0] if isinstance(output, list) else output
        
        img_response = requests.get(img_url, timeout=30)
        if img_response.status_code == 200:
            img = Image.open(BytesIO(img_response.content))
            img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
            img.save(output_path, quality=95)
            print(f"✓ Replicate image saved: {output_path}")
            return output_path
    except Exception as e:
        print(f"Replicate failed: {e}")
    return None


def generate_image_getimg(prompt: str, output_path: str):
    """Using GetImg.ai API (100 images/month free)"""
    if not hasattr(settings, 'GETIMG_API_KEY') or not settings.GETIMG_API_KEY:
        return None
    
    try:
        print("Attempting GetImg.ai API...")
        
        url = "https://api.getimg.ai/v1/stable-diffusion/text-to-image"
        headers = {
            "Authorization": f"Bearer {settings.GETIMG_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "width": 1080,
            "height": 1920,
            "model": "stable-diffusion-v1-5",
            "steps": 25,
            "guidance": 7.5
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            img_data = data.get('image')
            
            # Decode base64 image
            import base64
            img_bytes = base64.b64decode(img_data)
            
            with open(output_path, 'wb') as f:
                f.write(img_bytes)
            print(f"✓ GetImg image saved: {output_path}")
            return output_path
    except Exception as e:
        print(f"GetImg failed: {e}")
    return None


def generate_image_segmind(prompt: str, output_path: str):
    """Using Segmind API (Free tier available)"""
    if not hasattr(settings, 'SEGMIND_API_KEY') or not settings.SEGMIND_API_KEY:
        return None
    
    try:
        print("Attempting Segmind API...")
        
        url = "https://api.segmind.com/v1/sd1.5-txt2img"
        headers = {
            "x-api-key": settings.SEGMIND_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "negative_prompt": "low quality, blurry, distorted",
            "samples": 1,
            "scheduler": "UniPC",
            "num_inference_steps": 25,
            "guidance_scale": 8,
            "width": 1080,
            "height": 1920,
            "seed": random.randint(1, 1000000)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Segmind image saved: {output_path}")
            return output_path
    except Exception as e:
        print(f"Segmind failed: {e}")
    return None


def generate_image_deepai(prompt: str, output_path: str):
    """Using DeepAI API (Free with rate limits)"""
    if not hasattr(settings, 'DEEPAI_API_KEY') or not settings.DEEPAI_API_KEY:
        return None
    
    try:
        print("Attempting DeepAI API...")
        
        response = requests.post(
            "https://api.deepai.org/api/text2img",
            data={'text': prompt},
            headers={'api-key': settings.DEEPAI_API_KEY},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            img_url = data.get('output_url')
            
            # Download image
            img_response = requests.get(img_url, timeout=30)
            if img_response.status_code == 200:
                # Resize to desired dimensions
                img = Image.open(BytesIO(img_response.content))
                img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                img.save(output_path, quality=95)
                print(f"✓ DeepAI image saved: {output_path}")
                return output_path
    except Exception as e:
        print(f"DeepAI failed: {e}")
    return None


def generate_image_pollinations_smart(prompt: str, output_path: str):
    """Pollinations with aggressive rate limit handling"""
    clean_prompt = prompt.strip()[:800]
    encoded_prompt = urllib.parse.quote(clean_prompt)
    seed = random.randint(1, 10000000)
    
    models = ["flux", "flux-realism", "turbo"]
    
    for attempt in range(3):
        try:
            # Aggressive delays to avoid rate limits
            if attempt > 0:
                wait_time = 120 * (attempt + 1)  # 2min, 4min, 6min
                print(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                # Random initial delay
                initial_wait = random.uniform(5, 10)
                time.sleep(initial_wait)
            
            model_name = models[attempt % len(models)]
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&seed={seed}&enhance=true&model={model_name}"
            
            print(f"Attempt {attempt + 1}: Pollinations ({model_name})...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/*'
            }
            
            response = requests.get(image_url, headers=headers, timeout=45)
            
            if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                if os.path.getsize(output_path) > 1000:
                    print(f"✓ Pollinations image saved: {output_path}")
                    return output_path
            elif response.status_code == 429:
                print(f"Rate limited (429), will retry with longer delay")
                continue
            else:
                print(f"Status {response.status_code}")
                
        except Exception as e:
            print(f"Pollinations attempt {attempt + 1} error: {e}")
    
    return None


def generate_image_craiyon(prompt: str, output_path: str):
    """Using Craiyon (formerly DALL-E mini) - No API key needed"""
    try:
        print("Attempting Craiyon API...")
        
        # V3 endpoint with better parameters
        url = "https://api.craiyon.com/v3"
        payload = {
            "prompt": prompt,
            "model": "art",  # Changed from 'photo' to 'art' (more reliable)
            "negative_prompt": "low quality, blurry, distorted"
        }
        
        response = requests.post(url, json=payload, timeout=180)
        
        if response.status_code == 200:
            data = response.json()
            images = data.get('images', [])
            
            if images:
                # Get first image (base64 encoded)
                import base64
                img_data = base64.b64decode(images[0])
                
                img = Image.open(BytesIO(img_data))
                img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                img.save(output_path, quality=95)
                print(f"✓ Craiyon image saved: {output_path}")
                return output_path
        else:
            print(f"Craiyon error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"Craiyon failed: {e}")
    return None


def generate_image_prodia(prompt: str, output_path: str):
    """Using Prodia - Completely FREE, no API key needed"""
    try:
        print("Attempting Prodia API...")
        
        # Generate job
        url = "https://api.prodia.com/v1/job"
        payload = {
            "prompt": prompt,
            "model": "dreamshaper_8.safetensors",
            "negative_prompt": "bad quality, blurry, distorted",
            "steps": 20,
            "cfg_scale": 7,
            "seed": -1,
            "sampler": "DPM++ 2M Karras",
            "aspect_ratio": "portrait"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            job = response.json()
            job_id = job.get('job')
            
            # Wait for completion (max 60 seconds)
            for _ in range(30):
                time.sleep(2)
                status_url = f"https://api.prodia.com/v1/job/{job_id}"
                status_response = requests.get(status_url, timeout=10)
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    if status.get('status') == 'succeeded':
                        img_url = status.get('imageUrl')
                        
                        # Download image
                        img_response = requests.get(img_url, timeout=30)
                        if img_response.status_code == 200:
                            img = Image.open(BytesIO(img_response.content))
                            img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                            img.save(output_path, quality=95)
                            print(f"✓ Prodia image saved: {output_path}")
                            return output_path
                    elif status.get('status') == 'failed':
                        print("Prodia job failed")
                        break
        else:
            print(f"Prodia error {response.status_code}")
            
    except Exception as e:
        print(f"Prodia failed: {e}")
    return None


def generate_image_stablehorde(prompt: str, output_path: str):
    """Using Stable Horde - Free, community-powered"""
    try:
        print("Attempting Stable Horde API...")
        
        # Submit generation request
        url = "https://stablehorde.net/api/v2/generate/async"
        headers = {
            "Content-Type": "application/json",
            "apikey": "0000000000"  # Anonymous key
        }
        
        payload = {
            "prompt": prompt,
            "params": {
                "width": 512,  # Start smaller for faster generation
                "height": 768,
                "steps": 20,
                "cfg_scale": 7.5,
                "sampler_name": "k_euler"
            },
            "nsfw": False,
            "models": ["Deliberate"]
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 202:
            data = response.json()
            job_id = data.get('id')
            
            # Poll for completion (max 2 minutes)
            check_url = f"https://stablehorde.net/api/v2/generate/check/{job_id}"
            
            for _ in range(60):
                time.sleep(2)
                check_response = requests.get(check_url, timeout=10)
                
                if check_response.status_code == 200:
                    status = check_response.json()
                    if status.get('done'):
                        # Get the result
                        result_url = f"https://stablehorde.net/api/v2/generate/status/{job_id}"
                        result_response = requests.get(result_url, timeout=10)
                        
                        if result_response.status_code == 200:
                            result = result_response.json()
                            generations = result.get('generations', [])
                            
                            if generations:
                                img_url = generations[0].get('img')
                                
                                # Download image
                                img_response = requests.get(img_url, timeout=30)
                                if img_response.status_code == 200:
                                    img = Image.open(BytesIO(img_response.content))
                                    img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                                    img.save(output_path, quality=95)
                                    print(f"✓ Stable Horde image saved: {output_path}")
                                    return output_path
                        break
        else:
            print(f"Stable Horde error {response.status_code}")
            
    except Exception as e:
        print(f"Stable Horde failed: {e}")
    return None


def generate_image_dezgo(prompt: str, output_path: str):
    """Using DezGo - Free API, no key needed"""
    try:
        print("Attempting DezGo API...")
        
        url = "https://api.dezgo.com/text2image"
        
        payload = {
            "prompt": prompt,
            "model": "dreamshaper_8",  # Changed to a more reliable free model
            "width": 1080,
            "height": 1920,
            "guidance": 7.5,
            "steps": 25,
            "sampler": "k_euler"
        }
        
        response = requests.post(url, data=payload, timeout=90)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ DezGo image saved: {output_path}")
            return output_path
        else:
            print(f"DezGo error {response.status_code}")
            
    except Exception as e:
        print(f"DezGo failed: {e}")
    return None


def create_placeholder_image(prompt: str, output_path: str):
    """Creates an attractive placeholder image with gradient background"""
    try:
        img = Image.new('RGB', (1080, 1920), color=(20, 20, 40))
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for y in range(1920):
            r = int(20 + (y / 1920) * 60)
            g = int(20 + (y / 1920) * 40)
            b = int(40 + (y / 1920) * 80)
            draw.line([(0, y), (1080, y)], fill=(r, g, b))
        
        try:
            # Try to load standard fonts
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            
            if os.path.exists("C:/Windows/Fonts/arialbd.ttf"):
                font_large = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 60)
                font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
            elif os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            pass  # Use defaults
        
        text1 = "Image Generation"
        text2 = "Placeholder"
        
        bbox1 = draw.textbbox((0, 0), text1, font=font_large)
        bbox2 = draw.textbbox((0, 0), text2, font=font_large)
        
        x1 = (1080 - (bbox1[2] - bbox1[0])) // 2
        x2 = (1080 - (bbox2[2] - bbox2[0])) // 2
        
        draw.text((x1, 800), text1, fill=(255, 255, 255), font=font_large)
        draw.text((x2, 900), text2, fill=(200, 200, 255), font=font_large)
        
        prompt_preview = prompt[:60] + "..." if len(prompt) > 60 else prompt
        bbox3 = draw.textbbox((0, 0), prompt_preview, font=font_small)
        x3 = (1080 - (bbox3[2] - bbox3[0])) // 2
        draw.text((x3, 1050), prompt_preview, fill=(150, 150, 200), font=font_small)
        
        img.save(output_path, quality=95)
        print(f"✓ Placeholder created: {output_path}")
        return output_path
        
    except Exception as ex:
        print(f"Placeholder creation failed: {ex}")
        img = Image.new('RGB', (1080, 1920), color=(40, 40, 80))
        img.save(output_path)
        return output_path


def generate_image(prompt: str, output_path: str, retries: int = 4):
    """
    Generate an image from text prompt using multiple fallback methods.
    
    Priority order:
    1. HuggingFace (FLUX/SD 2.1) - Free with token
    2. HuggingFace Spaces - Free, no auth
    3. DezGo - Free, no auth
    4. Craiyon - Free, slower
    5. Replicate/GetImg/Segmind/DeepAI - If configured
    6. Pollinations - Free but rate limited
    7. Placeholder - Final fallback
    
    Args:
        prompt: Text description of image to generate
        output_path: Where to save the generated image
        retries: Number of retry attempts (deprecated, kept for compatibility)
    
    Returns:
        str: Path to generated image file
    """
    print(f"\n{'='*60}")
    print(f"Generating image: {prompt[:80]}...")
    print(f"{'='*60}")
    
    # Try APIs in priority order
    generators = [
        # Top tier: Free, reliable, good quality
        generate_image_hf,                    # FLUX.1-schnell, SD 2.1 (NEW ENDPOINT)
        generate_image_hf_spaces,             # FLUX via Spaces (NEW ENDPOINT)
        generate_image_prodia,                # Free, no key, reliable
        generate_image_stablehorde,           # Free, community-powered
        generate_image_dezgo,                 # Free, no key
        generate_image_craiyon,               # Free, slower but reliable
        
        # Paid/Limited APIs (if configured)
        generate_image_replicate,
        generate_image_getimg,
        generate_image_segmind,
        generate_image_deepai,
        
        # Last resort free option (rate limited)
        generate_image_pollinations_smart,
    ]
    
    for generator in generators:
        try:
            result = generator(prompt, output_path)
            if result:
                return result
        except Exception as e:
            print(f"{generator.__name__} failed: {e}")
            continue
    
    # Final fallback - placeholder
    print("\n⚠️  All generation methods failed. Creating placeholder...")
    return create_placeholder_image(prompt, output_path)


# Test function
if __name__ == "__main__":
    test_prompt = "A beautiful sunset over mountains, cinematic, high quality"
    output = "test_output.jpg"
    result = generate_image(test_prompt, output)
    print(f"\n✓ Final result: {result}")