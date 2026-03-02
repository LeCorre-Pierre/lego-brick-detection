"""
Command-line test for image download functionality.
Tests if BrickLink image downloads work properly.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from utils.image_downloader import ImageDownloader, BASE_URL


def run_direct_download(part_number: str, color_code: int = 3):
    """Test direct HTTP download without the downloader class."""
    url = f"{BASE_URL}/{color_code}/{part_number}.png"
    print(f"\n{'='*60}")
    print(f"Testing direct download: {part_number} (color {color_code})")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        # Try without User-Agent
        print("\n1. Trying without User-Agent...")
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✓ SUCCESS! Image size: {len(response.content)} bytes")
            return True
        elif response.status_code == 403:
            print(f"   ✗ FORBIDDEN (403) - Server rejected request")
        elif response.status_code == 404:
            print(f"   ✗ NOT FOUND (404) - Image doesn't exist")
        else:
            print(f"   ✗ ERROR {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Try with User-Agent header
    print("\n2. Trying WITH User-Agent header...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✓ SUCCESS! Image size: {len(response.content)} bytes")
            
            # Save test image
            test_file = Path("data/preview_images") / f"test_{part_number}.png"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            with open(test_file, 'wb') as f:
                f.write(response.content)
            print(f"   ✓ Saved to: {test_file}")
            return True
        elif response.status_code == 403:
            print(f"   ✗ FORBIDDEN (403) - Even with User-Agent")
        elif response.status_code == 404:
            print(f"   ✗ NOT FOUND (404) - Image doesn't exist for this color")
        else:
            print(f"   ✗ ERROR {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    return False


def run_color_fallback(part_number: str):
    """Test color fallback mechanism."""
    print(f"\n{'='*60}")
    print(f"Testing color fallback for: {part_number}")
    print(f"{'='*60}")
    
    colors_to_try = [3, 0, 1, 2, 4, 5, 6, 7, 8, 9]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for color in colors_to_try:
        url = f"{BASE_URL}/{color}/{part_number}.png"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"   ✓ Color {color}: SUCCESS ({len(response.content)} bytes)")
                return color
            elif response.status_code == 404:
                print(f"   ✗ Color {color}: Not found")
            else:
                print(f"   ✗ Color {color}: Status {response.status_code}")
        except Exception as e:
            print(f"   ✗ Color {color}: {e}")
        
        time.sleep(0.5)  # Small delay to avoid hammering the server
    
    print(f"   ✗ No valid color found for {part_number}")
    return None


def run_with_downloader(part_number: str):
    """Test using the ImageDownloader class."""
    print(f"\n{'='*60}")
    print(f"Testing with ImageDownloader class: {part_number}")
    print(f"{'='*60}")
    
    cache_dir = Path("data/preview_images")
    downloader = ImageDownloader(cache_dir=cache_dir)
    
    print(f"1. Requesting download...")
    status = downloader.request_image(part_number, priority=0)
    print(f"   Initial status: {status}")
    
    # Wait for download
    print(f"2. Waiting for download to complete (max 15 seconds)...")
    max_wait = 15
    start = time.time()
    
    while time.time() - start < max_wait:
        time.sleep(1)
        status = downloader.get_status(part_number)
        elapsed = time.time() - start
        print(f"   [{elapsed:.1f}s] Status: {status}")
        
        if status.name in ('CACHED', 'FAILED'):
            break
    
    # Check result
    final_status = downloader.get_status(part_number)
    image_path = downloader.get_image_path(part_number)
    
    print(f"\n3. Final result:")
    print(f"   Status: {final_status}")
    print(f"   Path: {image_path}")
    
    if image_path and image_path.exists():
        print(f"   ✓ Image file exists: {image_path.stat().st_size} bytes")
        success = True
    else:
        print(f"   ✗ Image file not found")
        success = False
    
    downloader.shutdown()
    return success


def main():
    """Run all tests."""
    print("="*60)
    print("LEGO BRICK IMAGE DOWNLOAD TEST")
    print("="*60)
    
    # Common brick part numbers to test
    test_parts = [
        "3001",  # 2x4 brick - very common
        "3003",  # 2x2 brick - very common
        "3005",  # 1x1 brick - very common
    ]
    
    results = []
    
    # Test 1: Direct downloads
    print("\n\nTEST 1: DIRECT HTTP DOWNLOADS")
    print("="*60)
    for part in test_parts:
        success = run_direct_download(part)
        results.append(("Direct download", part, success))
        time.sleep(1)  # Rate limiting
    
    # Test 2: Color fallback
    print("\n\nTEST 2: COLOR FALLBACK MECHANISM")
    print("="*60)
    color_found = run_color_fallback("3001")
    results.append(("Color fallback", "3001", color_found is not None))
    
    # Test 3: ImageDownloader class
    print("\n\nTEST 3: IMAGE DOWNLOADER CLASS")
    print("="*60)
    success = run_with_downloader("3001")
    results.append(("ImageDownloader", "3001", success))
    
    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, part, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {test_name} ({part})")
    
    total = len(results)
    passed = sum(1 for _, _, s in results if s)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == 0:
        print("\n⚠ WARNING: All downloads failed!")
        print("This suggests BrickLink may be blocking requests.")
        print("Possible solutions:")
        print("  1. Add proper User-Agent header (attempted in tests)")
        print("  2. Use a different image source")
        print("  3. Check if BrickLink API requires authentication")
    elif passed < total:
        print(f"\n⚠ WARNING: {total - passed} test(s) failed")
    else:
        print("\n✓ All tests passed! Download functionality is working.")


if __name__ == "__main__":
    main()
