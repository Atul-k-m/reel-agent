import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import time
import urllib.parse
import random

def generate_image(prompt: str, output_path: str, retries: int = 3):
    """
    Generates an image using the free Pollinations.ai API with improvements.
    Falls back to multiple APIs if one fails.
    """
    print(f"Generating image: {prompt}")
    
    # Try multiple times with different approaches
    for attempt in range(retries):
        try:
            # Clean and limit prompt length
            clean_prompt = prompt.strip()[:500]
            encoded_prompt = urllib.parse.quote(clean_prompt)
            
            # Use random seed for variety
            seed = random.randint(1, 1000000)
            
            # Pollinations API with correct parameters
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&seed={seed}&enhance=true"
            
            print(f"Attempt {attempt + 1}: Fetching from Pollinations.ai")
            
            # Set proper headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            # Longer timeout and follow redirects
            response = requests.get(image_url, headers=headers, timeout=60, allow_redirects=True)
            response.raise_for_status()
            
            # Check if we actually got image data
            content_type = response.headers.get('Content-Type', '')
            if 'image' not in content_type.lower() and len(response.content) < 1000:
                raise Exception(f"Invalid response: {content_type}, size: {len(response.content)}")
            
            # Try to open and verify image
            img = Image.open(BytesIO(response.content))
            
            # Verify image has reasonable dimensions
            if img.width < 100 or img.height < 100:
                raise Exception(f"Image too small: {img.width}x{img.height}")
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save with high quality
            img.save(output_path, quality=95)
            print(f"✓ Image saved successfully: {output_path}")
            return output_path
            
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            time.sleep(2)
            
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            time.sleep(2)
            
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            time.sleep(2)
    
    # All attempts failed - try alternative API
    print("Pollinations failed. Trying alternative API...")
    try:
        return generate_image_alternative(prompt, output_path)
    except Exception as e:
        print(f"Alternative API also failed: {e}")
    
    # Final fallback: Create a nice-looking placeholder
    print("Creating fallback placeholder image")
    return create_placeholder_image(prompt, output_path)


def generate_image_alternative(prompt: str, output_path: str):
    """
    Alternative image generation using a different free API.
    """
    try:
        # Picsum Photos for abstract/artistic images
        # or you could try other APIs like:
        # - https://api.deepai.org/api/text2img (requires free API key)
        # - https://huggingface.co/spaces (various models)
        
        # For now, using a different Pollinations endpoint
        encoded_prompt = urllib.parse.quote(prompt[:500])
        seed = random.randint(1, 1000000)
        
        # Alternative format without size constraints
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?seed={seed}"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, timeout=45)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        
        # Resize to desired dimensions
        img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(output_path, quality=95)
        print(f"✓ Alternative API succeeded: {output_path}")
        return output_path
        
    except Exception as e:
        raise Exception(f"Alternative generation failed: {e}")


def create_placeholder_image(prompt: str, output_path: str):
    """
    Creates an attractive placeholder image with gradient background.
    """
    try:
        # Create gradient background
        img = Image.new('RGB', (1080, 1920), color=(20, 20, 40))
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for y in range(1920):
            r = int(20 + (y / 1920) * 60)
            g = int(20 + (y / 1920) * 40)
            b = int(40 + (y / 1920) * 80)
            draw.line([(0, y), (1080, y)], fill=(r, g, b))
        
        # Add text
        try:
            # Try to use a nice font if available
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Main text
        text1 = "🎬 Image Generation"
        text2 = "Placeholder"
        
        # Center the text
        bbox1 = draw.textbbox((0, 0), text1, font=font_large)
        bbox2 = draw.textbbox((0, 0), text2, font=font_large)
        
        x1 = (1080 - (bbox1[2] - bbox1[0])) // 2
        x2 = (1080 - (bbox2[2] - bbox2[0])) // 2
        
        draw.text((x1, 800), text1, fill=(255, 255, 255), font=font_large)
        draw.text((x2, 900), text2, fill=(200, 200, 255), font=font_large)
        
        # Add prompt preview
        prompt_preview = prompt[:60] + "..." if len(prompt) > 60 else prompt
        bbox3 = draw.textbbox((0, 0), prompt_preview, font=font_small)
        x3 = (1080 - (bbox3[2] - bbox3[0])) // 2
        draw.text((x3, 1050), prompt_preview, fill=(150, 150, 200), font=font_small)
        
        img.save(output_path, quality=95)
        print(f"✓ Placeholder created: {output_path}")
        return output_path
        
    except Exception as ex:
        print(f"Placeholder creation failed: {ex}")
        # Absolute minimal fallback
        img = Image.new('RGB', (1080, 1920), color=(40, 40, 80))
        img.save(output_path)
        return output_path


# Test function
if __name__ == "__main__":
    test_prompt = "A beautiful sunset over mountains, cinematic, high quality"
    output = "test_output.jpg"
    generate_image(test_prompt, output)